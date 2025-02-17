from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User  # Assuming the User model is defined in user.py
from database import db  # Assuming database.py handles the DB session
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# ---------------------- Settings Page Route ---------------------- #
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Route to display and update user settings page."""
    
    if request.method == 'POST':
        # Handle form submission for updating profile and privacy settings
        name = request.form.get('name')
        bio = request.form.get('bio')
        email = request.form.get('email')
        profile_picture = request.files.get('profile_picture')

        # Update User Profile Info
        if name:
            current_user.name = name
        if bio:
            current_user.bio = bio
        if email and email != current_user.email:
            current_user.email = email
        
        # Update Profile Picture (Optional: save the file to server and update the database)
        if profile_picture:
            profile_picture_path = save_profile_picture(profile_picture)
            current_user.profile_picture = profile_picture_path
        
        # Commit the changes to the database
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('settings'))

    return render_template('settings.html', user=current_user)

# ---------------------- Change Password Route ---------------------- #
@app.route('/settings/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Route to change the user's account password."""
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')

        # Check if current password is correct
        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('change_password'))

        # Check if new passwords match
        if new_password != confirm_new_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('change_password'))

        # Update password (hash the new password before saving)
        hashed_password = generate_password_hash(new_password)
        current_user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('settings'))

    return render_template('change_password.html')

# ---------------------- Privacy Settings Route ---------------------- #
@app.route('/settings/privacy', methods=['GET', 'POST'])
@login_required
def privacy():
    """Route to manage privacy settings (e.g., account visibility, block users)."""
    
    if request.method == 'POST':
        # Update Privacy Settings: e.g., Make account private or public
        account_private = request.form.get('account_private') == 'on'
        current_user.account_private = account_private
        db.session.commit()
        flash('Your privacy settings have been updated!', 'success')
        return redirect(url_for('settings'))

    return render_template('privacy.html', user=current_user)

# ---------------------- Manage Notifications Route ---------------------- #
@app.route('/settings/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    """Route to manage notification settings."""
    
    if request.method == 'POST':
        # Get the notification preferences from the form
        likes_notifications = request.form.get('likes_notifications') == 'on'
        comments_notifications = request.form.get('comments_notifications') == 'on'
        message_notifications = request.form.get('message_notifications') == 'on'

        # Update notification preferences
        current_user.likes_notifications = likes_notifications
        current_user.comments_notifications = comments_notifications
        current_user.message_notifications = message_notifications
        db.session.commit()
        flash('Your notification preferences have been updated!', 'success')
        return redirect(url_for('settings'))

    return render_template('notifications.html', user=current_user)

# ---------------------- Account Deactivation Route ---------------------- #
@app.route('/settings/deactivate_account', methods=['POST'])
@login_required
def deactivate_account():
    """Route to deactivate a user account."""
    
    # Deactivate account by updating user status
    current_user.is_active = False
    db.session.commit()
    flash('Your account has been deactivated.', 'info')
    return redirect(url_for('logout'))

# ---------------------- Save Profile Picture Helper ---------------------- #
def save_profile_picture(profile_picture):
    """Helper function to save profile picture."""
    
    picture_filename = f"{current_user.id}_profile.jpg"  # You can change this logic to handle file extensions better
    profile_picture.save(f"static/images/profile_pictures/{picture_filename}")
    return f"/static/images/profile_pictures/{picture_filename}"

# ---------------------- Run the Application ---------------------- #
if __name__ == '__main__':
    app.run(debug=True)
