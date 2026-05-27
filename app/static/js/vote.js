document.addEventListener('DOMContentLoaded', () => {
    const chatBody = document.getElementById('chatBody');

    if (!chatBody) return;

    chatBody.addEventListener('click', async (e) => {
        const voteBtn = e.target.closest('.vote-btn');
        if (!voteBtn) return;

        const messageEl = voteBtn.closest('.message');
        const messageId = messageEl.dataset.messageId;
        const voteType = voteBtn.dataset.vote;

        if (!messageId) return;

        try {
            const res = await fetch('/vote', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message_id: messageId,
                    vote_type: voteType
                })
            });

            const data = await res.json();

            if (res.ok) {
                const scoreEl = messageEl.querySelector('.vote-score');
                scoreEl.textContent = data.net_score;

                // Update score color
                scoreEl.classList.remove('text-green-600', 'text-red-600', 'text-gray-500');
                if (data.net_score > 0) scoreEl.classList.add('text-green-600');
                else if (data.net_score < 0) scoreEl.classList.add('text-red-600');
                else scoreEl.classList.add('text-gray-500');

                // Highlight active button
                messageEl.querySelectorAll('.vote-btn').forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.vote === voteType);
                });
            }
        } catch (err) {
            console.error('Vote error:', err);
        }
    });
});