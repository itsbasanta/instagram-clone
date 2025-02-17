// DOM Content Loaded Event to ensure the script runs after the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {

    // ------------------------ Modal Functionality ------------------------
    // Get all the modals and close buttons
    const modals = document.querySelectorAll('.modal');
    const closeModalButtons = document.querySelectorAll('.close-modal');

    // Function to open a modal
    function openModal(modal) {
        modal.classList.add('show');
    }

    // Function to close a modal
    function closeModal(modal) {
        modal.classList.remove('show');
    }

    // Open modals when clicked on certain elements (example: post, story, etc.)
    const openModalElements = document.querySelectorAll('.open-modal');
    openModalElements.forEach((element) => {
        element.addEventListener('click', function (e) {
            const modalId = e.target.getAttribute('data-modal-id');
            const modal = document.getElementById(modalId);
            openModal(modal);
        });
    });

    // Close modals when the close button is clicked
    closeModalButtons.forEach((button) => {
        button.addEventListener('click', function () {
            modals.forEach((modal) => closeModal(modal));
        });
    });

    // ------------------------ Post Hover Effects ------------------------
    const posts = document.querySelectorAll('.post');
    posts.forEach((post) => {
        post.addEventListener('mouseover', function () {
            post.style.transform = 'scale(1.05)';
            post.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.2)';
        });

        post.addEventListener('mouseout', function () {
            post.style.transform = 'scale(1)';
            post.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
        });
    });

    // ------------------------ Story Hover Effects ------------------------
    const stories = document.querySelectorAll('.story');
    stories.forEach((story) => {
        story.addEventListener('mouseover', function () {
            const overlay = story.querySelector('.story-overlay');
            overlay.style.opacity = '1';
        });

        story.addEventListener('mouseout', function () {
            const overlay = story.querySelector('.story-overlay');
            overlay.style.opacity = '0';
        });
    });

    // ------------------------ Like/Comment Button Interactions ------------------------
    const likeButtons = document.querySelectorAll('.like-button');
    const commentButtons = document.querySelectorAll('.comment-button');

    likeButtons.forEach((button) => {
        button.addEventListener('click', function () {
            button.classList.toggle('liked');
            if (button.classList.contains('liked')) {
                button.style.backgroundColor = '#ff4500';  // Change color on like
            } else {
                button.style.backgroundColor = '#ff6347';  // Original color
            }
        });
    });

    commentButtons.forEach((button) => {
        button.addEventListener('click', function () {
            const post = button.closest('.post');
            const commentInput = post.querySelector('.comment-input');
            commentInput.classList.toggle('show');
            if (commentInput.classList.contains('show')) {
                commentInput.focus();
            }
        });
    });

    // ------------------------ Sticky Navigation ------------------------
    window.addEventListener('scroll', function () {
        const header = document.querySelector('header');
        if (window.scrollY > 0) {
            header.classList.add('sticky');
        } else {
            header.classList.remove('sticky');
        }
    });

    // ------------------------ Story Auto-Change Effect ------------------------
    const storiesContainer = document.querySelector('.stories-container');
    if (storiesContainer) {
        let storyIndex = 0;
        const storiesArray = Array.from(storiesContainer.children);
        setInterval(() => {
            storiesArray.forEach((story, index) => {
                if (index === storyIndex) {
                    story.style.transform = 'scale(1.1)';
                    story.style.transition = 'transform 0.3s ease';
                } else {
                    story.style.transform = 'scale(1)';
                }
            });
            storyIndex = (storyIndex + 1) % storiesArray.length;
        }, 3000); // Change every 3 seconds
    }

    // ------------------------ Notifications Bell Animation ------------------------
    const notificationBell = document.querySelector('.notification-bell');
    const notificationsCount = document.querySelector('.notification-count');
    let notificationCount = 0;

    setInterval(() => {
        notificationCount++;
        notificationsCount.textContent = notificationCount;
        notificationBell.classList.add('new-notification');
        setTimeout(() => {
            notificationBell.classList.remove('new-notification');
        }, 500);
    }, 10000); // Add a notification every 10 seconds (example for animation)

    // ------------------------ Smooth Scroll for Navigation ------------------------
    const navLinks = document.querySelectorAll('header .nav a');
    navLinks.forEach((link) => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = link.getAttribute('href').slice(1);
            const targetElement = document.getElementById(targetId);
            window.scrollTo({
                top: targetElement.offsetTop - 50, // Adjust scroll position for header height
                behavior: 'smooth'
            });
        });
    });

    // ------------------------ Image Lazy Loading ------------------------
    const lazyLoadImages = document.querySelectorAll('img.lazy');
    const options = {
        rootMargin: '0px 0px 100px 0px',
        threshold: 0.1
    };
    const observer = new IntersectionObserver(function (entries, observer) {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src; // Set the image source from data-src attribute
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    }, options);

    lazyLoadImages.forEach((img) => {
        observer.observe(img);
    });

});




