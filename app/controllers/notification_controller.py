from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Notification, User
from database import db  # Assuming database.py handles the DB session

# ---------------------- Notification Center Route ---------------------- #
@app.route('/notifications')
@login_required
def notifications():
    """Route to display all notifications for the logged-in user."""
    
    # Fetch notifications for the user
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    
    # Mark notifications as read (optional: only unread notifications)
    for notification in notifications:
        if not notification.read:
            notification.read = True
    db.session.commit()

    return render_template('notifications.html', notifications=notifications)

# ---------------------- Notification Settings Route ---------------------- #
@app.route('/settings/notifications', methods=['GET', 'POST'])
@login_required
def notification_settings():
    """Route to update user's notification preferences."""
    
    if request.method == 'POST':
        # Get notification preferences from the form
        likes_notifications = request.form.get('likes_notifications') == 'on'
        comments_notifications = request.form.get('comments_notifications') == 'on'
        follows_notifications = request.form.get('follows_notifications') == 'on'
        messages_notifications = request.form.get('messages_notifications') == 'on'

        # Update the notification preferences in the database
        current_user.likes_notifications = likes_notifications
        current_user.comments_notifications = comments_notifications
        current_user.follows_notifications = follows_notifications
        current_user.messages_notifications = messages_notifications
        db.session.commit()

        flash('Your notification preferences have been updated!', 'success')
        return redirect(url_for('notifications'))

    return render_template('notification_settings.html', user=current_user)

# ---------------------- Mark Notification as Read ---------------------- #
@app.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_as_read(notification_id):
    """Route to mark a notification as read."""
    
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == current_user.id:
        notification.read = True
        db.session.commit()
        flash('Notification marked as read.', 'success')
    else:
        flash('You cannot mark this notification as read.', 'danger')
    
    return redirect(url_for('notifications'))

# ---------------------- Delete Notification ---------------------- #
@app.route('/notifications/delete/<int:notification_id>', methods=['POST'])
@login_required
def delete_notification(notification_id):
    """Route to delete a notification."""
    
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == current_user.id:
        db.session.delete(notification)
        db.session.commit()
        flash('Notification deleted.', 'success')
    else:
        flash('You cannot delete this notification.', 'danger')
    
    return redirect(url_for('notifications'))

# ---------------------- Send Notification ---------------------- #
def send_notification(user_id, notification_type, message):
    """Helper function to send notifications to users."""
    
    # Create a new notification instance
    new_notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        message=message,
        read=False
    )
    
    # Add to the session and commit to the database
    db.session.add(new_notification)
    db.session.commit()

# ---------------------- Trigger Notification on Like ---------------------- #
@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    """Route to handle liking a post and sending notification."""
    
    # Like the post (assumed logic)
    post = Post.query.get_or_404(post_id)
    post.likes.append(current_user)
    db.session.commit()

    # Send notification to the post owner about the like
    send_notification(post.user_id, 'like', f"{current_user.username} liked your post.")

    flash('You liked this post!', 'success')
    return redirect(url_for('feed'))

# ---------------------- Trigger Notification on Comment ---------------------- #
@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment_on_post(post_id):
    """Route to handle commenting on a post and sending notification."""
    
    comment_text = request.form.get('comment_text')
    post = Post.query.get_or_404(post_id)
    
    # Add comment to the post (assumed logic)
    comment = Comment(user_id=current_user.id, post_id=post.id, text=comment_text)
    db.session.add(comment)
    db.session.commit()

    # Send notification to the post owner about the comment
    send_notification(post.user_id, 'comment', f"{current_user.username} commented on your post.")

    flash('Your comment has been posted!', 'success')
    return redirect(url_for('feed'))

# ---------------------- Trigger Notification on Follow ---------------------- #
@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    """Route to handle following a user and sending notification."""
    
    user_to_follow = User.query.get_or_404(user_id)
    current_user.following.append(user_to_follow)
    db.session.commit()

    # Send notification to the followed user
    send_notification(user_to_follow.id, 'follow', f"{current_user.username} followed you.")

    flash(f"You are now following {user_to_follow.username}!", 'success')
    return redirect(url_for('profile', username=user_to_follow.username))

# ---------------------- Real-time Notifications (Using WebSockets or Polling) ---------------------- #
# Implement real-time notifications using WebSockets (e.g., Flask-SocketIO) or polling for instant updates

if __name__ == '__main__':
    app.run(debug=True)
