<template>
  <div class="home" @mouseleave="handleMouseLeave">
      <!-- Hover Zone for Sidebar -->
      <div 
        class="sidebar-hover-zone"
        @mouseenter="handleSidebarHover"
        @mouseleave="handleSidebarLeave"
      ></div>
      
      <!-- Sidebar -->
      <aside 
        class="sidebar" 
        :class="{ collapsed: !showSidebar, visible: showSidebar }"
        @mouseenter="handleSidebarHover"
        @mouseleave="handleSidebarLeave"
      >
        <SidebarNavigation
          :conversations="conversationStore.conversations"
          :current-id="conversationStore.currentConversation?.id"
          :collapsed="!showSidebar"
          @select-conversation="loadConversation"
          @delete-conversation="deleteConversation"
          @new-thread="startNewChat"
        />
      </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Minimal Header -->
      <header class="header">
        <div class="header-content">
        </div>
      </header>

      <!-- Chat Area -->
      <div class="chat-container">
        <!-- Welcome Screen with Centered Search -->
        <div v-if="conversationStore.messages.length === 0" class="welcome-screen">
          <div class="welcome-content">
            <img src="/logo.svg" alt="Moplexity Logo" class="welcome-logo" />
            <h1 class="welcome-title-animated">Moplexity</h1>
            <p class="welcome-subtitle">Open Knowledge should not be 20$/month</p>
            
            <!-- Centered Search Bar -->
            <div class="welcome-search">
              <SearchBar
                :disabled="conversationStore.loading || conversationStore.streaming"
                :model-value="selectedModelId"
                :selected-sources="selectedSources"
                @submit="handleSearch"
                @update:model-value="selectedModelId = $event"
                @update:selected-sources="selectedSources = $event"
                class="welcome-search-bar"
              />
            </div>

            <!-- Quick Suggestions -->
            <div class="quick-suggestions">
              <button
                v-for="suggestion in quickSuggestions"
                :key="suggestion"
                @click="handleSearch(suggestion)"
                class="suggestion-btn"
              >
                {{ suggestion }}
              </button>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <div v-else class="messages-container">
          <!-- Sources Section at Top -->
          <div v-if="conversationStore.sources.length > 0" class="sources-section-top">
            <div class="sources-header-grouped">
              <h3 class="sources-title">Sources</h3>
              <details class="sources-details-grouped">
                <summary class="sources-summary">
                  <span>View All ({{ conversationStore.sources.length }})</span>
                </summary>
                <div class="sources-grouped">
                  <div v-for="(group, category) in groupedSources" :key="category" class="source-category-group">
                    <h4 class="category-title">{{ category }}</h4>
                    <div class="sources-grid">
                      <SourceCard
                        v-for="(source, index) in group"
                        :key="source.id || `source-${category}-${index}`"
                        :source="source"
                        :index="getSourceIndex(source)"
                      />
                    </div>
                  </div>
                </div>
              </details>
            </div>
          </div>
          
          <div class="messages">
            <ChatMessage
              v-for="message in conversationStore.messages"
              :key="message.id"
              :message="message"
              @follow-up-click="handleSearch"
            />
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="conversationStore.loading || conversationStore.streaming" class="loading-indicator">
          <div class="loading-spinner"></div>
          <span>{{ conversationStore.streaming ? 'Generating response...' : 'Searching...' }}</span>
        </div>

        <!-- Error Message -->
        <div v-if="conversationStore.error" class="error-message">
          {{ conversationStore.error }}
        </div>
      </div>

      <!-- Bottom Search Bar (when messages exist) -->
      <div v-if="conversationStore.messages.length > 0" class="search-container">
        <SearchBar
          :disabled="conversationStore.loading || conversationStore.streaming"
          :model-value="selectedModelId"
          :selected-sources="selectedSources"
          @submit="handleSearch"
          @update:model-value="selectedModelId = $event"
          @update:selected-sources="selectedSources = $event"
          class="search-bar"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useConversationStore } from '../stores/conversation'
import { useSettingsStore as useSettingsStoreLocal } from '../stores/settings'
import SearchBar from '../components/SearchBar.vue'
import ChatMessage from '../components/ChatMessage.vue'
import SourceCard from '../components/SourceCard.vue'
import SidebarNavigation from '../components/SidebarNavigation.vue'

const conversationStore = useConversationStore()
const settingsStore = useSettingsStoreLocal()
const showSidebar = ref(false) // Sidebar hidden by default
const selectedModelId = ref(null)
const selectedSources = ref(settingsStore.defaultFocusSources && settingsStore.defaultFocusSources.length ? settingsStore.defaultFocusSources : ['web'])
const quickSuggestions = ref([])
let sidebarHoverTimeout = null

