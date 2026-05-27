document.addEventListener("DOMContentLoaded", () => {

    const memberCards = document.querySelectorAll('.member-card');

    // Only ensure UI text matches backend-rendered state
    function syncUI() {
        memberCards.forEach(card => {

            const statusText = card.querySelector('p');

            const isOnline = card.classList.contains('online');

            statusText.textContent = isOnline
                ? "Status: Online"
                : "Status: Offline";
        });
    }

    syncUI();

});