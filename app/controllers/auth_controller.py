from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User  # Assume User model is defined in user.py
from database import db  # Assuming database.py handles the DB session

# Initialize Flask app and Flask-Login
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

# ---------------------- User Loader ---------------------- #
@login_manager.user_loader
def load_user(user_id):
    """Load user by their ID for login management."""
    return User.query.get(int(user_id))

# ---------------------- Sign Up Route ---------------------- #
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Route for new user registration."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        
        # Validate password match
        if password != password_confirm:
            flash("Passwords do not match.", 'danger')
            return redirect(url_for('signup'))
        
        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or Email already exists.", 'danger')
            return redirect(url_for('signup'))
        
        # Create a new user and hash the password
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# ---------------------- Login Route ---------------------- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Route for user login."""
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        
        # Fetch the user by username or email
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        
        if user and check_password_hash(user.password, password):
            # Log in the user
            login_user(user)
            flash("Login successful!", 'success')
            return redirect(url_for('feed'))  # Redirect to the feed page after successful login
        else:
            flash("Invalid credentials. Please try again.", 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# ---------------------- Logout Route ---------------------- #
@app.route('/logout')
@login_required
def logout():
    """Route for user logout."""
    logout_user()
    flash("You have been logged out.", 'info')
    return redirect(url_for('login'))

# ---------------------- User Profile Route ---------------------- #
@app.route('/profile')
@login_required
def profile():
    """Route for viewing and editing the user's profile."""
    return render_template('profile.html', user=current_user)

# ---------------------- Password Reset Request ---------------------- #
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Route for requesting a password reset."""
    if request.method == 'POST':
        email = request.form['email']
        
        user = User.query.filter_by(email=email).first()
        if user:
            # Send reset password email (you can integrate with a mail service here)
            flash("Password reset email sent.", 'success')
        else:
            flash("Email not found.", 'danger')
        
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')

# ---------------------- Password Reset Route ---------------------- #
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    """Route for resetting the password using the token sent via email."""
    # Verify token (this would require JWT or another token-based method)
    user = verify_reset_token(token)  # Implement the token verification logic
    if user is None:
        flash("Invalid or expired token.", 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        if password != password_confirm:
            flash("Passwords do not match.", 'danger')
            return redirect(url_for('reset_password_token', token=token))
        
        # Update the user's password
        hashed_password = generate_password_hash(password, method='sha256')
        user.password = hashed_password
        db.session.commit()

        flash("Password has been reset successfully.", 'success')
        return redirect(url_for('login'))

    return render_template('reset_password_token.html', token=token)

# ---------------------- Helper Functions ---------------------- #
def verify_reset_token(token):
    """Helper function to verify the reset password token (JWT or another method)."""
    # In practice, you would decode the token here and return the user if valid.
    # Here, it's just a placeholder.
    return None  # Replace with real verification logic.

# ---------------------- Run Application ---------------------- #
if __name__ == '__main__':
    app.run(debug=True)
