from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_cors import CORS
from config import Config

# Initialize the Flask application
app = Flask(__name__)

# Enable CORS for handling cross-origin requests
CORS(app)

# Configure the app (using environment variables)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
mail = Mail(app)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Profile route
@app.route('/profile')
@login_required
def profile():
    from models.user import User
    # Get the user data from the database
    user = User.query.filter_by(id=current_user.id).first()
    return render_template('profile.html', user=user)

# Feed route - to show posts of the users they follow
@app.route('/feed')
@login_required
def feed():
    from models.post import Post
    posts = Post.query.all()  # Retrieve posts from the database
    return render_template('feed.html', posts=posts)

# Explore route - search posts, hashtags, and users
@app.route('/explore')
@login_required
def explore():
    from models.hashtag import Hashtag
    hashtags = Hashtag.query.all()  # Retrieve all hashtags
    return render_template('explore.html', hashtags=hashtags)

# Direct Messages (DM) route
@app.route('/messages')
@login_required
def messages():
    from models.message import Message
    # Fetch the user messages
    messages = Message.query.filter_by(recipient_id=current_user.id).all()
    return render_template('dm.html', messages=messages)

# Settings route for user preferences
@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for('index'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    from models.user import User
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "danger")

    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    from models.user import User
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("You have successfully registered", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Reset Password route (send reset link)
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    from models.user import User
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            # Send email with reset link (use Flask-Mail)
            token = user.get_reset_token()
            msg = Message("Password Reset Request", recipients=[email])
            msg.body = f"To reset your password, visit the following link: {url_for('reset_token', token=token, _external=True)}"
            mail.send(msg)
            flash("A password reset link has been sent to your email", "info")
        else:
            flash("Email address not found.", "danger")

    return render_template('reset_password.html')

# Token route for resetting password
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    from models.user import User
    user = User.verify_reset_token(token)
    if not user:
        flash("The token is invalid or expired", "danger")
        return redirect(url_for('reset_password'))

    if request.method == 'POST':
        password = request.form['password']
        user.set_password(password)
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for('login'))

    return render_template('reset_token.html')

# Running the app
if __name__ == '__main__':
    app.run(debug=True)