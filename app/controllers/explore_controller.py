from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Post, Hashtag, User  # Assuming the Post and Hashtag models are defined in post.py and hashtag.py
from database import db  # Assuming database.py handles the DB session
from sqlalchemy import func

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# ---------------------- Explore Page Route ---------------------- #
@app.route('/explore', methods=['GET'])
@login_required
def explore():
    """Route to display the explore page, featuring trending posts, hashtags, and recommended content."""
    
    # Fetch trending posts - Sorted by the number of likes and comments
    trending_posts = Post.query.outerjoin(Post.likes).outerjoin(Post.comments).group_by(Post.id).order_by(
        func.count(Post.likes).desc(), func.count(Post.comments).desc()).limit(20).all()

    # Fetch trending hashtags - Sorted by usage frequency
    trending_hashtags = Hashtag.query.join(Post).group_by(Hashtag.id).order_by(func.count(Post.id).desc()).limit(10).all()

    # Personalized recommendations - Posts liked by people you follow
    following_posts = db.session.query(Post).join(User.following).filter(User.id == current_user.id).all()

    # Discover posts from hashtags (optional)
    hashtag = request.args.get('hashtag')
    if hashtag:
        posts_by_hashtag = Post.query.join(Post.hashtags).filter(Hashtag.name == hashtag).all()
    else:
        posts_by_hashtag = []

    return render_template(
        'explore.html',
        trending_posts=trending_posts,
        trending_hashtags=trending_hashtags,
        following_posts=following_posts,
        posts_by_hashtag=posts_by_hashtag,
        hashtag=hashtag
    )

# ---------------------- Search Hashtags ---------------------- #
@app.route('/search_hashtags', methods=['GET'])
@login_required
def search_hashtags():
    """Route to search for posts by hashtags."""
    
    hashtag_query = request.args.get('q', '').strip()

    if hashtag_query:
        hashtags = Hashtag.query.filter(Hashtag.name.ilike(f'%{hashtag_query}%')).all()
    else:
        hashtags = []

    return render_template('search_hashtags.html', hashtags=hashtags, hashtag_query=hashtag_query)

# ---------------------- Explore Trending Posts ---------------------- #
@app.route('/trending', methods=['GET'])
@login_required
def trending():
    """Route to view the most popular or trending posts globally."""
    
    # Get posts with the most engagement (likes/comments)
    trending_posts = Post.query.outerjoin(Post.likes).outerjoin(Post.comments).group_by(Post.id).order_by(
        func.count(Post.likes).desc(), func.count(Post.comments).desc()).limit(10).all()

    return render_template('trending_posts.html', trending_posts=trending_posts)

# ---------------------- Follow Recommendations ---------------------- #
@app.route('/follow_recommendations', methods=['GET'])
@login_required
def follow_recommendations():
    """Route to show user follow recommendations based on interests."""
    
    # Recommend users to follow based on similar interests or mutual friends
    recommended_users = User.query.filter(User.id != current_user.id).limit(10).all()  # Example logic

    return render_template('follow_recommendations.html', recommended_users=recommended_users)

# ---------------------- Like a Post ---------------------- #
@app.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    """Route to like a post."""
    
    post = Post.query.get(post_id)
    if not post:
        flash("Post not found.", 'danger')
        return redirect(url_for('explore'))

    if post not in current_user.liked_posts:
        current_user.liked_posts.append(post)
        db.session.commit()
        flash("Post liked!", 'success')
    else:
        flash("You already liked this post.", 'warning')

    return redirect(url_for('explore'))

# ---------------------- Save Post ---------------------- #
@app.route('/save_post/<int:post_id>', methods=['POST'])
@login_required
def save_post(post_id):
    """Route to save a post for later viewing."""
    
    post = Post.query.get(post_id)
    if not post:
        flash("Post not found.", 'danger')
        return redirect(url_for('explore'))

    if post not in current_user.saved_posts:
        current_user.saved_posts.append(post)
        db.session.commit()
        flash("Post saved!", 'success')
    else:
        flash("This post is already saved.", 'warning')

    return redirect(url_for('explore'))

# ---------------------- Discover Posts by Hashtags ---------------------- #
@app.route('/hashtag/<string:hashtag_name>', methods=['GET'])
@login_required
def discover_by_hashtag(hashtag_name):
    """Route to view posts associated with a specific hashtag."""
    
    hashtag = Hashtag.query.filter_by(name=hashtag_name).first()
    if not hashtag:
        flash(f"Hashtag #{hashtag_name} not found.", 'danger')
        return redirect(url_for('explore'))

    posts_with_hashtag = Post.query.join(Post.hashtags).filter(Hashtag.name == hashtag_name).all()

    return render_template('hashtag_posts.html', posts=posts_with_hashtag, hashtag=hashtag_name)

# ---------------------- Run the Application ---------------------- #
if __name__ == '__main__':
    app.run(debug=True)