// Modal open and close functionality for post details
document.querySelectorAll('.open-modal').forEach((element) => {
    element.addEventListener('click', (e) => {
        const modalId = e.target.getAttribute('data-modal-id');
        const modal = document.getElementById(modalId);
        modal.classList.add('show');
    });
});

// Close modal functionality
document.querySelectorAll('.close-modal').forEach((button) => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.modal').forEach((modal) => {
            modal.classList.remove('show');
        });
    });
});



// Modal functionality for login and sign up forms
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function (e) {
        e.preventDefault();
        if (this.getAttribute('href') === "#login") {
            document.getElementById('login').classList.add('show-modal');
        } else if (this.getAttribute('href') === "#signup") {
            document.getElementById('signup').classList.add('show-modal');
        }
    });
});

// Close the modals when the user clicks on the close button
document.querySelectorAll('.close-modal').forEach(closeBtn => {
    closeBtn.addEventListener('click', () => {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show-modal');
        });
    });
});

// Close the modal if clicked outside of the modal content
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show-modal');
        });
    }
});


// JavaScript for liking and commenting on posts
document.querySelectorAll('.like-btn').forEach(button => {
    button.addEventListener('click', function() {
        this.classList.toggle('liked');
        if (this.classList.contains('liked')) {
            this.innerText = "Liked";
        } else {
            this.innerText = "Like";
        }
    });
});

// Toggle comment section (can be expanded)
document.querySelectorAll('.comment-btn').forEach(button => {
    button.addEventListener('click', function() {
        const commentSection = this.parentElement.querySelector('.comment-section');
        if (!commentSection) {
            const newCommentSection = document.createElement('div');
            newCommentSection.classList.add('comment-section');
            newCommentSection.innerHTML = `
                <input type="text" placeholder="Add a comment...">
                <button class="post-comment">Post</button>
            `;
            this.parentElement.appendChild(newCommentSection);
        } else {
            commentSection.classList.toggle('show');
        }
    });
});

// Edit Profile functionality (trigger modal or navigate to a new page)
document.querySelector('.edit-profile-btn').addEventListener('click', function() {
    window.location.href = '/edit-profile'; // Redirect to Edit Profile page or open modal
});


// Toggle Like button
document.querySelectorAll('.like-btn').forEach(button => {
    button.addEventListener('click', function () {
        this.classList.toggle('liked');
        if (this.classList.contains('liked')) {
            this.innerText = "Liked";
        } else {
            this.innerText = "Like";
        }
    });
});

// Toggle Comment Section visibility
document.querySelectorAll('.comment-btn').forEach(button => {
    button.addEventListener('click', function () {
        const commentSection = this.parentElement.nextElementSibling;
        commentSection.classList.toggle('show');
    });
});

// Add Comment functionality
document.querySelectorAll('.post-comment').forEach(button => {
    button.addEventListener('click', function () {
        const commentInput = this.previousElementSibling;
        const commentText = commentInput.value.trim();
        if (commentText) {
            const commentSection = this.closest('.comments-section');
            const newComment = document.createElement('div');
            newComment.classList.add('comment');
            newComment.innerHTML = `<strong>Your Name</strong> ${commentText} <span class="comment-time">Just Now</span>`;
            commentSection.insertBefore(newComment, commentSection.querySelector('.comment-form'));
            commentInput.value = ''; // Clear input after posting
        }
    });
});


// Like Button Interaction
document.querySelectorAll('.like-btn').forEach(button => {
    button.addEventListener('click', function () {
        this.classList.toggle('liked');
        if (this.classList.contains('liked')) {
            this.innerHTML = "❤️ Liked";
        } else {
            this.innerHTML = "❤️ Like";
        }
    });
});

// View Button Interaction (Modal or Full Screen View)
document.querySelectorAll('.view-btn').forEach(button => {
    button.addEventListener('click', function () {
        // Implement the logic to open a modal or full-screen view of the post
        alert("View post in full-screen or modal!");
    });
});

