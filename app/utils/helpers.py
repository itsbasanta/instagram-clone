import os
import random
import string
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

# ---------------------- Generate a Random String ---------------------- #
def generate_random_string(length=10):
    """Generate a random string of uppercase and lowercase letters and digits."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# ---------------------- Format Date ---------------------- #
def format_date(timestamp):
    """Format a timestamp into a readable date string."""
    return timestamp.strftime('%B %d, %Y at %I:%M %p')

# ---------------------- Check File Extension ---------------------- #
def allowed_file(filename, allowed_extensions=None):
    """Check if the uploaded file is allowed based on its extension."""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# ---------------------- Save File ---------------------- #
def save_file(file, upload_folder, allowed_extensions=None):
    """Save a file to the server and return its filename."""
    if file and allowed_file(file.filename, allowed_extensions):
        filename = secure_filename(file.filename)  # Secure the filename
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], upload_folder, filename)
        file.save(filepath)
        return filename
    return None

# ---------------------- Generate Slug from Text ---------------------- #
def generate_slug(text):
    """Generate a URL-friendly slug from the given text."""
    text = text.lower().strip()
    text = text.replace(" ", "-")
    text = "".join(e for e in text if e.isalnum() or e == '-')
    return text

# ---------------------- Convert Time to Human Readable Format ---------------------- #
def time_ago(timestamp):
    """Return a human-readable string of how long ago a timestamp occurred."""
    now = datetime.utcnow()
    diff = now - timestamp
    days = diff.days
    seconds = diff.seconds

    if days > 0:
        if days == 1:
            return "1 day ago"
        return f"{days} days ago"
    elif seconds < 60:
        return "Just now"
    elif seconds < 3600:
        return f"{seconds // 60} minutes ago"
    elif seconds < 86400:
        return f"{seconds // 3600} hours ago"
    return f"{days} days ago"

# ---------------------- Send Email ---------------------- #
def send_email(subject, recipient, body):
    """Helper function to send email (to be used with an email library like Flask-Mail)."""
    from flask_mail import Message
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    current_app.mail.send(msg)

# ---------------------- Sanitize HTML Input ---------------------- #
def sanitize_html(input_text):
    """Sanitize HTML input to avoid XSS and other malicious inputs."""
    from bleach import clean
    return clean(input_text)

# ---------------------- Paginate Query Results ---------------------- #
def paginate_query(query, page, per_page=10):
    """Paginate query results and return the results for the current page."""
    return query.paginate(page, per_page, False)

# ---------------------- Format File Size ---------------------- #
def format_file_size(size_in_bytes):
    """Convert file size in bytes to a human-readable format."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024**2:
        return f"{size_in_bytes // 1024} KB"
    elif size_in_bytes < 1024**3:
        return f"{size_in_bytes // 1024**2} MB"
    return f"{size_in_bytes // 1024**3} GB"

# ---------------------- Get Random Color ---------------------- #
def get_random_color():
    """Generate a random color in HEX format."""
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# ---------------------- Handle Form Validation ---------------------- #
def validate_form(form_data, required_fields):
    """Check if all required fields are present in the form data."""
    missing_fields = [field for field in required_fields if field not in form_data]
    if missing_fields:
        return False, f"Missing fields: {', '.join(missing_fields)}"
    return True, "Form validation successful"

# ---------------------- Convert Image to Thumbnail ---------------------- #
def create_thumbnail(image_path, thumbnail_folder):
    """Create a thumbnail for an image."""
    from PIL import Image
    base_width = 200
    img = Image.open(image_path)
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), Image.ANTIALIAS)
    
    thumbnail_path = os.path.join(thumbnail_folder, os.path.basename(image_path))
    img.save(thumbnail_path)
    return thumbnail_path
