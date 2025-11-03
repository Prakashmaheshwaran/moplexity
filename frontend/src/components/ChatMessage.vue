<template>
  <div class="chat-message" :class="`message-${message.role}`">
    <div class="message-header">
      <div class="message-avatar">
        {{ message.role === 'user' ? 'U' : 'M' }}
      </div>
      <div class="message-meta">
        <span class="message-role">{{ message.role === 'user' ? 'You' : 'Moplexity' }}</span>
        <span class="message-time">{{ formatTime(message.created_at) }}</span>
      </div>
    </div>
    <div class="message-content">
      <div v-if="message.role === 'user'" class="message-text">
        {{ message.content }}
      </div>
      <div v-else class="message-text markdown-content" v-html="renderedContent"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
})

const renderedContent = computed(() => {
  if (props.message.role === 'assistant') {
    const html = marked(props.message.content)
    return DOMPurify.sanitize(html)
  }
  return props.message.content
})

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  
  return date.toLocaleDateString()
}
</script>

<style scoped>
.chat-message {
  margin-bottom: 2rem;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.message-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.message-user .message-avatar {
  background-color: var(--primary-color);
  color: white;
}

.message-assistant .message-avatar {
  background-color: var(--surface);
  color: var(--primary-color);
  border: 2px solid var(--primary-color);
}

.message-meta {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.message-role {
  font-weight: 600;
  font-size: 0.875rem;
}

.message-time {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.message-content {
  margin-left: 2.75rem;
}

.message-text {
  line-height: 1.8;
  color: var(--text-primary);
}

.message-user .message-text {
  font-size: 1rem;
}

.message-assistant .message-text {
  font-size: 0.9375rem;
}
</style>

