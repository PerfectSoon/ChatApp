// websocket.js

let currentSocket = null;
let currentConnectedChatId = null;

/**
 * Подключается к WebSocket для конкретного чата.
 * Если уже подключены к этому чату – не переподключается.
 * @param {number} chatId - Идентификатор чата.
 * @param {string} token - Токен аутентификации.
 */
function connectToChat(chatId, token) {
  // Если уже есть открытое соединение с этим чатом, ничего не делаем
  if (currentSocket && currentConnectedChatId === chatId && currentSocket.readyState === WebSocket.OPEN) {
    console.log(`Уже подключены к чату ${chatId}`);
    return;
  }
  // Если есть подключение к другому чату, закрываем его
  if (currentSocket) {
    currentSocket.close();
  }
  currentConnectedChatId = chatId;
  currentSocket = new WebSocket(`ws://localhost:8001/chat/ws/${chatId}?token=${token}`);

  currentSocket.onopen = () => {
    console.log('WebSocket connection opened');
  };

  currentSocket.onmessage = (event) => {
    try {
      const messageData = JSON.parse(event.data);
      console.log('Новое сообщение:', messageData);
      if (window.handleIncomingMessage && typeof window.handleIncomingMessage === 'function') {
        window.handleIncomingMessage(messageData);
      }
    } catch (e) {
      console.error('Ошибка при обработке сообщения WebSocket', e);
    }
  };

  currentSocket.onerror = (error) => {
    console.error('WebSocket error', error);
  };

  currentSocket.onclose = () => {
    console.log('WebSocket connection closed');
    currentSocket = null;
    currentConnectedChatId = null;
  };
}

/**
 * Отправка сообщения через WebSocket.
 * @param {string} message - Сообщение для отправки.
 */
function sendWSMessage(message) {
  if (currentSocket && currentSocket.readyState === WebSocket.OPEN) {
    currentSocket.send(message);
  } else {
    console.error('WebSocket не подключён.');
  }
}

/**
 * Закрывает текущее WebSocket-соединение.
 */
function closeWSConnection() {
  if (currentSocket) {
    currentSocket.close();
    currentSocket = null;
    currentConnectedChatId = null;
  }
}

// Экспорт функций в глобальную область
window.connectToChat = connectToChat;
window.sendWSMessage = sendWSMessage;
window.closeWSConnection = closeWSConnection;
