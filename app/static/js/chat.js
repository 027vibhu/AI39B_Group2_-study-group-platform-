const sendBtn = document.getElementById('sendBtn');
const messageInput = document.getElementById('messageInput');
const chatBody = document.getElementById('chatBody');
const fileInput = document.getElementById('fileInput');

function sendMessage() {
  const text = messageInput.value.trim();
  if (!text) return;

  const message = document.createElement('div');
  message.classList.add('message', 'sent');
  message.innerHTML = `
    <div class="message-content">
      ${text}
      <div class="message-time">${getTime()}</div>
    </div>
  `;

  chatBody.appendChild(message);
  messageInput.value = '';
  chatBody.scrollTop = chatBody.scrollHeight;
}

function getTime() {
  const now = new Date();
  return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

if (sendBtn && messageInput) {
  sendBtn.addEventListener('click', sendMessage);
  messageInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });
}

// File uploads are handled by the chat template script (multi-file upload, previews, and send)
