import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app and database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stories.db'
app.config['UPLOAD_FOLDER'] = 'static/story_media'
db = SQLAlchemy(app)

# ---------------------------- Story Model ---------------------------- #
class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(120), nullable=True)
    video = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='stories')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Story {self.id}>'

# ---------------------------- Create Story ---------------------------- #
@app.route('/create_story', methods=['GET', 'POST'])
def create_story():
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

        story = Story(content=content, image=image_filename, video=video_filename, user_id=session['user_id'])
        db.session.add(story)
        db.session.commit()
        flash("Story posted successfully!", "success")
        return redirect(url_for('profile'))

    return render_template('create_story.html')

# ---------------------------- View Stories ---------------------------- #
@app.route('/view_stories')
def view_stories():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get the stories of the current user that are less than 24 hours old
    current_time = datetime.utcnow()
    stories = Story.query.filter(Story.timestamp >= current_time - timedelta(days=1)).all()

    return render_template('view_stories.html', stories=stories)

# ---------------------------- Delete Story ---------------------------- #
@app.route('/delete_story/<int:story_id>', methods=['POST'])
def delete_story(story_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    story = Story.query.get_or_404(story_id)

    # Ensure the story belongs to the current user
    if story.user_id != session['user_id']:
        flash("You can only delete your own stories.", "danger")
        return redirect(url_for('view_stories'))

    # Delete the story's media from the filesystem (optional)
    if story.image:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], story.image))
    if story.video:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], story.video))

    # Delete the story from the database
    db.session.delete(story)
    db.session.commit()

    flash("Story deleted successfully!", "success")
    return redirect(url_for('view_stories'))

# ---------------------------- Story Expiration ---------------------------- #
@app.route('/expired_stories')
def expired_stories():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get stories that are older than 24 hours (expired stories)
    current_time = datetime.utcnow()
    expired_stories = Story.query.filter(Story.timestamp <= current_time - timedelta(days=1)).all()

    return render_template('expired_stories.html', stories=expired_stories)

# ---------------------------- Run Application ---------------------------- #
if __name__ == '__main__':
    app.run(debug=True)
