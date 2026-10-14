// Function that runs once the window is fully loaded
window.onload = function() {
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');

    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
};

// Function for displaying posts
function displayPosts(data) {
    const postContainer = document.getElementById('post-container');
    postContainer.innerHTML = '';

    data.forEach(post => {
        const postDiv = document.createElement('div');
        postDiv.className = 'post';

        const title = document.createElement('h2');
        title.textContent = post.title;

        const content = document.createElement('p');
        content.className = 'post-content';
        content.textContent = post.content;

        const meta = document.createElement('p');
        meta.className = 'post-meta';

        const authorLabel = document.createElement('strong');
        authorLabel.textContent = 'Author: ';

        const author = document.createElement('span');
        author.textContent = post.author;

        const separator = document.createElement('span');
        separator.textContent = ' • ';

        const dateLabel = document.createElement('strong');
        dateLabel.textContent = 'Date: ';

        const date = document.createElement('span');
        date.textContent = post.date;

        meta.append(
            authorLabel,
            author,
            separator,
            dateLabel,
            date
        );

        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', () => {
            deletePost(post.id);
        });

        postDiv.append(title, content, meta, deleteButton);
        postContainer.appendChild(postDiv);
    });
}


// Function to fetch posts and display them
function loadPosts() {
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    var sort = document.getElementById('sort-field').value;
    var direction = document.getElementById('sort-direction').value;

    var url = baseUrl + '/posts';

    // Only add sorting parameters if a sort field was selected
    if (sort) {
        url += '?sort=' + encodeURIComponent(sort) +
               '&direction=' + encodeURIComponent(direction);
    }

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Could not load posts.');
            }
            return response.json();
        })
        .then(data => {
            displayPosts(data);
        })
        .catch(error => console.error('Error:', error));
}


// Function to search posts
function searchPosts() {
    var baseUrl = document.getElementById('api-base-url').value.trim();
    var titleQuery = document.getElementById('search-title').value.trim();
    var contentQuery = document.getElementById('search-content').value.trim();

    if (!titleQuery && !contentQuery) {
        loadPosts();
        return;
    }

    var params = new URLSearchParams();

    if (titleQuery) {
        params.append('title', titleQuery);
    }
    if (contentQuery) {
        params.append('content', contentQuery);
    }

    fetch(baseUrl + '/posts/search?' + params.toString())
        .then(response => {
            if (!response.ok) {
                throw new Error('Could not search posts.');
            }
            return response.json();
        })
        .then(data => {
            displayPosts(data);
        })
        .catch(error => console.error('Error:', error));
}


// Function to add a new post
function addPost() {
    var baseUrl = document.getElementById('api-base-url').value;

    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;
    var postAuthor = document.getElementById('post-author').value;
    var postDate = document.getElementById('post-date').value;

    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: postTitle,
            content: postContent,
            author: postAuthor,
            date: postDate
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Could not add post.');
        }
        return response.json();
    })
    .then(post => {
        console.log('Post added:', post);

        // Clear input fields
        document.getElementById('post-title').value = '';
        document.getElementById('post-content').value = '';
        document.getElementById('post-author').value = '';
        document.getElementById('post-date').value = '';

        loadPosts();
    })
    .catch(error => console.error('Error:', error));
}


// Function to delete a post
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Could not delete post.');
        }

        console.log('Post deleted:', postId);
        loadPosts();
    })
    .catch(error => console.error('Error:', error));
}
