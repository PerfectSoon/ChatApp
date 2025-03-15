// chat.js

// Константы
const AUTH_SERVICE_URL = 'http://localhost:8000/auth';
const CHAT_SERVICE_URL = 'http://localhost:8001/chat';
const STORAGE_KEY_TOKEN = 'chat_messenger_token';

// Состояние
let currentUser = null;
let currentChatId = null;
let chats = [];

// Элементы DOM
const userNameElement = document.getElementById('user-name');
const userEmailElement = document.getElementById('user-email');
const logoutBtn = document.getElementById('logout-btn');
const chatListElement = document.getElementById('chat-list');
const newChatBtn = document.getElementById('new-chat-btn');
const currentChatNameElement = document.getElementById('current-chat-name');
const messagesContainer = document.getElementById('messages-container');
const messageInput = document.getElementById('message-input');
const sendMessageBtn = document.getElementById('send-message-btn');
const addUserBtn = document.getElementById('add-user-btn');
const deleteBtn = document.getElementById('delete-chat-btn');

// Модальные окна
const newChatModal = document.getElementById('new-chat-modal');
const createChatForm = document.getElementById('create-chat-form');
const addUserModal = document.getElementById('add-user-modal');
const addUserForm = document.getElementById('add-user-form');
const closeModalButtons = document.querySelectorAll('.close-modal');

// Инициализация – проверка токена и загрузка профиля/чатов
checkAuthStatus();

// Слушатели событий
logoutBtn.addEventListener('click', handleLogout);
newChatBtn.addEventListener('click', () => showModal(newChatModal));
createChatForm.addEventListener('submit', handleCreateChat);
addUserBtn.addEventListener('click', () => showModal(addUserModal));
addUserForm.addEventListener('submit', handleAddUser);
deleteBtn.addEventListener('click', handleDeleteChat);
sendMessageBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

closeModalButtons.forEach(button => {
  button.addEventListener('click', (e) => {
    const modal = e.target.closest('.modal');
    hideModal(modal);
  });
});

// Закрытие модальных окон при клике вне их области
window.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal')) {
    hideModal(e.target);
  }
});

// Функции

async function checkAuthStatus() {
  const token = localStorage.getItem(STORAGE_KEY_TOKEN);
  if (!token) {
    window.location.href = 'auth.html';
    return;
  }
  try {
    const response = await fetch(`${AUTH_SERVICE_URL}/profile`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      throw new Error('Неправильный токен');
    }
    currentUser = await response.json();
    userNameElement.textContent = currentUser.nickname;
    userEmailElement.textContent = currentUser.email;
    await loadChats();
  } catch (error) {
    console.error('Auth error:', error);
    localStorage.removeItem(STORAGE_KEY_TOKEN);
    window.location.href = 'auth.html';
  }
}

function handleLogout() {
  localStorage.removeItem(STORAGE_KEY_TOKEN);
  window.location.href = 'auth.html';
}

async function loadChats() {
  const token = localStorage.getItem(STORAGE_KEY_TOKEN);
  try {
    const response = await fetch(`${CHAT_SERVICE_URL}/all_chats`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      throw new Error('Ошибка загрузки чатов');
    }
    chats = await response.json();
    renderChatList();
  } catch (error) {
    console.error('Ошибка загрузки чатов:', error);
  }
}

function renderChatList() {
  chatListElement.innerHTML = '';
  if (chats.length === 0) {
    chatListElement.innerHTML = '<p>Нет доступных чатов</p>';
    return;
  }
  chats.forEach(chat => {
    const chatItem = document.createElement('div');
    chatItem.classList.add('chat-item');
    chatItem.textContent = chat.name || `Чат ${chat.id}`;
    chatItem.addEventListener('click', () => openChat(chat));
    chatListElement.appendChild(chatItem);
  });
}

function openChat(chat) {
  if (currentChatId === chat.id) return;
  currentChatId = chat.id;
  currentChatNameElement.textContent = chat.name || `Чат ${currentChatId}`;
  messagesContainer.innerHTML = '';
  messageInput.disabled = false;
  sendMessageBtn.disabled = false;
  loadChatMessages(currentChatId);
  const token = localStorage.getItem(STORAGE_KEY_TOKEN);
  // Подключаемся к WebSocket через websocket.js
  window.connectToChat(currentChatId, token);
}

