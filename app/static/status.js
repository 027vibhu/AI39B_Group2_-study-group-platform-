document.addEventListener("DOMContentLoaded", () => {

    const cards = document.querySelectorAll('.member-card');

    cards.forEach(card => {

        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-4px)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0px)';
        });

    });

});