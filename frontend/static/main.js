// Function that runs once the window is fully loaded
window.onload = function() {
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');

    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
};


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
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';

                postDiv.innerHTML = `
                    <h2>${post.title}</h2>
                    <p class="post-content">${post.content}</p>
                    <p class="post-meta">
                        <strong>Author:</strong> ${post.author}
                        <span>•</span>
                        <strong>Date:</strong> ${post.date}
                    </p>
                    <button onclick="deletePost(${post.id})">Delete</button>
                `;

                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));
}


// Function to search posts
function searchPosts() {
    var baseUrl = document.getElementById('api-base-url').value;
    var searchQuery = document.getElementById('search-input').value;

    if (!searchQuery) {
        loadPosts();
        return;
    }

    fetch(baseUrl + '/posts/search?search=' + encodeURIComponent(searchQuery))
        .then(response => {
            if (!response.ok) {
                throw new Error('Could not search posts.');
            }
            return response.json();
        })
        .then(data => {
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';

                postDiv.innerHTML = `
                    <h2>${post.title}</h2>
                    <p class="post-content">${post.content}</p>
                    <p class="post-meta">
                        <strong>Author:</strong> ${post.author}
                        <span>•</span>
                        <strong>Date:</strong> ${post.date}
                    </p>
                    <button onclick="deletePost(${post.id})">Delete</button>
                `;

                postContainer.appendChild(postDiv);
            });
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
