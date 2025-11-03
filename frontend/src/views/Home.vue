<template>
  <div class="home">
    <!-- Sidebar -->
    <aside class="sidebar" v-if="showSidebar">
      <ConversationList
        :conversations="conversationStore.conversations"
        :current-id="conversationStore.currentConversation?.id"
        @select="loadConversation"
        @delete="deleteConversation"
        @new-chat="startNewChat"
      />
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Header -->
      <header class="header">
        <div class="header-content">
          <button @click="showSidebar = !showSidebar" class="btn-toggle-sidebar">
            ☰
          </button>
          <h1 class="logo">Moplexity</h1>
          <div class="header-actions">
            <label class="pro-mode-toggle">
              <input
                type="checkbox"
                v-model="settingsStore.proMode"
                @change="settingsStore.toggleProMode()"
              />
              <span>Pro Mode</span>
            </label>
            <router-link to="/settings" class="btn-settings">
              ⚙️ Settings
            </router-link>
          </div>
        </div>
      </header>

      <!-- Chat Area -->
      <div class="chat-container">
        <!-- Welcome Screen -->
        <div v-if="conversationStore.messages.length === 0" class="welcome">
          <h2>Welcome to Moplexity</h2>
          <p>Ask me anything and I'll search the web to find accurate answers.</p>
          <div class="welcome-features">
            <div class="feature">
              <span class="feature-icon">🔍</span>
              <span>Multi-source search</span>
            </div>
            <div class="feature">
              <span class="feature-icon">📺</span>
              <span>YouTube transcripts</span>
            </div>
            <div class="feature">
              <span class="feature-icon">💬</span>
              <span>Reddit discussions</span>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <div v-else class="messages-container">
          <div class="messages">
            <ChatMessage
              v-for="message in conversationStore.messages"
              :key="message.id"
              :message="message"
            />
          </div>

          <!-- Sources -->
          <div v-if="conversationStore.sources.length > 0" class="sources-section">
            <h3>Sources</h3>
            <div class="sources-grid">
              <SourceCard
                v-for="(source, index) in conversationStore.sources"
                :key="index"
                :source="source"
                :index="index + 1"
              />
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="conversationStore.error" class="error-message">
          {{ conversationStore.error }}
        </div>
      </div>

      <!-- Search Bar -->
      <div class="search-container">
        <ModelSelector
          v-model="selectedModelId"
          class="model-selector"
        />
        <SearchBar
          :disabled="conversationStore.loading || conversationStore.streaming"
          @submit="handleSearch"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useConversationStore } from '../stores/conversation'
import { useSettingsStore } from '../stores/settings'
import SearchBar from '../components/SearchBar.vue'
import ChatMessage from '../components/ChatMessage.vue'
import SourceCard from '../components/SourceCard.vue'
import ConversationList from '../components/ConversationList.vue'
import ModelSelector from '../components/ModelSelector.vue'

const conversationStore = useConversationStore()
const settingsStore = useSettingsStore()
const showSidebar = ref(true)
const selectedModelId = ref(null)

onMounted(() => {
  conversationStore.fetchConversations()
})

async function handleSearch(query) {
  if (settingsStore.streamingEnabled) {
    await conversationStore.sendMessageStreaming(query, settingsStore.proMode, selectedModelId.value)
  } else {
    await conversationStore.sendMessage(query, settingsStore.proMode, selectedModelId.value)
  }
}

async function loadConversation(id) {
  await conversationStore.fetchConversation(id)
  // Set selected model from the conversation
  selectedModelId.value = conversationStore.currentConversation?.selected_model_id || null
}

async function deleteConversation(id) {
  if (confirm('Are you sure you want to delete this conversation?')) {
    await conversationStore.deleteConversation(id)
  }
}

function startNewChat() {
  conversationStore.resetConversation()
}
</script>

<style scoped>
.home {
  display: flex;
  height: 100vh;
  background-color: var(--surface);
}

.sidebar {
  width: 280px;
  flex-shrink: 0;
  transition: transform 0.3s;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  background: white;
  border-bottom: 1px solid var(--border);
  padding: 1rem;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-toggle-sidebar {
  padding: 0.5rem;
  background: transparent;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: background-color 0.2s;
}

.btn-toggle-sidebar:hover {
  background-color: var(--surface);
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

.pro-mode-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
}

.pro-mode-toggle input {
  cursor: pointer;
}

.btn-settings {
  padding: 0.5rem 1rem;
  background-color: var(--surface);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  text-decoration: none;
  color: var(--text-primary);
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-settings:hover {
  background-color: var(--border);
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 1rem;
}

.welcome {
  max-width: 800px;
  margin: 4rem auto;
  text-align: center;
}

.welcome h2 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: var(--primary-color);
}

.welcome p {
  font-size: 1.125rem;
  color: var(--text-secondary);
  margin-bottom: 3rem;
}

.welcome-features {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.feature {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem;
  background: white;
  border-radius: 0.75rem;
  border: 1px solid var(--border);
  min-width: 150px;
}

.feature-icon {
  font-size: 2rem;
}

.messages-container {
  max-width: 900px;
  margin: 0 auto;
}

.messages {
  margin-bottom: 3rem;
}

.sources-section {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border);
}

.sources-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.sources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.error-message {
  max-width: 800px;
  margin: 1rem auto;
  padding: 1rem;
  background-color: #fee2e2;
  color: #991b1b;
  border-radius: 0.5rem;
  text-align: center;
}

.search-container {
  padding: 1.5rem;
  background: white;
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.model-selector {
  align-self: flex-start;
}

@media (max-width: 768px) {
  .sidebar {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    z-index: 1000;
    box-shadow: var(--shadow-lg);
  }

  .sources-grid {
    grid-template-columns: 1fr;
  }
}
</style>

