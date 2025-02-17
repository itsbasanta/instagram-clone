from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app and database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hashtag.db'  # Using SQLite for simplicity
db = SQLAlchemy(app)

# ---------------------------- Hashtag Model ---------------------------- #
class Hashtag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hashtag = db.Column(db.String(100), unique=True, nullable=False)  # Hashtag text (e.g., #travel)
    posts = db.relationship('Post', secondary='post_hashtags', back_populates='hashtags')

    def __repr__(self):
        return f'<Hashtag #{self.hashtag}>'

# ---------------------------- Post-Hashtag Relationship ---------------------------- #
class PostHashtag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    hashtag_id = db.Column(db.Integer, db.ForeignKey('hashtag.id', ondelete='CASCADE'), nullable=False)

    post = db.relationship('Post', back_populates='post_hashtags')
    hashtag = db.relationship('Hashtag', back_populates='post_hashtags')

# ---------------------------- Add Hashtags to Post ---------------------------- #
def add_hashtags_to_post(post_id, hashtags):
    """Helper function to associate hashtags with a post."""
    for hashtag in hashtags:
        # Check if the hashtag already exists
        existing_hashtag = Hashtag.query.filter_by(hashtag=hashtag).first()
        if existing_hashtag:
            # If it exists, add it to the post
            post_hashtag = PostHashtag(post_id=post_id, hashtag_id=existing_hashtag.id)
        else:
            # If not, create a new hashtag and associate it with the post
            new_hashtag = Hashtag(hashtag=hashtag)
            db.session.add(new_hashtag)
            db.session.commit()  # Commit to get the new hashtag's ID
            post_hashtag = PostHashtag(post_id=post_id, hashtag_id=new_hashtag.id)

        # Add the post-hashtag relationship
        db.session.add(post_hashtag)
    db.session.commit()

# ---------------------------- Get Posts by Hashtag ---------------------------- #
@app.route('/hashtag/<string:hashtag>')
def get_posts_by_hashtag(hashtag):
    """Route to display posts by hashtag."""
    hashtag_obj = Hashtag.query.filter_by(hashtag=hashtag).first()

    if not hashtag_obj:
        flash("Hashtag not found.", "danger")
        return redirect(url_for('index'))

    # Get all posts associated with the hashtag
    posts = [post_hashtag.post for post_hashtag in hashtag_obj.post_hashtags]

    return render_template('hashtag_posts.html', hashtag=hashtag, posts=posts)

# ---------------------------- Search Hashtags ---------------------------- #
@app.route('/search', methods=['POST'])
def search_hashtags():
    """Search for hashtags and display related posts."""
    query = request.form['query']
    hashtags = Hashtag.query.filter(Hashtag.hashtag.ilike(f'%{query}%')).all()

    if not hashtags:
        flash("No hashtags found.", "danger")
        return redirect(url_for('index'))

    return render_template('search_results.html', hashtags=hashtags)

# ---------------------------- Display Trending Hashtags ---------------------------- #
@app.route('/trending')
def trending_hashtags():
    """Route to display trending hashtags based on the number of posts associated with them."""
    hashtags = db.session.query(Hashtag, db.func.count(PostHashtag.id).label('count')) \
                         .join(PostHashtag, Hashtag.id == PostHashtag.hashtag_id) \
                         .group_by(Hashtag.id) \
                         .order_by(db.desc('count')).limit(10).all()

    return render_template('trending_hashtags.html', hashtags=hashtags)

# ---------------------------- Helper Function to Extract Hashtags from Post ---------------------------- #
def extract_hashtags_from_text(text):
    """Helper function to extract hashtags from a given text."""
    # Extract words that start with '#' and return them as a list
    return [word[1:] for word in text.split() if word.startswith('#')]

# ---------------------------- Run Application ---------------------------- #
if __name__ == '__main__':
    app.run(debug=True)
