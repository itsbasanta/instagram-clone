from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import Message, User  # Assuming Message model is defined in message.py
from database import db  # Assuming database.py handles the DB session
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# ---------------------- Send Message Route ---------------------- #
@app.route('/send_message/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id):
    """Route to send a message to another user."""
    recipient = User.query.get(recipient_id)

    if request.method == 'POST':
        content = request.form['content']
        if not content:
            flash("Please enter a message.", 'danger')
            return redirect(url_for('send_message', recipient_id=recipient.id))

        # Create a new message
        new_message = Message(sender_id=current_user.id, recipient_id=recipient.id, content=content, timestamp=datetime.utcnow())
        db.session.add(new_message)
        db.session.commit()

        flash("Message sent successfully!", 'success')
        return redirect(url_for('view_conversation', recipient_id=recipient.id))

    return render_template('send_message.html', recipient=recipient)

# ---------------------- View Messages Route ---------------------- #
@app.route('/messages/<int:recipient_id>')
@login_required
def view_conversation(recipient_id):
    """Route to view a conversation with another user."""
    # Get all messages between the current user and the recipient
    conversation = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == recipient_id)) |
        ((Message.sender_id == recipient_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    # Get recipient's details for displaying in the conversation
    recipient = User.query.get(recipient_id)

    return render_template('view_conversation.html', conversation=conversation, recipient=recipient)

# ---------------------- Delete Message Route ---------------------- #
@app.route('/delete_message/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    """Route to delete a message."""
    message = Message.query.get(message_id)

    if not message:
        flash("Message not found.", 'danger')
        return redirect(url_for('view_conversation', recipient_id=message.recipient_id))

    # Only the sender or recipient of the message can delete it
    if message.sender_id == current_user.id or message.recipient_id == current_user.id:
        db.session.delete(message)
        db.session.commit()
        flash("Message deleted successfully.", 'success')
    else:
        flash("You are not authorized to delete this message.", 'danger')

    return redirect(url_for('view_conversation', recipient_id=message.recipient_id))

# ---------------------- Mark Message as Read ---------------------- #
@app.route('/mark_as_read/<int:message_id>', methods=['POST'])
@login_required
def mark_as_read(message_id):
    """Route to mark a message as read."""
    message = Message.query.get(message_id)

    if message and message.recipient_id == current_user.id:
        message.is_read = True
        db.session.commit()
        flash("Message marked as read.", 'success')
    else:
        flash("Message not found or you are not the recipient.", 'danger')

    return redirect(url_for('view_conversation', recipient_id=message.sender_id))

# ---------------------- View All Messages ---------------------- #
@app.route('/inbox')
@login_required
def inbox():
    """Route to view the inbox with all conversations."""
    # Get the list of conversations (messages) sorted by the latest message date
    conversations = db.session.query(Message).filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).group_by(Message.sender_id, Message.recipient_id).order_by(Message.timestamp.desc()).all()

    return render_template('inbox.html', conversations=conversations)

# ---------------------- Search Messages ---------------------- #
@app.route('/search_messages', methods=['GET'])
@login_required
def search_messages():
    """Route to search messages."""
    query = request.args.get('q', '').strip()

    if query:
        messages = Message.query.filter(
            (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id),
            Message.content.ilike(f'%{query}%')
        ).order_by(Message.timestamp.desc()).all()
    else:
        messages = []

    return render_template('search_messages.html', messages=messages, query=query)

# ---------------------- Notifications for New Messages ---------------------- #
@app.route('/check_notifications')
@login_required
def check_notifications():
    """Route to check for new messages."""
    # Get unread messages for the current user
    unread_messages = Message.query.filter(Message.recipient_id == current_user.id, Message.is_read == False).all()

    if unread_messages:
        flash(f"You have {len(unread_messages)} new messages.", 'info')

    return redirect(url_for('inbox'))

# ---------------------- Helper Function for Real-time Notifications ---------------------- #
def send_message_notification(sender_id, recipient_id, message_content):
    """Helper function to send real-time notifications when a message is received."""
    # Here you can implement the code to send notifications (e.g., email, app notifications, etc.)
    pass

# ---------------------- Run the Application ---------------------- #
if __name__ == '__main__':
    app.run(debug=True)