async function loadChatMessages(chatId) {
  const token = localStorage.getItem(STORAGE_KEY_TOKEN);
  try {
    const response = await fetch(`${CHAT_SERVICE_URL}/${chatId}/messages`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      throw new Error('Ошибка загрузки сообщений');
    }
    const messages = await response.json();
    renderMessages(messages);
  } catch (error) {
    console.error('Ошибка загрузки сообщений:', error);
  }
}

function renderMessages(messages) {
  messagesContainer.innerHTML = '';
  if (messages.length === 0) {
    messagesContainer.innerHTML = '<p>Нет сообщений в чате</p>';
    return;
  }
  messages.forEach(msg => {
    appendMessage(msg);
  });
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Функция для добавления сообщения в интерфейс
function appendMessage(msg) {
  const msgElem = document.createElement('div');
  msgElem.classList.add('message');
  if (msg.sender_id === currentUser.id) {
    msgElem.classList.add('my-message');
  } else {
    msgElem.classList.add('other-message');
  }
  msgElem.innerHTML = `
    <div class="message-header">
        <span class="message-sender">${msg.sender_id}</span>
        <span class="message-time">${new Date(msg.sent_at).toLocaleTimeString()}</span>
    </div>
    <div class="message-content">${msg.text}</div>
`;
  messagesContainer.appendChild(msgElem);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Эта функция будет вызываться как из WebSocket, так и для оптимистичного обновления UI
function handleIncomingMessage(message) {
  appendMessage(message);
}

// Делаем функцию handleIncomingMessage доступной глобально (для websocket.js)
window.handleIncomingMessage = handleIncomingMessage;

async function handleCreateChat(e) {
  e.preventDefault();
  const chatNameInput = document.getElementById('chat-name');
  const chatName = chatNameInput.value.trim();
  if (!chatName) return;
  const token = localStorage.getItem(STORAGE_KEY_TOKEN);
  try {
    const response = await fetch(`${CHAT_SERVICE_URL}/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ name: chatName })
    });
    if (!response.ok) {
      throw new Error('Ошибка создания чата');
    }
    const newChat = await response.json();
    chats.push(newChat);
    renderChatList();
    hideModal(newChatModal);
    chatNameInput.value = '';
  } catch (error) {
    console.error('Ошибка создания чата:', error);
  }
}

async function handleAddUser(e) {
  e.preventDefault();
  const userIdInput = document.getElementById('user-id');
  const userId = userIdInput.value.trim();
  if (!userId || !currentChatId) return;
  const token = localStorage.getItem(STORAGE_KEY_TOKEN);
  try {
    const response = await fetch(`${CHAT_SERVICE_URL}/${currentChatId}/add/${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ chat_id: currentChatId, user_id: parseInt(userId) })
    });
    if (!response.ok) {
      throw new Error('Ошибка добавления пользователя в чат');
    }
    await loadChats();
    hideModal(addUserModal);
    userIdInput.value = '';
  } catch (error) {
    console.error('Ошибка добавления пользователя:', error);
  }
}

async function handleDeleteChat() {
  if (!currentChatId) return;
  const token = localStorage.getItem(STORAGE_KEY_TOKEN);
  try {
    const response = await fetch(`${CHAT_SERVICE_URL}/delete/${currentChatId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      throw new Error('Ошибка удаления чата');
    }
    chats = chats.filter(chat => chat.id !== currentChatId);
    renderChatList();
    currentChatId = null;
    currentChatNameElement.textContent = 'Выбрать чат';
    messagesContainer.innerHTML = '<div class="no-chat-selected"><p>Выберите чат или создайте новый</p></div>';
    messageInput.disabled = true;
    sendMessageBtn.disabled = true;
    window.closeWSConnection();
  } catch (error) {
    console.error('Ошибка удаления чата:', error);
  }
}

function sendMessage() {
  const message = messageInput.value.trim();
  if (!message) return;
  // Оптимистичное обновление UI: сразу добавляем сообщение
  const messageObj = {
    sender_id: currentUser.nickname,
    text: message,
    sent_at: new Date().toISOString()
  };
  handleIncomingMessage(messageObj);
  // Отправляем сообщение через WebSocket
  window.sendWSMessage(message);
  messageInput.value = '';
}

// Функции для управления модальными окнами
function showModal(modal) {
  modal.style.display = 'block';
}

function hideModal(modal) {
  modal.style.display = 'none';
}
