const sendBtn = document.getElementById('sendBtn');
const messageInput = document.getElementById('messageInput');
const chatBody = document.getElementById('chatBody');
const imageInput = document.getElementById('imageInput');

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

if (imageInput && chatBody) {
  imageInput.addEventListener('change', function () {
    const file = this.files[0];
    if (!file) return;

    const imageURL = URL.createObjectURL(file);
    const message = document.createElement('div');
    message.classList.add('message', 'sent');
    message.innerHTML = `
      <div class="message-content">
        <img src="${imageURL}">
        <div class="message-time">${getTime()}</div>
      </div>
    `;

    chatBody.appendChild(message);
    chatBody.scrollTop = chatBody.scrollHeight;
  });
}
