<template>
  <div class="model-selector">
    <label for="model-select" class="model-label">AI Model:</label>
    <select
      id="model-select"
      v-model="selectedModelId"
      @change="onModelChange"
      class="model-dropdown"
      :disabled="loading"
    >
      <option value="" disabled v-if="loading">Loading models...</option>
      <option value="" disabled v-else-if="models.length === 0">No models available</option>
      <option
        v-for="model in models"
        :key="model.id"
        :value="model.id"
        :title="model.description"
      >
        {{ model.display_name }} ({{ model.provider_name }})
      </option>
    </select>
    <div v-if="selectedModel && selectedModel.description" class="model-description">
      {{ selectedModel.description }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModelSelector',
  props: {
    modelValue: {
      type: [Number, String],
      default: null
    }
  },
  emits: ['update:modelValue', 'model-changed'],
  data() {
    return {
      models: [],
      loading: true,
      selectedModelId: this.modelValue
    }
  },
  computed: {
    selectedModel() {
      return this.models.find(model => model.id === parseInt(this.selectedModelId)) || null
    }
  },
  async mounted() {
    await this.fetchModels()
  },
  methods: {
    async fetchModels() {
      try {
        this.loading = true
        const response = await fetch('/api/llm/models/active')
        if (response.ok) {
          this.models = await response.json()
        } else {
          console.error('Failed to fetch models:', response.statusText)
          this.models = []
        }
      } catch (error) {
        console.error('Error fetching models:', error)
        this.models = []
      } finally {
        this.loading = false
      }
    },
    onModelChange() {
      this.$emit('update:modelValue', this.selectedModelId ? parseInt(this.selectedModelId) : null)
      this.$emit('model-changed', this.selectedModel)
    }
  },
  watch: {
    modelValue(newValue) {
      this.selectedModelId = newValue
    }
  }
}
</script>

<style scoped>
.model-selector {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.model-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #374151;
}

.model-dropdown {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background-color: white;
  font-size: 0.9rem;
  min-width: 250px;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.model-dropdown:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.model-dropdown:disabled {
  background-color: #f9fafb;
  cursor: not-allowed;
}

.model-description {
  font-size: 0.8rem;
  color: #6b7280;
  font-style: italic;
  margin-top: 0.25rem;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .model-label {
    color: #d1d5db;
  }

  .model-dropdown {
    background-color: #1f2937;
    border-color: #374151;
    color: #f9fafb;
  }

  .model-dropdown:focus {
    border-color: #60a5fa;
    box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
  }

  .model-dropdown:disabled {
    background-color: #111827;
  }

  .model-description {
    color: #9ca3af;
  }
}
</style>
