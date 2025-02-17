from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app and database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notifications.db'  # Using SQLite for simplicity
db = SQLAlchemy(app)

# ---------------------------- Notification Model ---------------------------- #
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who will receive the notification
    message = db.Column(db.String(255), nullable=False)  # Notification message (e.g., "You have a new like!")
    is_read = db.Column(db.Boolean, default=False)  # Whether the notification has been read by the user
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of when the notification was created

    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'

# ---------------------------- Send Notification ---------------------------- #
def send_notification(user_id, message):
    """Helper function to create and send a notification."""
    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)
    db.session.commit()

# ---------------------------- Get Notifications ---------------------------- #
@app.route('/notifications')
def get_notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get notifications for the current user
    notifications = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.timestamp.desc()).all()

    return render_template('notifications.html', notifications=notifications)

# ---------------------------- Mark Notifications as Read ---------------------------- #
@app.route('/mark_read/<int:notification_id>', methods=['POST'])
def mark_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    # Mark the notification as read
    notification.is_read = True
    db.session.commit()

    flash("Notification marked as read.", "success")
    return redirect(url_for('get_notifications'))

# ---------------------------- Delete Notification ---------------------------- #
@app.route('/delete_notification/<int:notification_id>', methods=['POST'])
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    # Delete the notification
    db.session.delete(notification)
    db.session.commit()

    flash("Notification deleted.", "success")
    return redirect(url_for('get_notifications'))

# ---------------------------- New Like Notification ---------------------------- #
@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)
    # Assuming `post.user_id` is the user who owns the post
    send_notification(post.user_id, f"Your post has been liked by User {session['user_id']}.")

    # Proceed with the like functionality (store the like in the database)
    like = Like(post_id=post_id, user_id=session['user_id'])
    db.session.add(like)
    db.session.commit()

    flash("You liked the post!", "success")
    return redirect(url_for('feed'))

# ---------------------------- New Comment Notification ---------------------------- #
@app.route('/comment_post/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)
    content = request.form['comment']

    # Send notification to the post owner
    send_notification(post.user_id, f"User {session['user_id']} commented on your post.")

    # Store the comment in the database
    comment = Comment(post_id=post_id, user_id=session['user_id'], content=content)
    db.session.add(comment)
    db.session.commit()

    flash("Comment posted!", "success")
    return redirect(url_for('feed'))

# ---------------------------- New Follower Notification ---------------------------- #
@app.route('/follow_user/<int:user_id>', methods=['POST'])
def follow_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Follow the user
    new_follow = Follow(follower_id=session['user_id'], followed_id=user_id)
    db.session.add(new_follow)
    db.session.commit()

    # Send notification to the user being followed
    send_notification(user_id, f"User {session['user_id']} started following you.")

    flash(f"You started following User {user_id}!", "success")
    return redirect(url_for('profile', user_id=user_id))

# ---------------------------- Helper Function to Get Unread Notifications ---------------------------- #
def get_unread_notifications(user_id):
    """Return unread notifications for the user."""
    return Notification.query.filter_by(user_id=user_id, is_read=False).all()

# ---------------------------- Run Application ---------------------------- #
if __name__ == '__main__':
    app.run(debug=True)
