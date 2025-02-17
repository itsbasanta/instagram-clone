from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize Flask app and database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reels.db'
app.config['UPLOAD_FOLDER'] = 'app/static/videos'  # Folder to store uploaded videos
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'mkv'}
db = SQLAlchemy(app)

# ---------------------------- Reel Model ---------------------------- #
class Reel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_file = db.Column(db.String(120), nullable=False)  # Video file name
    caption = db.Column(db.String(255), nullable=True)  # Optional caption for the reel
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.relationship('Like', backref='reel', lazy=True)
    comments = db.relationship('Comment', backref='reel', lazy=True)

    def __repr__(self):
        return f'<Reel {self.id} by {self.user_id}>'

# ---------------------------- Like Model ---------------------------- #
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reel_id = db.Column(db.Integer, db.ForeignKey('reel.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Like {self.id}>'

# ---------------------------- Comment Model ---------------------------- #
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reel_id = db.Column(db.Integer, db.ForeignKey('reel.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Comment {self.id} on Reel {self.reel_id}>'

# ---------------------------- Upload Reel ---------------------------- #
@app.route('/upload_reel', methods=['GET', 'POST'])
def upload_reel():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        video_file = request.files['video']
        caption = request.form['caption']

        if video_file and allowed_file(video_file.filename):
            # Save the video file to the designated folder
            video_filename = os.path.join(app.config['UPLOAD_FOLDER'], video_file.filename)
            video_file.save(video_filename)

            # Create new reel entry in the database
            reel = Reel(user_id=session['user_id'], video_file=video_file.filename, caption=caption)
            db.session.add(reel)
            db.session.commit()
            flash("Reel uploaded successfully!", "success")
            return redirect(url_for('view_reels'))

        flash("Invalid file type. Only video files are allowed.", "danger")

    return render_template('upload_reel.html')

# ---------------------------- View Reels ---------------------------- #
@app.route('/reels')
def view_reels():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    reels = Reel.query.all()
    return render_template('view_reels.html', reels=reels)

# ---------------------------- Like Reel ---------------------------- #
@app.route('/like_reel/<int:reel_id>', methods=['POST'])
def like_reel(reel_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    reel = Reel.query.get_or_404(reel_id)

    # Check if the user has already liked the reel
    existing_like = Like.query.filter_by(reel_id=reel.id, user_id=session['user_id']).first()

    if existing_like:
        flash("You already liked this reel.", "info")
    else:
        like = Like(reel_id=reel.id, user_id=session['user_id'])
        db.session.add(like)
        db.session.commit()
        flash("You liked this reel!", "success")

    return redirect(url_for('view_reels'))

# ---------------------------- Comment on Reel ---------------------------- #
@app.route('/comment_reel/<int:reel_id>', methods=['POST'])
def comment_reel(reel_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    reel = Reel.query.get_or_404(reel_id)
    content = request.form['comment']

    if content.strip():
        comment = Comment(reel_id=reel.id, user_id=session['user_id'], content=content)
        db.session.add(comment)
        db.session.commit()
        flash("Comment added successfully!", "success")
    else:
        flash("Comment cannot be empty.", "danger")

    return redirect(url_for('view_reels'))

# ---------------------------- Helper Function to Check File Type ---------------------------- #
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ---------------------------- Run Application ---------------------------- #
if __name__ == '__main__':
    app.run(debug=True)
