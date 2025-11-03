<template>
  <div class="conversation-list">
    <div class="list-header">
      <h3>Conversations</h3>
      <button @click="$emit('new-chat')" class="btn-new-chat">
        + New
      </button>
    </div>
    <div class="list-content">
      <div
        v-for="conversation in conversations"
        :key="conversation.id"
        class="conversation-item"
        :class="{ active: conversation.id === currentId }"
        @click="$emit('select', conversation.id)"
      >
        <div class="conversation-info">
          <h4 class="conversation-title">{{ conversation.title }}</h4>
          <span class="conversation-time">{{ formatTime(conversation.updated_at) }}</span>
        </div>
        <button
          @click.stop="$emit('delete', conversation.id)"
          class="btn-delete"
          title="Delete conversation"
        >
          ×
        </button>
      </div>
      <div v-if="conversations.length === 0" class="empty-state">
        <p>No conversations yet</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  conversations: {
    type: Array,
    default: () => []
  },
  currentId: {
    type: Number,
    default: null
  }
})

defineEmits(['select', 'delete', 'new-chat'])

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`
  
  return date.toLocaleDateString()
}
</script>

<style scoped>
.conversation-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-right: 1px solid var(--border);
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid var(--border);
}

.list-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.btn-new-chat {
  padding: 0.5rem 0.75rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-new-chat:hover {
  background-color: var(--primary-hover);
}

.list-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.conversation-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  margin-bottom: 0.25rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.conversation-item:hover {
  background-color: var(--surface);
}

.conversation-item.active {
  background-color: var(--surface);
  border-left: 3px solid var(--primary-color);
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-time {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.btn-delete {
  display: none;
  width: 1.5rem;
  height: 1.5rem;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  font-size: 1.5rem;
  line-height: 1;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.conversation-item:hover .btn-delete {
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-delete:hover {
  background-color: #fee2e2;
  color: #991b1b;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.875rem;
}
</style>

