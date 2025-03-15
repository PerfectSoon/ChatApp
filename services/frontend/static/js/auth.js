// Constants
const AUTH_SERVICE_URL = 'http://localhost:8000/auth';
const STORAGE_KEY_TOKEN = 'chat_messenger_token';

// DOM Elements
const loginForm = document.getElementById('login-form');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const errorMessageElement = document.getElementById('error-message');

// Check if user is already logged in
checkAuthStatus();

// Event Listeners
loginForm.addEventListener('submit', handleLogin);

// Functions
function checkAuthStatus() {
    const token = localStorage.getItem(STORAGE_KEY_TOKEN);

    if (token) {
        // Verify token validity by making a request to profile endpoint
        fetch(`${AUTH_SERVICE_URL}/profile`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (response.ok) {
                // Token is valid, redirect to chat page
                window.location.href = 'chat.html';
            } else {
                // Token is invalid, clear it
                localStorage.removeItem(STORAGE_KEY_TOKEN);
            }
        })
        .catch(error => {
            console.error('Ошибка проверки статуса:', error);
            localStorage.removeItem(STORAGE_KEY_TOKEN);
        });
    }
}

async function handleLogin(event) {
    event.preventDefault();

    // Clear previous error messages
    errorMessageElement.textContent = '';

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!email || !password) {
        showError('Все поля обязательны для заполнения');
        return;
    }

    try {
        // Create form data for OAuth2 format
        const formData = new FormData();
        formData.append('username', email); // API expects username field for email
        formData.append('password', password);

        const response = await fetch(`${AUTH_SERVICE_URL}/login`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.detail || 'Ошибка входа');
            return;
        }

        // Save token to local storage
        localStorage.setItem(STORAGE_KEY_TOKEN, data.access_token);

        // Redirect to chat page
        window.location.href = AUTH_SERVICE_URL+'/success';

    } catch (error) {
        console.error('Login error:', error);
        showError('Ошибка входа. Попробуйте позже');
    }
}

function showError(message) {
    errorMessageElement.textContent = message;
}