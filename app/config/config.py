import os

# ---------------------- General App Settings ---------------------- #

# Secret key used to sign session cookies and other cryptographic operations
# Make sure to set this to a random string for security purposes
SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey')

# The environment that the application is running in
# Options: 'development', 'production', or 'testing'
ENV = os.environ.get('FLASK_ENV', 'development')

# Debug mode - can be turned on in development to show detailed error messages
DEBUG = ENV == 'development'

# ---------------------- Database Configuration ---------------------- #

# Database URI (can be SQLite, PostgreSQL, MySQL, etc.)
# Here we're using SQLite as an example. In production, you'd typically use something more robust.
DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///app.db')

# Database echo flag - set to True to log all SQL statements
SQLALCHEMY_ECHO = ENV == 'development'

# Enables SQLAlchemy's session to commit automatically at the end of a request
SQLALCHEMY_TRACK_MODIFICATIONS = False

# ---------------------- Email and Notification Settings ---------------------- #

# Email settings (for notifications, password resets, etc.)
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'your-email@example.com')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your-email-password')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@example.com')

# ---------------------- Caching Configuration ---------------------- #

# Caching configuration for performance optimization (optional)
CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')  # Options: 'simple', 'redis', 'memcached'
CACHE_DEFAULT_TIMEOUT = 300

# ---------------------- Session and Security Settings ---------------------- #

# Session timeout (in seconds)
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

# Enable CSRF protection for forms
CSRF_ENABLED = True

# CSRF secret key for form submission security
CSRF_SESSION_KEY = os.environ.get('CSRF_SESSION_KEY', 'mycsrfsecretkey')

# ---------------------- Other Custom Configurations ---------------------- #

# Maximum file upload size (in bytes)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

# Allowed file extensions for uploads (e.g., images, videos)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mkv', 'mov'}

# ---------------------- Logging Configuration ---------------------- #

# Enable logging in production environment
if ENV == 'production':
    LOGGING_LEVEL = 'ERROR'
else:
    LOGGING_LEVEL = 'DEBUG'

LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING_FILE = 'app.log'

# ---------------------- Application Specific Configuration ---------------------- #

# Maximum number of posts per page for pagination
POSTS_PER_PAGE = 20

# Maximum number of users to fetch for search results
USER_SEARCH_LIMIT = 10

# ---------------------- Setup for Flask-Extensions ---------------------- #

# Flask extensions (e.g., SQLAlchemy, Mail, Cache, etc.)
class Config:
    """Base configuration."""
    SECRET_KEY = SECRET_KEY
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = SQLALCHEMY_TRACK_MODIFICATIONS
    MAIL_SERVER = MAIL_SERVER
    MAIL_PORT = MAIL_PORT
    MAIL_USE_TLS = MAIL_USE_TLS
    MAIL_USERNAME = MAIL_USERNAME
    MAIL_PASSWORD = MAIL_PASSWORD
    MAIL_DEFAULT_SENDER = MAIL_DEFAULT_SENDER
    CACHE_TYPE = CACHE_TYPE
    CACHE_DEFAULT_TIMEOUT = CACHE_DEFAULT_TIMEOUT
    CSRF_ENABLED = CSRF_ENABLED
    CSRF_SESSION_KEY = CSRF_SESSION_KEY
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH
    ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS
    LOGGING_LEVEL = LOGGING_LEVEL
    LOGGING_FORMAT = LOGGING_FORMAT
    LOGGING_FILE = LOGGING_FILE
    POSTS_PER_PAGE = POSTS_PER_PAGE
    USER_SEARCH_LIMIT = USER_SEARCH_LIMIT
    PERMANENT_SESSION_LIFETIME = PERMANENT_SESSION_LIFETIME


# ---------------------- Development Configuration ---------------------- #
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_ECHO = True

# ---------------------- Production Configuration ---------------------- #
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENV = 'production'
    SQLALCHEMY_ECHO = False

# ---------------------- Testing Configuration ---------------------- #
class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'  # Use a separate database for tests
    DEBUG = False
    ENV = 'testing'
