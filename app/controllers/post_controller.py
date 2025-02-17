from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import Post, Comment, Like, User  # Assuming Post, Comment, Like models are defined in post.py
from database import db  # Assuming database.py handles the DB session
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'app/static/images/post_images'

# ---------------------- Create Post Route ---------------------- #
@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    """Route for creating a new post."""
    if request.method == 'POST':
        caption = request.form['caption']
        media_file = request.files.get('media')  # File input for media (image/video)

        if not media_file:
            flash("Please upload an image or video.", 'danger')
            return redirect(url_for('create_post'))

        # Save the file to the specified folder
        media_filename = os.path.join(app.config['UPLOAD_FOLDER'], media_file.filename)
        media_file.save(media_filename)

        # Create a new post entry in the database
        new_post = Post(caption=caption, media_url=media_filename, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()

        flash("Post created successfully!", 'success')
        return redirect(url_for('feed'))

    return render_template('create_post.html')

# ---------------------- Feed Route ---------------------- #
@app.route('/feed')
@login_required
def feed():
    """Route to display all posts in the user's feed."""
    posts = Post.query.order_by(Post.created_at.desc()).all()  # Get all posts in descending order
    return render_template('feed.html', posts=posts)

# ---------------------- View Post Route ---------------------- #
@app.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    """Route to view a single post and interact with it."""
    post = Post.query.get(post_id)
    if not post:
        flash("Post not found.", 'danger')
        return redirect(url_for('feed'))

    # Get comments and likes for the post
    comments = Comment.query.filter_by(post_id=post.id).all()
    is_liked = Like.query.filter_by(post_id=post.id, user_id=current_user.id).first() is not None

    return render_template('view_post.html', post=post, comments=comments, is_liked=is_liked)

# ---------------------- Like Post Route ---------------------- #
@app.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    """Route to like or unlike a post."""
    post = Post.query.get(post_id)
    if not post:
        flash("Post not found.", 'danger')
        return redirect(url_for('feed'))

    # Check if the user already liked the post
    existing_like = Like.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        flash("Post unliked.", 'success')
    else:
        new_like = Like(post_id=post_id, user_id=current_user.id)
        db.session.add(new_like)
        db.session.commit()
        flash("Post liked.", 'success')

    return redirect(url_for('view_post', post_id=post_id))

# ---------------------- Comment on Post Route ---------------------- #
@app.route('/comment_post/<int:post_id>', methods=['POST'])
@login_required
def comment_post(post_id):
    """Route to comment on a post."""
    post = Post.query.get(post_id)
    if not post:
        flash("Post not found.", 'danger')
        return redirect(url_for('feed'))

    comment_text = request.form['comment']
    if not comment_text:
        flash("Please enter a comment.", 'danger')
        return redirect(url_for('view_post', post_id=post_id))

    # Create a new comment and add it to the database
    new_comment = Comment(post_id=post_id, user_id=current_user.id, text=comment_text)
    db.session.add(new_comment)
    db.session.commit()

    flash("Comment added successfully!", 'success')
    return redirect(url_for('view_post', post_id=post_id))

# ---------------------- Edit Post Route ---------------------- #
@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Route to edit an existing post."""
    post = Post.query.get(post_id)
    if not post or post.user_id != current_user.id:
        flash("Post not found or you are not authorized.", 'danger')
        return redirect(url_for('feed'))

    if request.method == 'POST':
        caption = request.form['caption']
        media_file = request.files.get('media')  # File input for media (image/video)

        # If media is uploaded, save it and update the post
        if media_file:
            media_filename = os.path.join(app.config['UPLOAD_FOLDER'], media_file.filename)
            media_file.save(media_filename)
            post.media_url = media_filename

        post.caption = caption
        db.session.commit()

        flash("Post updated successfully!", 'success')
        return redirect(url_for('view_post', post_id=post_id))

    return render_template('edit_post.html', post=post)

# ---------------------- Delete Post Route ---------------------- #
@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    """Route to delete a post."""
    post = Post.query.get(post_id)
    if not post or post.user_id != current_user.id:
        flash("Post not found or you are not authorized.", 'danger')
        return redirect(url_for('feed'))

    # Delete the post and associated likes and comments
    db.session.delete(post)
    db.session.commit()

    flash("Post deleted successfully.", 'success')
    return redirect(url_for('feed'))

# ---------------------- Helper Function for File Management ---------------------- #
def allowed_file(filename):
    """Helper function to check if the uploaded file is an allowed media type."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------- Run Application ---------------------- #
if __name__ == '__main__':
    app.run(debug=True)
