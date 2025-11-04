<template>
  <div class="settings">
    <div class="settings-container">
      <header class="settings-header">
        <router-link to="/" class="btn-back">← Back</router-link>
        <h1>Settings</h1>
      </header>

      <div class="settings-content">
        <!-- Model Configuration -->
        <section class="settings-section">
          <div class="section-header-with-link">
            <h2>Model Configuration</h2>
            <router-link to="/llm-settings" class="btn-link">
              Manage Providers & Models →
            </router-link>
          </div>
          <p class="section-description">
            Configure AI model providers and manage available models in the
            <router-link to="/llm-settings" class="link">LLM Settings</router-link> page.
          </p>
          <div class="form-group">
            <label for="model">Default LLM Model (Legacy)</label>
            <select
              id="model"
              v-model="settingsStore.model"
              @change="settingsStore.updateModel(settingsStore.model)"
              class="form-control"
            >
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              <option value="gpt-4">GPT-4</option>
              <option value="gpt-4-turbo-preview">GPT-4 Turbo</option>
              <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
              <option value="claude-3-opus-20240229">Claude 3 Opus</option>
              <option value="gemini-pro">Gemini Pro</option>
            </select>
            <p class="help-text">
              This is the legacy model selector. Use the LLM Settings page for full model management.
            </p>
          </div>
        </section>


        <!-- Search API Keys -->
        <section class="settings-section">
          <h2>Search API Keys (Optional)</h2>
          <p class="section-description">
            These are optional. DuckDuckGo works without an API key.
          </p>

          <div class="form-group">
            <label for="bing_key">Bing Search API Key</label>
            <input
              id="bing_key"
              type="password"
              v-model="apiKeys.bing_search_api_key"
              @change="updateKey('bing_search_api_key')"
              placeholder="Optional"
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label for="google_search_key">Google Search API Key</label>
            <input
              id="google_search_key"
              type="password"
              v-model="apiKeys.google_search_api_key"
              @change="updateKey('google_search_api_key')"
              placeholder="Optional"
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label for="google_cse">Google Custom Search Engine ID</label>
            <input
              id="google_cse"
              type="text"
              v-model="apiKeys.google_cse_id"
              @change="updateKey('google_cse_id')"
              placeholder="Optional"
              class="form-control"
            />
          </div>
        </section>

        <!-- Preferences -->
        <section class="settings-section">
          <h2>Preferences</h2>
          
          <div class="form-group-checkbox">
            <label>
              <input
                type="checkbox"
                v-model="settingsStore.streamingEnabled"
                @change="settingsStore.toggleStreaming()"
              />
              <span>Enable streaming responses</span>
            </label>
            <p class="help-text">Stream responses in real-time for faster feedback</p>
          </div>

          <div class="form-group-checkbox">
            <label>
              <input
                type="checkbox"
                v-model="settingsStore.proMode"
                @change="settingsStore.toggleProMode()"
              />
              <span>Enable Pro Mode by default</span>
            </label>
            <p class="help-text">Pro mode searches more sources for comprehensive answers</p>
          </div>
        </section>

        <!-- Info -->
        <section class="settings-section">
          <h2>About</h2>
          <p class="about-text">
            Moplexity is an open-source Perplexity clone that gives you full control over your AI search experience.
          </p>
          <p class="about-text">
            Version: 1.0.0
          </p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '../stores/settings'

const settingsStore = useSettingsStore()
const apiKeys = ref({ ...settingsStore.apiKeys })

onMounted(() => {
  apiKeys.value = { ...settingsStore.apiKeys }
})

function updateKey(key) {
  settingsStore.updateApiKey(key, apiKeys.value[key])
}
</script>

<style scoped>
.settings {
  min-height: 100vh;
  background-color: var(--background);
  padding: 2rem;
}

.settings-container {
  max-width: 800px;
  margin: 0 auto;
}

.settings-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.btn-back {
  padding: 0.5rem 1rem;
  background-color: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  text-decoration: none;
  color: var(--text-primary);
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-back:hover {
  background-color: var(--surface-hover);
  border-color: var(--border-hover);
}

.settings-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.settings-section {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  transition: all 0.2s ease;
}

.settings-section:hover {
  border-color: var(--border-hover);
  box-shadow: var(--shadow);
}

.settings-section h2 {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.section-header-with-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.btn-link {
  padding: 0.5rem 1rem;
  background-color: var(--primary-color);
  color: white;
  text-decoration: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-link:hover {
  background-color: var(--primary-hover);
}

.link {
  color: var(--primary-color);
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.section-description {
  margin: 0 0 1.5rem 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 0.875rem;
  background-color: var(--background);
  color: var(--text-primary);
  transition: all 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  background-color: var(--surface);
}

.form-control::placeholder {
  color: var(--text-muted);
}

.form-group-checkbox {
  margin-bottom: 1.5rem;
}

.form-group-checkbox:last-child {
  margin-bottom: 0;
}

.form-group-checkbox label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
}

.form-group-checkbox input[type="checkbox"] {
  cursor: pointer;
}

.help-text {
  margin: 0.5rem 0 0 1.5rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.about-text {
  margin: 0 0 0.75rem 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.about-text:last-child {
  margin-bottom: 0;
}
</style>

