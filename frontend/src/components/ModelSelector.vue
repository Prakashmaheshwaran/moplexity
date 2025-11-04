<template>
  <div class="model-selector">
    <div class="dropdown-container">
      <button
        @click="toggleDropdown"
        @keydown="handleKeydown"
        class="dropdown-trigger"
        :class="{ 'dropdown-open': isOpen }"
        :disabled="loading"
        ref="trigger"
      >
        <div class="selected-model">
          <div v-if="loading" class="loading-text">Loading...</div>
          <div v-else-if="models.length === 0" class="no-models-text">No models</div>
          <div v-else-if="selectedModel" class="model-name-only">
            {{ selectedModel.model_name }}
          </div>
          <div v-else class="placeholder-text">Select model</div>
        </div>
        <svg class="dropdown-arrow" :class="{ 'arrow-up': isOpen }" viewBox="0 0 24 24" width="16" height="16">
          <path d="M7 10l5 5 5-5z"/>
        </svg>
      </button>

      <div v-if="isOpen" class="dropdown-menu" ref="dropdown">
        <div class="dropdown-content">
          <div
            v-for="model in models"
            :key="model.id"
            @click="selectModel(model.id)"
            class="dropdown-item"
            :class="{ 'selected': model.id === parseInt(selectedModelId) }"
          >
            <div class="item-checkmark">
              <svg v-if="model.id === parseInt(selectedModelId)" viewBox="0 0 24 24" width="16" height="16">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            </div>
            <div class="item-content">
              <div class="item-name">{{ model.model_name }}</div>
            </div>
          </div>
        </div>
      </div>
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
      selectedModelId: this.modelValue,
      isOpen: false
    }
  },
  computed: {
    selectedModel() {
      return this.models.find(model => model.id === parseInt(this.selectedModelId)) || null
    }
  },
  async mounted() {
    await this.fetchModels()
    document.addEventListener('click', this.handleClickOutside)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
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
    toggleDropdown() {
      if (this.loading || this.models.length === 0) return
      this.isOpen = !this.isOpen
    },
    selectModel(modelId) {
      this.selectedModelId = modelId
      this.isOpen = false
      this.$emit('update:modelValue', modelId ? parseInt(modelId) : null)
      this.$emit('model-changed', this.selectedModel)
    },
    handleClickOutside(event) {
      if (!this.$refs.trigger?.contains(event.target) && !this.$refs.dropdown?.contains(event.target)) {
        this.isOpen = false
      }
    },
    handleKeydown(event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault()
        this.toggleDropdown()
      } else if (event.key === 'Escape') {
        this.isOpen = false
      } else if (event.key === 'ArrowDown' && !this.isOpen) {
        event.preventDefault()
        this.isOpen = true
      }
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
}

.dropdown-container {
  position: relative;
  min-width: 280px;
}

.dropdown-trigger {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  background: var(--surface);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.dropdown-trigger:hover:not(:disabled) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.dropdown-trigger.dropdown-open {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.dropdown-trigger:disabled {
  background-color: var(--surface);
  cursor: not-allowed;
  opacity: 0.6;
}

.selected-model {
  display: flex;
  align-items: center;
  flex: 1;
}

.model-name-only {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.placeholder-text {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.loading-text,
.no-models-text {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-style: italic;
}

.dropdown-arrow {
  color: var(--text-secondary);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.dropdown-arrow.arrow-up {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  margin-top: 0.25rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  box-shadow: var(--shadow-lg);
  max-height: 300px;
  overflow: hidden;
}

.dropdown-content {
  max-height: 300px;
  overflow-y: auto;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.15s ease;
  border-bottom: 1px solid var(--border);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background-color: var(--surface-hover);
}

.dropdown-item.selected {
  background-color: rgba(59, 130, 246, 0.05);
}

.dropdown-item.selected:hover {
  background-color: rgba(59, 130, 246, 0.1);
}

.item-checkmark {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;
  color: var(--primary-color);
  flex-shrink: 0;
}

.item-content {
  display: flex;
  flex: 1;
}

.item-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.9rem;
}


/* Mobile responsiveness */
@media (max-width: 768px) {
  .dropdown-container {
    min-width: 250px;
  }

  .dropdown-menu {
    max-height: 250px;
  }
}
</style>
