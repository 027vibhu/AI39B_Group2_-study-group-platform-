document.addEventListener('DOMContentLoaded', () => {
  const tagsContainer = document.querySelector('.tags');
  const customTagInput = document.getElementById('custom-tag-input');
  const addCustomBtn = document.getElementById('add-custom-btn');
  const selectedTagsInput = document.getElementById('selected-tags-input');
  const formEl = document.querySelector('form');
  const toggleInput = document.getElementById('public-toggle');
  const toggleLabel = document.getElementById('toggle-label');
  const toggleSublabel = document.getElementById('toggle-sublabel');
  const isPrivateValue = document.getElementById('is-private-value');

  if (!tagsContainer || !selectedTagsInput || !formEl || !toggleInput) return;

  const defaultTags = ['Math', 'Science', 'Programming', 'History', 'Design'];

  function createTag(name, active = false) {
    const tag = document.createElement('div');
    tag.className = 'tag' + (active ? ' active' : '');
    tag.textContent = name;
    return tag;
  }

  function updateSelectedTags() {
    const selectedTags = Array.from(tagsContainer.querySelectorAll('.tag.active'))
      .map(tag => tag.dataset.subject || tag.textContent.trim());
    selectedTagsInput.value = selectedTags.join(',');
  }

  function updateToggleText() {
    if (toggleInput.checked) {
      toggleLabel.textContent = 'Public Room';
      toggleSublabel.textContent = 'Listed in Browse Rooms and open to anyone';
      isPrivateValue.value = '0';
    } else {
      toggleLabel.textContent = 'Private Room';
      toggleSublabel.textContent = 'Requires the room code to join';
      isPrivateValue.value = '1';
    }
  }

  function initTags() {
    if (tagsContainer.children.length === 0) {
      defaultTags.forEach((tag, index) => {
        tagsContainer.appendChild(createTag(tag, index === 0));
      });
    }
  }

  tagsContainer.addEventListener('click', (e) => {
    const tag = e.target.closest('.tag');
    if (!tag) return;

    if (tag.classList.contains('add')) {
      customTagInput.focus();
      return;
    }

    tag.classList.toggle('active');
    updateSelectedTags();
  });

  addCustomBtn.addEventListener('click', (e) => {
    e.preventDefault();
    const value = customTagInput.value.trim();
    if (!value) return;

    const exists = Array.from(tagsContainer.querySelectorAll('.tag'))
      .some(tag => tag.textContent.trim().toLowerCase() === value.toLowerCase());

    if (exists) {
      customTagInput.value = '';
      return;
    }

    const newTag = createTag(value, true);
    newTag.dataset.subject = value.toLowerCase();
    tagsContainer.appendChild(newTag);
    customTagInput.value = '';
    updateSelectedTags();
  });

  customTagInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addCustomBtn.click();
    }
  });

  toggleInput.addEventListener('change', updateToggleText);
  formEl.addEventListener('submit', updateSelectedTags);

  initTags();
  updateSelectedTags();
  updateToggleText();
});
