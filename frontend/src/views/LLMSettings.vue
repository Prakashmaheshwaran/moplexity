<template>
  <div class="llm-settings">
    <header class="settings-header">
      <h1>LLM Configuration</h1>
      <p>Manage AI model providers and their models</p>
    </header>

    <div class="settings-content">
      <!-- Providers Section -->
      <section class="providers-section">
        <div class="section-header">
          <h2>Providers</h2>
          <button @click="showProviderForm = true" class="btn-primary">
            Add Provider
          </button>
        </div>

        <div v-if="providers.length === 0" class="empty-state">
          <p>No providers configured yet. Add your first provider to get started.</p>
        </div>

        <div class="providers-list">
          <div
            v-for="provider in providers"
            :key="provider.id"
            class="provider-card"
            :class="{ 'inactive': !provider.is_active }"
          >
            <div class="provider-info">
              <h3>{{ provider.name }}</h3>
              <p class="provider-type">{{ provider.provider_type }}</p>
              <div class="provider-status">
                <span :class="provider.is_active ? 'status-active' : 'status-inactive'">
                  {{ provider.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
            </div>

            <div class="provider-actions">
              <button @click="editProvider(provider)" class="btn-secondary">
                Edit
              </button>
              <button @click="deleteProvider(provider.id)" class="btn-danger">
                Delete
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Models Section -->
      <section class="models-section">
        <div class="section-header">
          <h2>Models</h2>
          <button @click="showModelForm = true" class="btn-primary" :disabled="providers.length === 0">
            Add Model
          </button>
        </div>

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
              <h3>{{ model.display_name }}</h3>
              <p class="model-name">{{ model.model_name }}</p>
              <p class="model-provider">{{ model.provider?.name || 'Unknown Provider' }}</p>
              <p v-if="model.description" class="model-description">{{ model.description }}</p>
              <div class="model-status">
                <span :class="model.is_active ? 'status-active' : 'status-inactive'">
                  {{ model.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
            </div>

            <div class="model-actions">
              <button @click="editModel(model)" class="btn-secondary">
                Edit
              </button>
              <button @click="deleteModel(model.id)" class="btn-danger">
                Delete
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Provider Form Modal -->
    <div v-if="showProviderForm" class="modal-overlay" @click="closeProviderForm">
      <div class="modal-content" @click.stop>
        <h3>{{ editingProvider ? 'Edit Provider' : 'Add Provider' }}</h3>
        <form @submit.prevent="saveProvider" class="provider-form">
          <div class="form-group">
            <label for="provider-name">Name:</label>
            <input
              id="provider-name"
              v-model="providerForm.name"
              type="text"
              required
              placeholder="e.g., OpenAI, Anthropic"
            />
          </div>

          <div class="form-group">
            <label for="provider-type">Provider Type:</label>
            <select id="provider-type" v-model="providerForm.provider_type" required>
              <option value="">Select provider type</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="google">Google</option>
              <option value="gemini">Gemini</option>
              <option value="vertexai">Vertex AI</option>
              <option value="cohere">Cohere</option>
              <option value="replicate">Replicate</option>
              <option value="together">Together AI</option>
              <option value="huggingface">HuggingFace</option>
              <option value="bedrock">AWS Bedrock</option>
              <option value="azure">Azure OpenAI</option>
            </select>
          </div>

          <div class="form-group">
            <label for="provider-api-key">API Key:</label>
            <input
              id="provider-api-key"
              v-model="providerForm.api_key"
              type="password"
              required
              placeholder="Enter API key"
            />
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="providerForm.is_active"
              />
              Active
            </label>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeProviderForm" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary">
              {{ editingProvider ? 'Update' : 'Add' }} Provider
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Model Form Modal -->
    <div v-if="showModelForm" class="modal-overlay" @click="closeModelForm">
      <div class="modal-content" @click.stop>
        <h3>{{ editingModel ? 'Edit Model' : 'Add Model' }}</h3>
        <form @submit.prevent="saveModel" class="model-form">
          <div class="form-group">
            <label for="model-provider">Provider:</label>
            <select id="model-provider" v-model="modelForm.provider_id" required>
              <option value="">Select provider</option>
              <option
                v-for="provider in providers"
                :key="provider.id"
                :value="provider.id"
              >
                {{ provider.name }} ({{ provider.provider_type }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="model-name">Model Name:</label>
            <input
              id="model-name"
              v-model="modelForm.model_name"
              type="text"
              required
              placeholder="e.g., gpt-3.5-turbo, gemini/gemini-2.0-flash"
            />
          </div>

          <div class="form-group">
            <label for="model-display-name">Display Name:</label>
            <input
              id="model-display-name"
              v-model="modelForm.display_name"
              type="text"
              required
              placeholder="e.g., GPT-3.5 Turbo, Gemini 2.0 Flash"
            />
          </div>

          <div class="form-group">
            <label for="model-description">Description (optional):</label>
            <textarea
              id="model-description"
              v-model="modelForm.description"
              placeholder="Brief description of the model"
              rows="3"
            ></textarea>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="modelForm.is_active"
              />
              Active
            </label>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModelForm" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary">
              {{ editingModel ? 'Update' : 'Add' }} Model
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const providers = ref([])
const models = ref([])
const showProviderForm = ref(false)
const showModelForm = ref(false)
const editingProvider = ref(null)
const editingModel = ref(null)

const providerForm = ref({
  name: '',
  provider_type: '',
  api_key: '',
  is_active: true
})

const modelForm = ref({
  provider_id: '',
  model_name: '',
  display_name: '',
  description: '',
  is_active: true
})

// Fetch providers and models
async function fetchProviders() {
  try {
    const response = await fetch('/api/llm/providers')
    if (response.ok) {
      providers.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching providers:', error)
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

// Provider CRUD operations
async function saveProvider() {
  try {
    const url = editingProvider.value
      ? `/api/llm/providers/${editingProvider.value.id}`
      : '/api/llm/providers'

    const method = editingProvider.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(providerForm.value)
    })

    if (response.ok) {
      await fetchProviders()
      closeProviderForm()
    } else {
      const error = await response.json()
      alert(`Error: ${error.detail || 'Failed to save provider'}`)
    }
  } catch (error) {
    console.error('Error saving provider:', error)
    alert('Failed to save provider')
  }
}

async function deleteProvider(id) {
  if (!confirm('Are you sure you want to delete this provider? This will also delete all associated models.')) {
    return
  }

  try {
    const response = await fetch(`/api/llm/providers/${id}`, {
      method: 'DELETE'
    })

    if (response.ok) {
      await fetchProviders()
      await fetchModels()
    } else {
      alert('Failed to delete provider')
    }
  } catch (error) {
    console.error('Error deleting provider:', error)
    alert('Failed to delete provider')
  }
}

// Model CRUD operations
async function saveModel() {
  try {
    const url = editingModel.value
      ? `/api/llm/models/${editingModel.value.id}`
      : '/api/llm/models'

    const method = editingModel.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(modelForm.value)
    })

    if (response.ok) {
      await fetchModels()
      closeModelForm()
    } else {
      const error = await response.json()
      alert(`Error: ${error.detail || 'Failed to save model'}`)
    }
  } catch (error) {
    console.error('Error saving model:', error)
    alert('Failed to save model')
  }
}

async function deleteModel(id) {
  if (!confirm('Are you sure you want to delete this model?')) {
    return
  }

  try {
    const response = await fetch(`/api/llm/models/${id}`, {
      method: 'DELETE'
    })

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

// Form management
function editProvider(provider) {
  editingProvider.value = provider
  providerForm.value = { ...provider }
  showProviderForm.value = true
}

function editModel(model) {
  editingModel.value = model
  modelForm.value = { ...model }
  showModelForm.value = true
}

function closeProviderForm() {
  showProviderForm.value = false
  editingProvider.value = null
  providerForm.value = {
    name: '',
    provider_type: '',
    api_key: '',
    is_active: true
  }
}

function closeModelForm() {
  showModelForm.value = false
  editingModel.value = null
  modelForm.value = {
    provider_id: '',
    model_name: '',
    display_name: '',
    description: '',
    is_active: true
  }
}

onMounted(() => {
  fetchProviders()
  fetchModels()
})
</script>

<style scoped>
.llm-settings {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.settings-header {
  text-align: center;
  margin-bottom: 3rem;
}

.settings-header h1 {
  font-size: 2.5rem;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.settings-header p {
  color: var(--text-secondary);
  font-size: 1.125rem;
}

.settings-content {
  display: grid;
  gap: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.75rem;
  color: var(--text-primary);
  margin: 0;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.btn-primary:disabled {
  background-color: var(--border);
  cursor: not-allowed;
}

.btn-secondary {
  background-color: white;
  color: var(--text-primary);
  border: 1px solid var(--border);
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background-color: var(--surface);
}

.btn-danger {
  background-color: #dc2626;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-danger:hover {
  background-color: #b91c1c;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-secondary);
}

.providers-list, .models-list {
  display: grid;
  gap: 1rem;
}

.provider-card, .model-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.provider-card:hover, .model-card:hover {
  box-shadow: var(--shadow-md);
}

.provider-card.inactive, .model-card.inactive {
  opacity: 0.6;
  background-color: var(--surface);
}

.provider-info, .model-info {
  flex: 1;
}

.provider-info h3, .model-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.125rem;
  color: var(--text-primary);
}

.provider-type {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0.25rem 0;
}

.model-name {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0.25rem 0;
  font-family: monospace;
}

.model-provider {
  color: var(--primary-color);
  font-size: 0.875rem;
  margin: 0.25rem 0;
  font-weight: 500;
}

.model-description {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0.5rem 0 0.25rem 0;
}

.provider-status, .model-status {
  margin-top: 0.5rem;
}

.status-active {
  color: #16a34a;
  font-weight: 500;
  font-size: 0.875rem;
}

.status-inactive {
  color: #dc2626;
  font-weight: 500;
  font-size: 0.875rem;
}

.provider-actions, .model-actions {
  display: flex;
  gap: 0.5rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-top: 0;
  color: var(--text-primary);
}

.provider-form, .model-form {
  display: grid;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: var(--text-primary);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid var(--border);
  border-radius: 0.375rem;
  font-size: 0.9rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: normal !important;
}

.checkbox-label input {
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .llm-settings {
    padding: 1rem;
  }

  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .provider-card, .model-card {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .provider-actions, .model-actions {
    justify-content: center;
  }

  .modal-content {
    margin: 1rem;
    padding: 1.5rem;
  }
}
</style>
