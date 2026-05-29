// Tag selection and add-tag interactivity
document.addEventListener('DOMContentLoaded', () => {
  const tagsContainer = document.querySelector('.tags');
  if (!tagsContainer) return;

  tagsContainer.addEventListener('click', (e) => {
    const el = e.target.closest('.tag');
    if (!el) return;

    if (el.classList.contains('add')) {
      const name = prompt('Add a subject tag:');
      if (name && name.trim()) {
        const tag = document.createElement('div');
        tag.className = 'tag';
        tag.textContent = name.trim();
        // insert before the add button
        tagsContainer.insertBefore(tag, el);
      }
      return;
    }

    // toggle active state
    el.classList.toggle('active');
  });
});
