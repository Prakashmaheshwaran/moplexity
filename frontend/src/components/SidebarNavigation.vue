<template>
  <div class="sidebar-navigation" :class="{ collapsed: collapsed }">
    <!-- Top Navigation -->
    <nav class="nav-top">
      <button
        @click="navigate('home')"
        class="nav-item"
        :class="{ active: currentRoute === 'home' }"
        :title="collapsed ? 'Home' : ''"
      >
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
          <polyline points="9 22 9 12 15 12 15 22"></polyline>
        </svg>
        <span class="nav-label" v-if="!collapsed">Home</span>
      </button>
    </nav>

    <!-- New Thread Button -->
    <div class="nav-new-thread">
      <button @click="$emit('new-thread')" class="btn-new-thread" :title="collapsed ? 'New Thread' : ''">
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span v-if="!collapsed">New Thread</span>
      </button>
    </div>

    <!-- Conversation History -->
    <div class="conversation-history" v-if="!collapsed">
      <div class="history-header">
        <h3>Recent Conversations</h3>
      </div>
      <div class="history-list">
        <div
          v-for="conversation in conversations"
          :key="conversation.id"
          class="history-item"
          :class="{ active: conversation.id === currentId }"
          @click="$emit('select-conversation', conversation.id)"
        >
          <div class="history-item-info">
            <h4 class="history-item-title">{{ conversation.title }}</h4>
            <span class="history-item-time">{{ formatTime(conversation.updated_at) }}</span>
          </div>
          <button
            @click.stop="$emit('delete-conversation', conversation.id)"
            class="history-item-delete"
            title="Delete"
          >
            ×
          </button>
        </div>
        <div v-if="conversations.length === 0" class="history-empty">
          <p>No conversations yet</p>
        </div>
      </div>
    </div>

    <!-- Profile/Settings at Bottom -->
    <div class="nav-bottom">
      <button @click="showSettings = !showSettings" class="nav-profile" :title="collapsed ? 'Profile' : ''">
        <div class="profile-avatar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
        </div>
        <span class="profile-name" v-if="!collapsed">Profile</span>
        <svg v-if="!collapsed" class="profile-arrow" :class="{ rotated: showSettings }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>

      <!-- Settings Dropdown -->
      <div v-if="showSettings && !collapsed" class="settings-dropdown">
        <router-link to="/settings" class="settings-item" @click="showSettings = false">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M12 1v6m0 6v6m9-9h-6m-6 0H3"></path>
          </svg>
          <span>Settings</span>
        </router-link>
        <router-link to="/llm-settings" class="settings-item" @click="showSettings = false">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
            <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
          </svg>
          <span>LLM Settings</span>
        </router-link>
      </div>
      
      <!-- Collapsed Settings Icon -->
      <div v-if="collapsed" class="collapsed-settings">
        <router-link to="/settings" class="collapsed-nav-item" title="Settings">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M12 1v6m0 6v6m9-9h-6m-6 0H3"></path>
          </svg>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  conversations: {
    type: Array,
    default: () => []
  },
  currentId: {
    type: Number,
    default: null
  },
  collapsed: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select-conversation', 'delete-conversation', 'new-thread'])

const route = useRoute()
const router = useRouter()
const showSettings = ref(false)
const showLibrary = ref(false)

const currentRoute = computed(() => {
  if (route.path === '/') return 'home'
  return 'home'
})

function navigate(routeName) {
  if (routeName === 'home') {
    router.push('/')
  }
}

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
.sidebar-navigation {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--surface);
  padding: 1rem 0.5rem;
  transition: all 0.3s ease;
}

.sidebar-navigation.collapsed {
  padding: 1rem 0.25rem;
  align-items: center;
}

.nav-top {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius);
  transition: all 0.2s ease;
  font-size: 0.9375rem;
  text-align: left;
}

.nav-item:hover {
  background: var(--surface-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--surface-hover);
  color: var(--primary-color);
  font-weight: 500;
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-label {
  flex: 1;
}

.sidebar-navigation.collapsed .nav-label {
  display: none;
}

.sidebar-navigation.collapsed .nav-item {
  justify-content: center;
  padding: 0.75rem;
  width: 100%;
}

.nav-new-thread {
  padding: 0.5rem 0;
  margin-bottom: 1rem;
}

.btn-new-thread {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}

.btn-new-thread::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.btn-new-thread:active::before {
  width: 300px;
  height: 300px;
}

.sidebar-navigation.collapsed .btn-new-thread {
  padding: 0.75rem;
}

.sidebar-navigation.collapsed .btn-new-thread span {
  display: none;
}

.btn-new-thread:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.btn-new-thread:active {
  transform: translateY(0);
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.conversation-history {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-top: 1rem;
}

.history-header {
  padding: 0.5rem 1rem;
  margin-bottom: 0.5rem;
}

.history-header h3 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.25rem;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  margin-bottom: 0.25rem;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}

.history-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--primary-color);
  transform: scaleX(0);
  transition: transform var(--transition-base);
}

.history-item:hover {
  background: var(--surface-hover);
  transform: translateX(4px);
}

.history-item:hover::before {
  transform: scaleX(1);
}

.history-item.active {
  background: var(--surface-hover);
  border-left: 3px solid var(--primary-color);
}

.history-item-info {
  flex: 1;
  min-width: 0;
}

.history-item-title {
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-item-time {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.history-item-delete {
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

.history-item:hover .history-item-delete {
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-item-delete:hover {
  background: rgba(220, 38, 38, 0.1);
  color: #ef4444;
}

.history-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.nav-bottom {
  position: relative;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

.nav-profile {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius);
  transition: all 0.2s ease;
  font-size: 0.9375rem;
}

.nav-profile:hover {
  background: var(--surface-hover);
  color: var(--text-primary);
}

.profile-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--surface-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.profile-avatar svg {
  width: 18px;
  height: 18px;
  color: var(--text-primary);
}

.profile-name {
  flex: 1;
  text-align: left;
}

.sidebar-navigation.collapsed .profile-name {
  display: none;
}

.sidebar-navigation.collapsed .nav-profile {
  justify-content: center;
  padding: 0.75rem;
  width: 100%;
}

.collapsed-settings {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 0.5rem;
}

.collapsed-nav-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  border-radius: var(--radius);
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.collapsed-nav-item:hover {
  background: var(--surface-hover);
  color: var(--text-primary);
}

.collapsed-nav-item svg {
  width: 20px;
  height: 20px;
}

.profile-arrow {
  width: 16px;
  height: 16px;
  transition: transform 0.2s ease;
}

.profile-arrow.rotated {
  transform: rotate(180deg);
}

.settings-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  margin-bottom: 0.5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  animation: slideUpScale 0.2s cubic-bezier(0.33, 1, 0.68, 1);
  transform-origin: bottom;
}

@keyframes slideUpScale {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.settings-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: var(--text-primary);
  text-decoration: none;
  transition: all 0.2s ease;
  font-size: 0.9375rem;
}

.settings-item:hover {
  background: var(--surface-hover);
}

.settings-item svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

/* Scrollbar styling for history list */
.history-list::-webkit-scrollbar {
  width: 6px;
}

.history-list::-webkit-scrollbar-track {
  background: transparent;
}

.history-list::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}

.history-list::-webkit-scrollbar-thumb:hover {
  background: var(--border-hover);
}
</style>

