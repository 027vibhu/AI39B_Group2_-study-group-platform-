document.addEventListener("DOMContentLoaded", () => {

    const cards = document.querySelectorAll('.member-card');
    const initButton = document.getElementById('initialize-database-btn');
    const initStatus = document.getElementById('initialize-status');

    cards.forEach(card => {

        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-4px)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0px)';
        });

    });

    if (initButton) {
        initButton.addEventListener('click', async () => {
            initButton.disabled = true;
            initStatus.textContent = 'Initializing database...';

            try {
                const response = await fetch('/initialize_database', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                const result = await response.json();
                initStatus.textContent = result.message || 'Database initialization complete.';
            } catch (error) {
                initStatus.textContent = 'Initialization failed.';
            } finally {
                initButton.disabled = false;
            }
        });
    }

});