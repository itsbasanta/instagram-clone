import re
from datetime import datetime
from werkzeug.routing import BaseConverter

# ---------------------- Filter Posts by Hashtag ---------------------- #
def filter_posts_by_hashtags(posts, hashtags):
    """Filter posts that contain any of the given hashtags."""
    return [post for post in posts if any(hashtag in post.hashtags for hashtag in hashtags)]

# ---------------------- Filter Posts by Date Range ---------------------- #
def filter_posts_by_date(posts, start_date=None, end_date=None):
    """Filter posts by a date range."""
    filtered_posts = posts
    if start_date:
        filtered_posts = [post for post in filtered_posts if post.created_at >= start_date]
    if end_date:
        filtered_posts = [post for post in filtered_posts if post.created_at <= end_date]
    return filtered_posts

# ---------------------- Filter Posts by User ---------------------- #
def filter_posts_by_user(posts, user_id):
    """Filter posts by a specific user."""
    return [post for post in posts if post.user_id == user_id]

# ---------------------- Search Posts by Title ---------------------- #
def search_posts_by_title(posts, search_term):
    """Search posts by title."""
    return [post for post in posts if search_term.lower() in post.title.lower()]

# ---------------------- Search Posts by Content ---------------------- #
def search_posts_by_content(posts, search_term):
    """Search posts by content."""
    return [post for post in posts if search_term.lower() in post.content.lower()]

# ---------------------- Filter Posts by Popularity ---------------------- #
def filter_posts_by_popularity(posts, min_likes=0, min_comments=0):
    """Filter posts that have a minimum number of likes or comments."""
    return [post for post in posts if post.likes >= min_likes and post.comments >= min_comments]

# ---------------------- Apply Date Formatting ---------------------- #
def format_post_date(post):
    """Format the post's creation date."""
    return post.created_at.strftime('%B %d, %Y')

# ---------------------- Apply Image/Video Type Filters ---------------------- #
def filter_by_media_type(posts, media_type):
    """Filter posts by media type (image/video)."""
    if media_type == 'image':
        return [post for post in posts if post.media_type == 'image']
    elif media_type == 'video':
        return [post for post in posts if post.media_type == 'video']
    return posts

# ---------------------- Apply Content Length Filter ---------------------- #
def filter_by_content_length(posts, min_length=0, max_length=1000):
    """Filter posts based on the length of the content."""
    return [post for post in posts if min_length <= len(post.content) <= max_length]

# ---------------------- Filter Users by Follower Count ---------------------- #
def filter_users_by_follower_count(users, min_followers=0):
    """Filter users based on the number of followers."""
    return [user for user in users if user.followers_count >= min_followers]

# ---------------------- Filter Content by Keywords ---------------------- #
def filter_content_by_keywords(posts, keywords):
    """Filter posts by keywords. Matches any keyword in the content or title."""
    return [post for post in posts if any(keyword.lower() in post.title.lower() or keyword.lower() in post.content.lower() for keyword in keywords)]

# ---------------------- Normalize a Search Query ---------------------- #
def normalize_search_query(query):
    """Normalize the search query by removing special characters and lowering case."""
    return re.sub(r'[^a-zA-Z0-9\s]', '', query).lower()

# ---------------------- Paginate Content ---------------------- #
def paginate_content(content_list, page, per_page=10):
    """Paginate content into pages."""
    start = (page - 1) * per_page
    end = start + per_page
    return content_list[start:end]

# ---------------------- Apply Content Filtering (Multiple Filters) ---------------------- #
def apply_filters(posts, filters):
    """Apply multiple filters to the posts."""
    for filter_func, filter_args in filters.items():
        posts = filter_func(posts, *filter_args)
    return posts

# ---------------------- URL Slug Converter ---------------------- #
class SlugConverter(BaseConverter):
    """Custom URL converter to convert slug-like strings."""
    def to_python(self, value):
        return value.replace('-', ' ').title()

    def to_url(self, value):
        return value.replace(' ', '-').lower()
