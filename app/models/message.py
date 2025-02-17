from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app and database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
db = SQLAlchemy(app)

# ---------------------------- Message Model ---------------------------- #
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)  # Whether the message has been read or not
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

    def __repr__(self):
        return f'<Message {self.id} from {self.sender.username} to {self.receiver.username}>'

# ---------------------------- User Model ---------------------------- #
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    messages_sent = db.relationship('Message', foreign_keys=[Message.sender_id], backref='sender', lazy=True)
    messages_received = db.relationship('Message', foreign_keys=[Message.receiver_id], backref='receiver', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

# ---------------------------- Send Message ---------------------------- #
@app.route('/send_message/<int:receiver_id>', methods=['GET', 'POST'])
def send_message(receiver_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    receiver = User.query.get_or_404(receiver_id)

    if request.method == 'POST':
        content = request.form['content']
        
        if content.strip():  # Ensure the message is not empty
            message = Message(sender_id=session['user_id'], receiver_id=receiver.id, content=content)
            db.session.add(message)
            db.session.commit()
            flash("Message sent!", "success")
        else:
            flash("Message content cannot be empty", "danger")
        
        return redirect(url_for('view_conversation', user_id=receiver.id))

    return render_template('send_message.html', receiver=receiver)

# ---------------------------- View Conversation ---------------------------- #
@app.route('/view_conversation/<int:user_id>', methods=['GET', 'POST'])
def view_conversation(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)
    conversation = Message.query.filter(
        ((Message.sender_id == session['user_id']) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == session['user_id']))
    ).order_by(Message.timestamp.asc()).all()

    # Mark messages as read
    for message in conversation:
        if message.receiver_id == session['user_id'] and not message.is_read:
            message.is_read = True
    db.session.commit()

    return render_template('conversation.html', user=user, conversation=conversation)

# ---------------------------- Delete Message ---------------------------- #
@app.route('/delete_message/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    message = Message.query.get_or_404(message_id)

    # Ensure the message belongs to the current user (either as sender or receiver)
    if message.sender_id == session['user_id'] or message.receiver_id == session['user_id']:
        db.session.delete(message)
        db.session.commit()
        flash("Message deleted successfully!", "success")
    else:
        flash("You can only delete your own messages.", "danger")

    return redirect(url_for('view_conversation', user_id=message.receiver_id if message.sender_id == session['user_id'] else message.sender_id))

# ---------------------------- Notifications ---------------------------- #
@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    unread_messages = Message.query.filter_by(receiver_id=session['user_id'], is_read=False).all()

    return render_template('notifications.html', unread_messages=unread_messages)

# ---------------------------- Run Application ---------------------------- #
if __name__ == '__main__':
    app.run(debug=True)
