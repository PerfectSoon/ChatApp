// Constants
const AUTH_SERVICE_URL = 'http://localhost:8000/auth';

// DOM Elements
const registerForm = document.getElementById('register-form');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const confirmPasswordInput = document.getElementById('confirm-password');
const errorMessageElement = document.getElementById('error-message');

// Check if user is already logged in
checkAuthStatus();

// Event Listeners
registerForm.addEventListener('submit', handleRegister);

// Functions
function checkAuthStatus() {
    const token = localStorage.getItem('chat_messenger_token');

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
                localStorage.removeItem('chat_messenger_token');
            }
        })
        .catch(error => {
            console.error('Error checking auth status:', error);
            localStorage.removeItem('chat_messenger_token');
        });
    }
}

async function handleRegister(event) {
    event.preventDefault();

    // Clear previous error messages
    errorMessageElement.textContent = '';

    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    // Form validation
    if (!name || !email || !password || !confirmPassword) {
        showError('Все поля обязательны для заполнения');
        return;
    }

    if (password !== confirmPassword) {
        showError('Пароли не совпадают');
        return;
    }

    if (password.length < 6) {
        showError('Пароль должен быть минимум 6 символов');
        return;
    }

    try {
        const response = await fetch(`${AUTH_SERVICE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nickname: name,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.detail || 'Ошибка регистрации');
            return;
        }

        // Registration successful - redirect to login page
        alert('Регистрация прошла успешно!');
        window.location.href = 'auth.html';

    } catch (error) {
        console.error('Registration error:', error);
        showError('Во время регистрации произошла ошибка. Попробуйте позже.');
    }
}

function showError(message) {
    errorMessageElement.textContent = message;
}