function handleSidebarHover() {
  if (sidebarHoverTimeout) {
    clearTimeout(sidebarHoverTimeout)
    sidebarHoverTimeout = null
  }
  showSidebar.value = true
}

function handleSidebarLeave() {
  sidebarHoverTimeout = setTimeout(() => {
    showSidebar.value = false
  }, 300) // Small delay to prevent flickering
}

function handleMouseLeave() {
  // Hide sidebar when mouse leaves the entire home area
  if (sidebarHoverTimeout) {
    clearTimeout(sidebarHoverTimeout)
  }
  showSidebar.value = false
}

// Load last used model from localStorage
onMounted(async () => {
  conversationStore.fetchConversations()
  
  // Load last used model
  const lastModelId = localStorage.getItem('lastUsedModelId')
  if (lastModelId) {
    selectedModelId.value = parseInt(lastModelId)
  } else {
    // Try to get first available model
    try {
      const response = await fetch('/api/llm/models/active')
      if (response.ok) {
        const models = await response.json()
        if (models.length > 0) {
          selectedModelId.value = models[0].id
          localStorage.setItem('lastUsedModelId', models[0].id.toString())
        }
      }
    } catch (error) {
      console.error('Error fetching models:', error)
    }
  }
  
  // Load AI-generated suggestions
  loadAISuggestions()
})

async function loadAISuggestions() {
  try {
    const response = await fetch('/api/chat/suggestions')
    if (response.ok) {
      const data = await response.json()
      quickSuggestions.value = data.suggestions || []
    }
  } catch (error) {
    console.error('Error loading suggestions:', error)
    // Fallback to default suggestions
    quickSuggestions.value = [
      'What is artificial intelligence?',
      'Latest developments in quantum computing',
      'How does blockchain work?',
      'Climate change solutions'
    ]
  }
}

async function handleSearch(query) {
  // Save selected model to localStorage
  if (selectedModelId.value) {
    localStorage.setItem('lastUsedModelId', selectedModelId.value.toString())
  }
  
  // Use first selected source as focus mode (for backward compatibility)
  // TODO: Update backend to accept multiple sources
  const focusModes = selectedSources.value.length > 0 ? selectedSources.value : ['web']
  
  if (settingsStore.streamingEnabled) {
    await conversationStore.sendMessageStreaming(query, settingsStore.proMode, selectedModelId.value, focusModes)
  } else {
    await conversationStore.sendMessage(query, settingsStore.proMode, selectedModelId.value, focusModes)
  }
}

async function loadConversation(id) {
  await conversationStore.fetchConversation(id)
  // Set selected model from the conversation first, then fallback to last used
  const conversationModelId = conversationStore.currentConversation?.selected_model_id
  if (conversationModelId) {
    selectedModelId.value = conversationModelId
    localStorage.setItem('lastUsedModelId', conversationModelId.toString())
  } else {
    // Fallback to last used model
    const lastModelId = localStorage.getItem('lastUsedModelId')
    if (lastModelId) {
      selectedModelId.value = parseInt(lastModelId)
    }
  }
  
  // Load sources from conversation if available (future enhancement)
  // For now, default to web
  selectedSources.value = settingsStore.defaultFocusSources && settingsStore.defaultFocusSources.length ? settingsStore.defaultFocusSources : ['web']
}

async function deleteConversation(id) {
  if (confirm('Are you sure you want to delete this conversation?')) {
    await conversationStore.deleteConversation(id)
  }
}

function startNewChat() {
  conversationStore.resetConversation()
  selectedModelId.value = null
  selectedSources.value = settingsStore.defaultFocusSources && settingsStore.defaultFocusSources.length ? settingsStore.defaultFocusSources : ['web']
}

// Group sources by category
const groupedSources = computed(() => {
  const groups = {}
  conversationStore.sources.forEach(source => {
    const category = getSourceCategory(source.source_type)
    if (!groups[category]) {
      groups[category] = []
    }
    groups[category].push(source)
  })
  return groups
})

function getSourceCategory(sourceType) {
  // Map all social media sources to 'Social'
  const socialTypes = ['reddit', 'youtube', 'linkedin', 'twitter', 'github', 'social']
  if (socialTypes.includes(sourceType)) {
    return 'Social'
  }
  
  const categoryMap = {
    'web': 'Web',
    'academic': 'Academic Papers'
  }
  return categoryMap[sourceType] || 'Web'
}

function getSourceIndex(source) {
  // Find the index of this source in the original sources array
  const index = conversationStore.sources.findIndex(s => 
    s.id === source.id || 
    (s.url === source.url && s.title === source.title)
  )
  return index >= 0 ? index + 1 : 1
}
</script>

