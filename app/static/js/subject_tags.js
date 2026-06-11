/**
 * Subject Tags Management JavaScript
 * Handles adding, removing, and displaying subject tags for rooms
 */

class SubjectTagManager {
    constructor(roomId) {
        this.roomId = roomId;
        this.baseApiUrl = '/api';
        this.allTags = [];
        this.roomTags = [];
        this.init();
    }

    /**
     * Initialize the tag manager
     */
    init() {
        this.loadRoomTags();
        this.loadAvailableTags();
        this.attachEventListeners();
    }

    /**
     * Load all tags for the current room
     */
    async loadRoomTags() {
        try {
            const response = await fetch(`${this.baseApiUrl}/rooms/${this.roomId}/tags`);
            const data = await response.json();

            if (data.status === 200) {
                this.roomTags = data.tags || [];
                this.renderRoomTags();
            } else {
                console.error('Error loading room tags:', data.error);
            }
        } catch (error) {
            console.error('Error fetching room tags:', error);
        }
    }

    /**
     * Load all available tags in the system
     */
    async loadAvailableTags() {
        try {
            const response = await fetch(`${this.baseApiUrl}/tags`);
            const data = await response.json();

            if (data.status === 200) {
                this.allTags = data.tags || [];
                this.renderAvailableTags();
            } else {
                console.error('Error loading available tags:', data.error);
            }
        } catch (error) {
            console.error('Error fetching available tags:', error);
        }
    }

    /**
     * Render room tags in the DOM
     */
    renderRoomTags() {
        const container = document.getElementById('roomTagsContainer');
        if (!container) return;

        container.innerHTML = '';

        if (this.roomTags.length === 0) {
            container.innerHTML = '<p class="tag-empty-state">No tags added yet</p>';
            return;
        }

        this.roomTags.forEach(tag => {
            const tagElement = document.createElement('div');
            tagElement.className = 'tag-badge removable';
            tagElement.innerHTML = `
                ${this.escapeHtml(tag.tag_name)}
                <button class="tag-remove-btn" data-tag-id="${tag.id}" title="Remove tag">
                    &times;
                </button>
            `;

            tagElement.querySelector('.tag-remove-btn').addEventListener('click', (e) => {
                e.preventDefault();
                this.removeTagFromRoom(tag.id);
            });

            container.appendChild(tagElement);
        });
    }

    /**
     * Render available tags for suggestions
     */
    renderAvailableTags() {
        const container = document.getElementById('availableTagsList');
        if (!container) return;

        container.innerHTML = '';

        const roomTagIds = this.roomTags.map(t => t.id);

        this.allTags.forEach(tag => {
            if (!roomTagIds.includes(tag.id)) {
                const tagElement = document.createElement('div');
                tagElement.className = 'available-tag-item';
                tagElement.textContent = tag.tag_name;
                tagElement.addEventListener('click', () => {
                    this.addTagToRoom(tag.tag_name);
                });
                container.appendChild(tagElement);
            }
        });
    }

    /**
     * Add a single tag to the room
     */
    async addTagToRoom(tagName) {
        try {
            this.showMessage('Adding tag...', 'loading');

            const response = await fetch(`${this.baseApiUrl}/rooms/${this.roomId}/tags`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tag_name: tagName })
            });

            const data = await response.json();

            if (data.status === 200) {
                this.showMessage(`Tag "${tagName}" added successfully!`, 'success');
                this.loadRoomTags();
                this.loadAvailableTags();
                this.clearTagInput();
            } else {
                this.showMessage(data.error || 'Failed to add tag', 'error');
            }
        } catch (error) {
            console.error('Error adding tag:', error);
            this.showMessage('Error adding tag', 'error');
        }
    }

    /**
     * Remove a tag from the room
     */
    async removeTagFromRoom(tagId) {
        try {
            this.showMessage('Removing tag...', 'loading');

            const response = await fetch(`${this.baseApiUrl}/rooms/${this.roomId}/tags/${tagId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.status === 200) {
                this.showMessage('Tag removed successfully!', 'success');
                this.loadRoomTags();
                this.loadAvailableTags();
            } else {
                this.showMessage(data.error || 'Failed to remove tag', 'error');
            }
        } catch (error) {
            console.error('Error removing tag:', error);
            this.showMessage('Error removing tag', 'error');
        }
    }

    /**
     * Add multiple tags at once
     */
    async addMultipleTags(tagNames) {
        try {
            this.showMessage('Adding tags...', 'loading');

            const response = await fetch(`${this.baseApiUrl}/rooms/${this.roomId}/tags/bulk`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tag_names: tagNames })
            });

            const data = await response.json();

            if (data.status === 200) {
                const message = `Added ${data.results.added.length} tag(s)`;
                this.showMessage(message, 'success');
                this.loadRoomTags();
                this.loadAvailableTags();
                this.clearTagInput();
            } else {
                this.showMessage(data.error || 'Failed to add tags', 'error');
            }
        } catch (error) {
            console.error('Error adding tags:', error);
            this.showMessage('Error adding tags', 'error');
        }
    }

    /**
     * Attach event listeners to tag input and buttons
     */
    attachEventListeners() {
        const addTagBtn = document.getElementById('addTagBtn');
        const tagInput = document.getElementById('tagInput');

        if (addTagBtn) {
            addTagBtn.addEventListener('click', () => {
                const tagName = tagInput?.value.trim();
                if (tagName) {
                    this.addTagToRoom(tagName);
                }
            });
        }

        if (tagInput) {
            tagInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const tagName = tagInput.value.trim();
                    if (tagName) {
                        this.addTagToRoom(tagName);
                    }
                }
            });
        }
    }

    /**
     * Show a message to the user
     */
    showMessage(message, type = 'info') {
        const messageContainer = document.getElementById('tagMessageContainer');
        if (!messageContainer) return;

        messageContainer.innerHTML = `<div class="tag-message ${type}">${this.escapeHtml(message)}</div>`;

        if (type !== 'loading') {
            setTimeout(() => {
                messageContainer.innerHTML = '';
            }, 3000);
        }
    }

    /**
     * Clear the tag input field
     */
    clearTagInput() {
        const tagInput = document.getElementById('tagInput');
        if (tagInput) {
            tagInput.value = '';
        }
    }

    /**
     * Escape HTML special characters to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Get room tags data
     */
    getTags() {
        return this.roomTags;
    }

    /**
     * Refresh room tags
     */
    refresh() {
        this.loadRoomTags();
        this.loadAvailableTags();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const roomIdElement = document.getElementById('roomId');
    if (roomIdElement) {
        const roomId = roomIdElement.value;
        window.tagManager = new SubjectTagManager(roomId);
    }
});
