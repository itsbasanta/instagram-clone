import hashlib
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# Initialize Flask app and database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'

db = SQLAlchemy(app)

# ---------------------------- User Model ---------------------------- #
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.String(250))
    profile_pic = db.Column(db.String(120), default='default.jpg')
    is_private = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

# ---------------------------- User Registration ---------------------------- #
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------------------------- User Login ---------------------------- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Login successful!", "success")
            return redirect(url_for('profile'))

        flash("Invalid credentials, please try again.", "danger")

    return render_template('login.html')

# ---------------------------- User Profile ---------------------------- #
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=session['user_id']).first()

    if request.method == 'POST':
        if request.files['profile_pic']:
            profile_pic = request.files['profile_pic']
            filename = secure_filename(profile_pic.filename)
            profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.profile_pic = filename

        user.bio = request.form['bio']
        db.session.commit()
        flash("Profile updated successfully!", "success")

    return render_template('profile.html', user=user)

# ---------------------------- Change Password ---------------------------- #
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=session['user_id']).first()

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if check_password_hash(user.password, current_password):
            if new_password == confirm_password:
                hashed_password = generate_password_hash(new_password, method='sha256')
                user.password = hashed_password
                db.session.commit()
                flash("Password changed successfully!", "success")
                return redirect(url_for('profile'))
            else:
                flash("New passwords do not match.", "danger")
        else:
            flash("Current password is incorrect.", "danger")

    return render_template('change_password.html')

# ---------------------------- Privacy Settings ---------------------------- #
@app.route('/privacy', methods=['GET', 'POST'])
def privacy():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=session['user_id']).first()

    if request.method == 'POST':
        user.is_private = True if request.form.get('is_private') == 'on' else False
        db.session.commit()
        flash("Privacy settings updated successfully!", "success")

    return render_template('privacy.html', user=user)

# ---------------------------- Logout ---------------------------- #
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# ---------------------------- Run Application ---------------------------- #
if __name__ == '__main__':
    app.run(debug=True)
