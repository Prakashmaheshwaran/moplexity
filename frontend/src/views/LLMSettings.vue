<template>
  <div class="llm-settings">
    <header class="settings-header">
      <div class="header-content">
        <button @click="$router.push('/settings')" class="back-button">
          ← Back to Settings
        </button>
        <div class="header-text">
          <h1>LLM Configuration</h1>
          <p>Manage AI models</p>
        </div>
      </div>
    </header>

    <div class="settings-content">
      <!-- Models Section -->
      <section class="models-section">
        <div class="section-header">
          <h2>Models</h2>
          <button @click="showModelForm = true" class="btn-primary">
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

    <!-- Model Form Modal -->
    <div v-if="showModelForm" class="modal-overlay" @click="closeModelForm">
      <div class="modal-content" @click.stop>
        <h3>{{ editingModel ? 'Edit Model' : 'Add Model' }}</h3>
        <form @submit.prevent="saveModel" class="model-form">
          <div class="form-group">
            <label for="model-name">Model Name:</label>
            <input
              id="model-name"
              v-model="modelForm.model_name"
              type="text"
              required
              placeholder="e.g., gemini/gemini-2.0-pro, ollama/llama2, openai/gpt-4"
              @input="autoInferProviderType"
            />
            <small class="form-hint">Full model identifier (provider/model or just model name)</small>
          </div>

          <div class="form-group">
            <label for="model-api-key">API Key:</label>
            <input
              id="model-api-key"
              v-model="modelForm.api_key"
              type="password"
              required
              placeholder="Enter API key"
            />
          </div>

          <div class="form-group">
            <label for="model-base-url">Base URL (optional):</label>
            <input
              id="model-base-url"
              v-model="modelForm.base_url"
              type="url"
              placeholder="e.g., http://localhost:11434 (for Ollama)"
            />
            <small class="form-hint">For custom endpoints like Ollama or self-hosted models</small>
          </div>

          <div class="form-group">
            <label for="model-provider-type">Provider Type (optional):</label>
            <input
              id="model-provider-type"
              v-model="modelForm.provider_type"
              type="text"
              placeholder="Auto-filled from model name"
            />
            <small class="form-hint">Will be inferred from model name if not specified</small>
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

// Auto-infer provider type from model name
function autoInferProviderType() {
  const modelName = modelForm.value.model_name
  if (modelName && '/' in modelName && !modelForm.value.provider_type) {
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

// Model CRUD operations
async function saveModel() {
  try {
    const url = editingModel.value
      ? `/api/llm/models/${editingModel.value.id}`
      : '/api/llm/models'

    const method = editingModel.value ? 'PUT' : 'POST'

    // Prepare payload - only send non-empty base_url
    const payload = {
      model_name: modelForm.value.model_name,
      api_key: modelForm.value.api_key,
      is_active: modelForm.value.is_active
    }
    
    if (modelForm.value.base_url) {
      payload.base_url = modelForm.value.base_url
    }
    
    if (modelForm.value.provider_type) {
      payload.provider_type = modelForm.value.provider_type
    }

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
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
function editModel(model) {
  editingModel.value = model
  modelForm.value = {
    model_name: model.model_name || '',
    api_key: '', // Don't show existing API key for security
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
  fetchModels()
})
</script>

<style scoped>
.llm-settings {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
  background-color: var(--background);
}

.settings-header {
  margin-bottom: 3rem;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.back-button {
  background: none;
  border: none;
  color: var(--primary-color);
  font-size: 1rem;
  cursor: pointer;
  padding: 0.5rem 0;
  text-decoration: none;
  transition: color 0.2s;
}

.back-button:hover {
  color: var(--primary-hover);
  text-decoration: underline;
}

.header-text {
  text-align: center;
  flex: 1;
}

.header-text h1 {
  font-size: 2.5rem;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.header-text p {
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
  background-color: var(--surface);
  color: var(--text-primary);
  border: 1px solid var(--border);
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background-color: var(--surface-hover);
  border-color: var(--border-hover);
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

.models-list {
  display: grid;
  gap: 1rem;
}

.model-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: all 0.2s;
}

.model-card:hover {
  background: var(--surface-hover);
  border-color: var(--border-hover);
  box-shadow: var(--shadow-lg);
}

.model-card.inactive {
  opacity: 0.6;
  background-color: var(--surface);
}

.model-info {
  flex: 1;
}

.model-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.125rem;
  color: var(--text-primary);
  font-family: monospace;
}

.model-provider-type {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0.25rem 0;
}

.model-base-url {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0.25rem 0;
  font-family: monospace;
}

.model-status {
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

.model-actions {
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
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 2rem;
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-xl);
}

.modal-content h3 {
  margin-top: 0;
  color: var(--text-primary);
}

.model-form {
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
  border-radius: var(--radius);
  font-size: 0.9rem;
  background-color: var(--background);
  color: var(--text-primary);
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  background-color: var(--surface);
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: var(--text-muted);
}

.form-hint {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: -0.25rem;
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

  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .back-button {
    align-self: flex-start;
    font-size: 0.9rem;
  }

  .header-text h1 {
    font-size: 2rem;
  }

  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .model-card {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .model-actions {
    justify-content: center;
  }

  .modal-content {
    margin: 1rem;
    padding: 1.5rem;
  }
}
</style>