// Search Bar Interaction
document.getElementById('search-button').addEventListener('click', function () {
    const searchQuery = document.getElementById('search-input').value.trim();
    if (searchQuery) {
        alert("Searching for: " + searchQuery);
        // Implement the logic to search posts, users, or hashtags based on the query
    } else {
        alert("Please enter something to search!");
    }
});

// Send Button Interaction
document.getElementById('send-message').addEventListener('click', function () {
    const messageInput = document.getElementById('message-input');
    const messageText = messageInput.value.trim();

    if (messageText) {
        appendMessage('user', messageText);  // Append user's message
        messageInput.value = '';  // Clear the input field

        // Simulate Admin reply with a slight delay
        setTimeout(() => {
            appendMessage('admin', 'Thank you for your message!');  // Admin reply
        }, 1000);
    }
});

// Emoji Picker Toggle
document.getElementById('emoji-btn').addEventListener('click', function () {
    const emojiPicker = document.getElementById('emoji-picker');
    emojiPicker.classList.toggle('show');
});

// Append Emoji to the Input Field
function appendEmoji(emoji) {
    const messageInput = document.getElementById('message-input');
    messageInput.value += emoji;  // Add the emoji to the message input
    document.getElementById('emoji-picker').classList.remove('show');  // Close the emoji picker
}

// Function to Append Messages to the Chat Box
function appendMessage(sender, text) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.innerHTML = `<p>${text}</p>`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;  // Scroll to the latest message
}

// Sample notifications data (this could come from a database or API)
const notificationsData = [
    { id: 1, type: 'like', message: 'Your post got a like from John Doe!', read: false, time: '1 hour ago' },
    { id: 2, type: 'comment', message: 'Sarah commented on your photo!', read: false, time: '2 hours ago' },
    { id: 3, type: 'follow', message: 'You have a new follower: Jane Smith', read: true, time: '3 hours ago' },
    { id: 4, type: 'message', message: 'You received a message from Admin', read: false, time: '4 hours ago' },
];

// Function to render notifications
function renderNotifications() {
    const notificationList = document.getElementById('notification-list');
    notificationList.innerHTML = ''; // Clear existing notifications

    notificationsData.forEach(notification => {
        const notificationDiv = document.createElement('div');
        notificationDiv.classList.add('notification');
        if (!notification.read) {
            notificationDiv.classList.add('unread');
        }

        notificationDiv.innerHTML = `
            <div class="notification-icon">
                <img src="assets/icons/${notification.type}.png" alt="${notification.type}" />
            </div>
            <div class="notification-text">
                <p>${notification.message}</p>
                <span class="notification-time">${notification.time}</span>
            </div>
        `;

        // Add the notification to the list
        notificationList.appendChild(notificationDiv);
    });
}

// Mark notification as read on click
document.getElementById('notification-list').addEventListener('click', function (e) {
    if (e.target.closest('.notification')) {
        const notification = e.target.closest('.notification');
        notification.classList.remove('unread');
        const notificationId = notificationsData.findIndex(n => n.message === notification.querySelector('.notification-text p').textContent);
        notificationsData[notificationId].read = true;
    }
});

// Clear all notifications
document.getElementById('clear-notifications').addEventListener('click', function () {
    notificationsData.forEach(notification => {
        notification.read = true;
    });
    renderNotifications();  // Re-render notifications to update the list
});

// Initial render of notifications
renderNotifications();

// Function to handle profile form submission
document.getElementById('profile-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const bio = document.getElementById('bio').value;
    const profilePic = document.getElementById('profile-pic').files[0];

    console.log('Profile Saved:', { username, bio, profilePic });

    alert('Profile settings saved successfully!');
});

// Function to handle privacy form submission
document.getElementById('privacy-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const accountPrivacy = document.getElementById('account-privacy').value;
    const messagePrivacy = document.getElementById('message-privacy').value;

    console.log('Privacy Settings Saved:', { accountPrivacy, messagePrivacy });

    alert('Privacy settings saved successfully!');
});

// Function to handle notification form submission
document.getElementById('notification-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const likesNotifications = document.getElementById('likes-notifications').checked;
    const commentsNotifications = document.getElementById('comments-notifications').checked;
    const followersNotifications = document.getElementById('followers-notifications').checked;

    console.log('Notification Settings Saved:', { likesNotifications, commentsNotifications, followersNotifications });

    alert('Notification settings saved successfully!');
});

// Function to handle password form submission
document.getElementById('password-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (newPassword !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }

    console.log('Password Changed:', { currentPassword, newPassword });

    alert('Password changed successfully!');
});
