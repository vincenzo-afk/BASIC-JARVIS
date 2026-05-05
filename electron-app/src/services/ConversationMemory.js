/**
 * Conversation Memory Service
 * Manages chat history and context for JARVIS
 */

const STORAGE_KEY = 'jarvis-conversations';
const MAX_CONVERSATIONS = 50;
const MAX_MESSAGES_PER_CONVERSATION = 100;

class ConversationMemory {
    constructor() {
        this.conversations = [];
        this.activeConversationId = null;
        this.load();
    }

    /**
     * Load conversations from localStorage
     */
    load() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {
                const data = JSON.parse(saved);
                this.conversations = data.conversations || [];
                this.activeConversationId = data.activeConversationId;
            }
        } catch (e) {
            console.error('Failed to load conversations:', e);
            this.conversations = [];
        }
    }

    /**
     * Save conversations to localStorage
     */
    save() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
                conversations: this.conversations.slice(0, MAX_CONVERSATIONS),
                activeConversationId: this.activeConversationId
            }));
        } catch (e) {
            console.error('Failed to save conversations:', e);
        }
    }

    /**
     * Create a new conversation
     */
    createConversation(title = 'New Conversation') {
        const conversation = {
            id: Date.now().toString(),
            title,
            messages: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            model: 'llama3.1:8b'
        };

        this.conversations.unshift(conversation);
        this.activeConversationId = conversation.id;
        this.save();

        return conversation;
    }

    /**
     * Get the active conversation or create one
     */
    getActiveConversation() {
        if (!this.activeConversationId) {
            return this.createConversation();
        }

        const conversation = this.conversations.find(c => c.id === this.activeConversationId);
        return conversation || this.createConversation();
    }

    /**
     * Add a message to the active conversation
     */
    addMessage(role, content, metadata = {}) {
        const conversation = this.getActiveConversation();

        const message = {
            id: Date.now().toString(),
            role, // 'user' or 'assistant'
            content,
            timestamp: new Date().toISOString(),
            ...metadata
        };

        conversation.messages.push(message);

        // Keep only recent messages
        if (conversation.messages.length > MAX_MESSAGES_PER_CONVERSATION) {
            conversation.messages = conversation.messages.slice(-MAX_MESSAGES_PER_CONVERSATION);
        }

        // Update title from first user message
        if (role === 'user' && conversation.messages.filter(m => m.role === 'user').length === 1) {
            conversation.title = content.substring(0, 50) + (content.length > 50 ? '...' : '');
        }

        conversation.updatedAt = new Date().toISOString();
        this.save();

        return message;
    }

    /**
     * Get messages for context (last N messages)
     */
    getContext(count = 10) {
        const conversation = this.getActiveConversation();
        return conversation.messages.slice(-count);
    }

    /**
     * Get formatted context for LLM
     */
    getFormattedContext(count = 5) {
        const messages = this.getContext(count * 2); // Get enough for N exchanges

        return messages.map(msg => ({
            role: msg.role,
            content: msg.content
        }));
    }

    /**
     * Switch to a different conversation
     */
    switchConversation(conversationId) {
        const conversation = this.conversations.find(c => c.id === conversationId);
        if (conversation) {
            this.activeConversationId = conversationId;
            this.save();
            return conversation;
        }
        return null;
    }

    /**
     * Delete a conversation
     */
    deleteConversation(conversationId) {
        this.conversations = this.conversations.filter(c => c.id !== conversationId);

        if (this.activeConversationId === conversationId) {
            this.activeConversationId = this.conversations[0]?.id || null;
        }

        this.save();
    }

    /**
     * Clear all conversations
     */
    clearAll() {
        this.conversations = [];
        this.activeConversationId = null;
        this.save();
    }

    /**
     * Search through conversations
     */
    search(query) {
        const lowerQuery = query.toLowerCase();
        const results = [];

        for (const conv of this.conversations) {
            for (const msg of conv.messages) {
                if (msg.content.toLowerCase().includes(lowerQuery)) {
                    results.push({
                        conversationId: conv.id,
                        conversationTitle: conv.title,
                        message: msg,
                        snippet: this.getSnippet(msg.content, lowerQuery)
                    });
                }
            }
        }

        return results;
    }

    /**
     * Get snippet around search term
     */
    getSnippet(text, query, contextLength = 50) {
        const lowerText = text.toLowerCase();
        const index = lowerText.indexOf(query);

        if (index === -1) return text.substring(0, contextLength * 2);

        const start = Math.max(0, index - contextLength);
        const end = Math.min(text.length, index + query.length + contextLength);

        let snippet = text.substring(start, end);
        if (start > 0) snippet = '...' + snippet;
        if (end < text.length) snippet = snippet + '...';

        return snippet;
    }

    /**
     * Export conversations
     */
    export() {
        return JSON.stringify(this.conversations, null, 2);
    }

    /**
     * Import conversations
     */
    import(jsonData) {
        try {
            const imported = JSON.parse(jsonData);
            if (Array.isArray(imported)) {
                this.conversations = [...imported, ...this.conversations].slice(0, MAX_CONVERSATIONS);
                this.save();
                return true;
            }
        } catch (e) {
            console.error('Failed to import conversations:', e);
        }
        return false;
    }
}

// Singleton instance
const conversationMemory = new ConversationMemory();

export default conversationMemory;
export { ConversationMemory };
