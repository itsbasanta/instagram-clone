import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app and database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['UPLOAD_FOLDER'] = 'static/post_media'
db = SQLAlchemy(app)

# ---------------------------- Post Model ---------------------------- #
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(120), nullable=True)
    video = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='posts')
    likes = db.relationship('Like', backref='post', lazy=True)
    comments = db.relationship('Comment', backref='post', lazy=True)
    tags = db.relationship('Tag', backref='post', lazy=True)

    def __repr__(self):
        return f'<Post {self.id}>'

# ---------------------------- Like Model ---------------------------- #
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Like {self.id}>'

# ---------------------------- Comment Model ---------------------------- #
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(250), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='comments')

    def __repr__(self):
        return f'<Comment {self.id}>'

# ---------------------------- Tag Model ---------------------------- #
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f'<Tag {self.name}>'

# ---------------------------- Create Post ---------------------------- #
@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        content = request.form['content']
        image = request.files.get('image')
        video = request.files.get('video')

        # Save media files
        image_filename = None
        video_filename = None
        if image:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        if video:
            video_filename = secure_filename(video.filename)
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], video_filename))

        post = Post(content=content, image=image_filename, video=video_filename, user_id=session['user_id'])
        db.session.add(post)
        db.session.commit()
        flash("Post created successfully!", "success")
        return redirect(url_for('feed'))

    return render_template('create_post.html')

# ---------------------------- Like Post ---------------------------- #
@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)
    user = User.query.get(session['user_id'])

    # Check if the user has already liked the post
    if Like.query.filter_by(post_id=post.id, user_id=user.id).first() is None:
        like = Like(post_id=post.id, user_id=user.id)
        db.session.add(like)
        db.session.commit()
        flash("You liked this post!", "success")
    else:
        flash("You already liked this post.", "info")

    return redirect(url_for('feed'))

# ---------------------------- Comment on Post ---------------------------- #
@app.route('/comment_post/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)
    content = request.form['content']
    user = User.query.get(session['user_id'])

    comment = Comment(content=content, post_id=post.id, user_id=user.id)
    db.session.add(comment)
    db.session.commit()
    flash("Your comment was posted!", "success")

    return redirect(url_for('feed'))

# ---------------------------- Tag Post ---------------------------- #
@app.route('/tag_post/<int:post_id>', methods=['POST'])
def tag_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)
    tags = request.form['tags'].split(',')

    for tag_name in tags:
        tag_name = tag_name.strip()
        if tag_name:
            tag = Tag(name=tag_name, post_id=post.id)
            db.session.add(tag)

    db.session.commit()
    flash("Tags added to the post!", "success")

    return redirect(url_for('feed'))

# ---------------------------- Save Post ---------------------------- #
@app.route('/save_post/<int:post_id>', methods=['POST'])
def save_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)
    user = User.query.get(session['user_id'])

    # Logic for saving posts (You could implement a SavedPost model)
    # Flash a success message
    flash("Post saved to your collection!", "success")

    return redirect(url_for('feed'))

# ---------------------------- Feed ---------------------------- #
@app.route('/feed')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    posts = Post.query.all()
    return render_template('feed.html', posts=posts)

# ---------------------------- Run Application ---------------------------- #
if __name__ == '__main__':
    app.run(debug=True)