<style scoped>
.home {
  display: flex;
  height: 100vh;
  background-color: var(--surface);
  position: relative;
}

.sidebar-hover-zone {
  position: fixed;
  left: 0;
  top: 0;
  width: 20px;
  height: 100vh;
  z-index: 9;
  background: transparent;
  pointer-events: auto;
}

.sidebar {
  width: 260px;
  flex-shrink: 0;
  transition: transform 0.3s ease, width 0.3s ease, box-shadow 0.3s ease;
  z-index: 10;
  overflow: hidden;
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  transform: translateX(-100%);
  background: var(--surface);
  border-right: 1px solid var(--border);
  pointer-events: auto;
}

.sidebar.visible {
  transform: translateX(0);
  box-shadow: var(--shadow-xl);
}

.sidebar.collapsed {
  width: 60px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-left: 0;
  transition: margin-left 0.3s ease;
}

.header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 1rem;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.header-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 1rem;
}


.btn-settings {
  padding: 0.5rem 1rem;
  background-color: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  text-decoration: none;
  color: var(--text-primary);
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-settings:hover {
  background-color: var(--surface-hover);
  border-color: var(--border-hover);
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  position: relative;
}

/* Welcome Screen - Perplexity Style */
.welcome-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: 2rem 1rem;
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.welcome-content {
  width: 100%;
  max-width: 900px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.welcome-logo {
  width: 80px;
  height: 80px;
  animation: fadeIn 0.4s ease, slideUp 0.5s ease;
  filter: drop-shadow(0 4px 12px rgba(99, 102, 241, 0.3));
  transition: transform 0.3s ease;
}

.welcome-logo:hover {
  transform: scale(1.05) rotate(5deg);
}

.welcome-title-animated {
  font-size: 3.5rem;
  font-weight: 700;
  background: linear-gradient(90deg, var(--primary-color), #8b5cf6, var(--primary-color));
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 1rem 0;
  text-align: center;
  animation: slideUp 0.5s ease, gradientShift 3s ease infinite;
  letter-spacing: -0.02em;
}

@keyframes gradientShift {
  0%, 100% {
    background-position: 0% center;
  }
  50% {
    background-position: 100% center;
  }
}

.welcome-subtitle {
  font-size: 1.5rem;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
  text-align: center;
  animation: slideUp 0.6s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-search {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  animation: slideUp 0.6s ease;
}

.welcome-search-bar {
  width: 100%;
  max-width: 800px;
}

.quick-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
  max-width: 800px;
  animation: slideUp 0.7s ease;
}

.suggestion-btn {
  padding: 0.5rem 1rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.suggestion-btn:hover {
  background: var(--surface-hover);
  border-color: var(--border-hover);
  color: var(--text-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.messages-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1rem;
  animation: fadeIn 0.4s var(--ease-out-cubic);
}

.messages {
  margin-bottom: 3rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.sources-section-top {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
  animation: fadeInDown 0.4s var(--ease-out-cubic);
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.sources-header-grouped {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sources-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.sources-grouped {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1rem;
}

.source-category-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.category-title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sources-details {
  border-top: 1px solid var(--border);
  padding-top: 1rem;
}

.sources-summary {
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  list-style: none;
  padding: 0.5rem 0;
  transition: all var(--transition-base);
  user-select: none;
}

.sources-summary:hover {
  color: var(--primary-color);
  transform: translateX(4px);
}

.sources-summary::-webkit-details-marker {
  display: none;
}

.sources-summary::before {
  content: '▶';
  display: inline-block;
  margin-right: 0.5rem;
  transition: transform 0.2s;
  font-size: 0.75rem;
}

.sources-details[open] .sources-summary::before {
  transform: rotate(90deg);
}

.sources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.75rem;
}

.sources-details-grouped {
  margin-top: 0.5rem;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
  animation: fadeIn 0.3s ease;
}

.error-message {
  max-width: 800px;
  margin: 1rem auto;
  padding: 1rem;
  background-color: #dc2626;
  color: #ffffff;
  border-radius: var(--radius);
  text-align: center;
  border: 1px solid #ef4444;
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

.search-container {
  padding: 1.5rem;
  background: var(--surface);
  border-top: 1px solid var(--border);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  position: sticky;
  bottom: 0;
  z-index: 5;
}

.search-inputs {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 900px;
  margin: 0 auto;
}

.search-bar {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100%;
    z-index: 1000;
    box-shadow: var(--shadow-xl);
    transform: translateX(0);
  }

  .welcome-title-animated {
    font-size: 2.5rem;
  }

  .welcome-search {
    gap: 1rem;
  }

  .sources-grid {
    grid-template-columns: 1fr;
  }

  .messages-container {
    padding: 1rem 0.75rem;
  }
}
</style>

