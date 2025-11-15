<template>
  <div class="settings">
    <div class="settings-container">
      <header class="settings-header">
        <router-link to="/" class="btn-back">← Back</router-link>
        <h1>Settings</h1>
      </header>

      <div class="settings-content">
        <!-- Model Management -->
        <section class="settings-section">
          <div class="section-header-with-link">
            <h2>Model Management</h2>
            <button @click="showModelForm = true" class="btn-link">Add Model</button>
          </div>
          <p class="section-description">
            Configure AI models used by the assistant. Mutations require an Admin Token if configured server-side.
          </p>
          <div v-if="models.length === 0" class="empty-state">
            <p>No models configured yet. Add models to start using AI features.</p>
          </div>
          <div class="models-list">
            <div
              v-for="model in models"
              :key="model.id"
              class="model-card"
              :class="{ 'inactive': !model.is_active }"
            >
              <div class="model-info">
                <h3>{{ model.model_name }}</h3>
                <p v-if="model.provider_type" class="model-provider-type">Provider: {{ model.provider_type }}</p>
                <p v-if="model.base_url" class="model-base-url">Base URL: {{ model.base_url }}</p>
                <div class="model-status">
                  <span :class="model.is_active ? 'status-active' : 'status-inactive'">
                    {{ model.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
              </div>
              <div class="model-actions">
                <button @click="editModel(model)" class="btn-secondary">Edit</button>
                <button @click="deleteModel(model.id)" class="btn-danger">Delete</button>
              </div>
            </div>
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

          <div class="form-group">
            <label>Default Focus Sources</label>
            <div class="focus-source-list">
              <label class="checkbox-inline">
                <input type="checkbox" :checked="defaultSourcesSet.has('web')" @change="toggleDefaultSource('web', $event)" />
                Web
              </label>
              <label class="checkbox-inline">
                <input type="checkbox" :checked="defaultSourcesSet.has('social')" @change="toggleDefaultSource('social', $event)" />
                Social
              </label>
              <label class="checkbox-inline">
                <input type="checkbox" :checked="defaultSourcesSet.has('academic')" @change="toggleDefaultSource('academic', $event)" />
                Academic
              </label>
            </div>
            <p class="help-text">Used as initial sources in the chat page.</p>
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

        <!-- Security -->
        <section class="settings-section">
          <h2>Security</h2>
          <div class="form-group">
            <label for="admin-token">Admin Token (for model management)</label>
            <input id="admin-token" type="password" v-model="adminToken" @change="updateAdminToken" class="form-control" placeholder="Optional" />
            <p class="help-text">If the server configures ADMIN_TOKEN, this token is required for adding, editing, or deleting models.</p>
          </div>
        </section>
      </div>
    </div>
  </div>
      <!-- Model Form Modal -->
      <div v-if="showModelForm" class="modal-overlay" @click="closeModelForm">
        <div class="modal-content" @click.stop>
          <h3>{{ editingModel ? 'Edit Model' : 'Add Model' }}</h3>
          <form @submit.prevent="saveModel" class="model-form">
            <div class="form-group">
              <label for="model-name">Model Name:</label>
              <input id="model-name" v-model="modelForm.model_name" type="text" required placeholder="provider/model or model name" @input="autoInferProviderType" />
              <small class="form-hint">Full model identifier (provider/model or just model name)</small>
            </div>
            <div class="form-group">
              <label for="model-api-key">API Key:</label>
              <input id="model-api-key" v-model="modelForm.api_key" type="password" required placeholder="Enter API key" />
            </div>
            <div class="form-group">
              <label for="model-base-url">Base URL (optional):</label>
              <input id="model-base-url" v-model="modelForm.base_url" type="url" placeholder="e.g., http://localhost:11434" />
              <small class="form-hint">For custom endpoints like Ollama or self-hosted models</small>
            </div>
            <div class="form-group">
              <label for="model-provider-type">Provider Type (optional):</label>
              <input id="model-provider-type" v-model="modelForm.provider_type" type="text" placeholder="Auto-filled from model name" />
              <small class="form-hint">Will be inferred from model name if not specified</small>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="modelForm.is_active" />
                Active
              </label>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeModelForm" class="btn-secondary">Cancel</button>
              <button type="submit" class="btn-primary">{{ editingModel ? 'Update' : 'Add' }} Model</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useSettingsStore } from '../stores/settings'

const settingsStore = useSettingsStore()
const apiKeys = ref({ ...settingsStore.apiKeys })
const adminToken = ref(settingsStore.adminToken || '')

// Default sources management
const defaultSourcesSet = computed(() => new Set(settingsStore.defaultFocusSources))
function toggleDefaultSource(source, event) {
  const current = new Set(settingsStore.defaultFocusSources)
  if (event.target.checked) current.add(source)
  else current.delete(source)
  settingsStore.updateDefaultFocusSources([...current])
}

// Model management state
const models = ref([])
const showModelForm = ref(false)
const editingModel = ref(null)
const modelForm = ref({
  model_name: '',
  api_key: '',
  base_url: '',
  provider_type: '',
  is_active: true
})

function autoInferProviderType() {
  const modelName = modelForm.value.model_name
  if (modelName && modelName.includes('/') && !modelForm.value.provider_type) {
    modelForm.value.provider_type = modelName.split('/')[0]
  }
}

async function fetchModels() {
  try {
    const response = await fetch('/api/llm/models')
    if (response.ok) {
      models.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching models:', error)
  }
}

async function saveModel() {
  try {
    const url = editingModel.value ? `/api/llm/models/${editingModel.value.id}` : '/api/llm/models'
    const method = editingModel.value ? 'PUT' : 'POST'
    const payload = {
      model_name: modelForm.value.model_name,
      api_key: modelForm.value.api_key,
      is_active: modelForm.value.is_active
    }
    if (modelForm.value.base_url) payload.base_url = modelForm.value.base_url
    if (modelForm.value.provider_type) payload.provider_type = modelForm.value.provider_type

    const headers = { 'Content-Type': 'application/json' }
    if (settingsStore.adminToken) headers['Authorization'] = `Bearer ${settingsStore.adminToken}`

    const response = await fetch(url, { method, headers, body: JSON.stringify(payload) })
    if (response.ok) {
      await fetchModels()
      closeModelForm()
    } else {
      const error = await response.json().catch(() => ({}))
      alert(`Error: ${error.detail || 'Failed to save model'}`)
    }
  } catch (error) {
    console.error('Error saving model:', error)
    alert('Failed to save model')
  }
}

async function deleteModel(id) {
  if (!confirm('Are you sure you want to delete this model?')) return
  try {
    const headers = {}
    if (settingsStore.adminToken) headers['Authorization'] = `Bearer ${settingsStore.adminToken}`
    const response = await fetch(`/api/llm/models/${id}`, { method: 'DELETE', headers })
    if (response.ok) {
      await fetchModels()
    } else {
      alert('Failed to delete model')
    }
  } catch (error) {
    console.error('Error deleting model:', error)
    alert('Failed to delete model')
  }
}

function editModel(model) {
  editingModel.value = model
  modelForm.value = {
    model_name: model.model_name || '',
    api_key: '',
    base_url: model.base_url || '',
    provider_type: model.provider_type || '',
    is_active: model.is_active !== undefined ? model.is_active : true
  }
  showModelForm.value = true
}

function closeModelForm() {
  showModelForm.value = false
  editingModel.value = null
  modelForm.value = {
    model_name: '',
    api_key: '',
    base_url: '',
    provider_type: '',
    is_active: true
  }
}

onMounted(() => {
  apiKeys.value = { ...settingsStore.apiKeys }
  fetchModels()
})

function updateKey(key) {
  settingsStore.updateApiKey(key, apiKeys.value[key])
}

function updateAdminToken() {
  settingsStore.updateAdminToken(adminToken.value)
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

.focus-source-list {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.checkbox-inline {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
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
