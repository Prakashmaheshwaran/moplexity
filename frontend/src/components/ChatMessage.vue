<template>
  <div class="chat-message" :class="`message-${message.role}`">
    <div class="message-header">
      <div class="message-avatar">
        {{ message.role === 'user' ? 'U' : 'A' }}
      </div>
      <div class="message-meta">
        <span class="message-role">{{ message.role === 'user' ? 'You' : 'AI' }}</span>
        <span class="message-time">{{ formatTime(message.created_at) }}</span>
      </div>
    </div>
    <div class="message-content">
      <div v-if="message.role === 'user'" class="message-text">
        {{ message.content }}
      </div>
      <div v-else>
        <div class="message-text markdown-content" v-html="renderedContent"></div>
        
        <!-- Follow-up Questions -->
        <div v-if="message.follow_up_questions && message.follow_up_questions.length > 0" class="follow-up-questions">
          <div class="follow-up-header">Explore more:</div>
          <div class="follow-up-list">
            <button
              v-for="(question, index) in message.follow_up_questions"
              :key="index"
              @click="$emit('follow-up-click', question)"
              class="follow-up-btn"
            >
              {{ question }}
            </button>
          </div>
        </div>
      </div>
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

const emit = defineEmits(['follow-up-click'])

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
  animation: fadeInUp 0.4s var(--ease-out-cubic);
  opacity: 0;
  animation-fill-mode: forwards;
}

.chat-message:nth-child(1) { animation-delay: 0.05s; }
.chat-message:nth-child(2) { animation-delay: 0.1s; }
.chat-message:nth-child(3) { animation-delay: 0.15s; }
.chat-message:nth-child(4) { animation-delay: 0.2s; }
.chat-message:nth-child(5) { animation-delay: 0.25s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
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

.follow-up-questions {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
}

.follow-up-header {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.75rem;
}

.follow-up-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.follow-up-btn {
  text-align: left;
  padding: 0.75rem 1rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-base);
  transform: translateX(0);
  position: relative;
  overflow: hidden;
}

.follow-up-btn::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 3px;
  background: var(--primary-color);
  transform: scaleY(0);
  transition: transform var(--transition-base);
}

.follow-up-btn:hover {
  background: var(--surface-hover);
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.follow-up-btn:hover::before {
  transform: scaleY(1);
}
</style>

