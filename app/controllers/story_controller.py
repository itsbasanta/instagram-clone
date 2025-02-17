from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import Story, User  # Assuming Story model is defined in story.py
from database import db  # Assuming database.py handles the DB session
import os
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'app/static/images/stories'

# ---------------------- Create Story Route ---------------------- #
@app.route('/create_story', methods=['GET', 'POST'])
@login_required
def create_story():
    """Route for creating a new story."""
    if request.method == 'POST':
        story_text = request.form['story_text']
        media_file = request.files.get('media')  # File input for story media (image/video)

        if not media_file:
            flash("Please upload an image or video for your story.", 'danger')
            return redirect(url_for('create_story'))

        # Save the file to the specified folder
        media_filename = os.path.join(app.config['UPLOAD_FOLDER'], media_file.filename)
        media_file.save(media_filename)

        # Create a new story entry in the database with an expiration time of 24 hours
        expiration_time = datetime.utcnow() + timedelta(days=1)
        new_story = Story(user_id=current_user.id, text=story_text, media_url=media_filename, expiration_time=expiration_time)
        db.session.add(new_story)
        db.session.commit()

        flash("Story created successfully!", 'success')
        return redirect(url_for('view_stories'))

    return render_template('create_story.html')

# ---------------------- View Stories Route ---------------------- #
@app.route('/stories')
@login_required
def view_stories():
    """Route to display all active stories."""
    # Fetch all active stories (those that haven't expired yet)
    current_time = datetime.utcnow()
    stories = Story.query.filter(Story.expiration_time > current_time).order_by(Story.created_at.desc()).all()

    # Check if there are no active stories
    if not stories:
        flash("No active stories right now.", 'info')

    return render_template('view_stories.html', stories=stories)

# ---------------------- Edit Story Route ---------------------- #
@app.route('/edit_story/<int:story_id>', methods=['GET', 'POST'])
@login_required
def edit_story(story_id):
    """Route to edit an existing story."""
    story = Story.query.get(story_id)
    if not story or story.user_id != current_user.id:
        flash("Story not found or you are not authorized.", 'danger')
        return redirect(url_for('view_stories'))

    if request.method == 'POST':
        story_text = request.form['story_text']
        media_file = request.files.get('media')  # File input for story media (image/video)

        # If media is uploaded, save it and update the story
        if media_file:
            media_filename = os.path.join(app.config['UPLOAD_FOLDER'], media_file.filename)
            media_file.save(media_filename)
            story.media_url = media_filename

        story.text = story_text
        db.session.commit()

        flash("Story updated successfully!", 'success')
        return redirect(url_for('view_stories'))

    return render_template('edit_story.html', story=story)

# ---------------------- Delete Story Route ---------------------- #
@app.route('/delete_story/<int:story_id>', methods=['POST'])
@login_required
def delete_story(story_id):
    """Route to delete a story."""
    story = Story.query.get(story_id)
    if not story or story.user_id != current_user.id:
        flash("Story not found or you are not authorized.", 'danger')
        return redirect(url_for('view_stories'))

    # Delete the story
    db.session.delete(story)
    db.session.commit()

    flash("Story deleted successfully.", 'success')
    return redirect(url_for('view_stories'))

# ---------------------- Story Expiration Cleanup ---------------------- #
def cleanup_expired_stories():
    """Helper function to clean up expired stories."""
    current_time = datetime.utcnow()
    expired_stories = Story.query.filter(Story.expiration_time < current_time).all()

    for story in expired_stories:
        db.session.delete(story)

    db.session.commit()

# ---------------------- Helper Function for File Management ---------------------- #
def allowed_file(filename):
    """Helper function to check if the uploaded file is an allowed media type."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------- Run Application ---------------------- #
if __name__ == '__main__':
    app.run(debug=True)
