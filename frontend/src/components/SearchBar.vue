<template>
  <div class="search-bar">
    <form @submit.prevent="handleSubmit" class="search-form">
      <!-- Model Selector Icon -->
      <button
        type="button"
        class="icon-button model-icon"
        @click.stop="showModelDropdown = !showModelDropdown"
        :title="selectedModelName || 'Select model'"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
          <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
        </svg>
        <span v-if="selectedModelName" class="icon-label">{{ selectedModelName }}</span>
      </button>

      <!-- Model Dropdown -->
      <div v-if="showModelDropdown" ref="modelDropdown" class="dropdown-menu model-dropdown">
        <div class="dropdown-content">
          <div v-if="loading" class="dropdown-item disabled">
            <span>Loading models...</span>
          </div>
          <div
            v-for="model in models"
            :key="model.id"
            @click="selectModel(model.id)"
            class="dropdown-item"
            :class="{ selected: model.id === parseInt(modelValue) }"
          >
            <div class="item-checkmark">
              <svg v-if="model.id === parseInt(modelValue)" viewBox="0 0 24 24" width="16" height="16">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            </div>
            <div class="item-name">{{ model.model_name }}</div>
          </div>
          <div v-if="!loading && models.length === 0" class="dropdown-item disabled">
            <span>No models available</span>
          </div>
        </div>
      </div>

      <!-- Source Selector Icon -->
      <button
        type="button"
        class="icon-button source-icon"
        @click.stop="showSourceDropdown = !showSourceDropdown"
        :title="selectedSourcesLabel"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
        <span v-if="selectedSourcesCount > 0" class="icon-badge">{{ selectedSourcesCount }}</span>
        <span v-else class="icon-label">Sources</span>
      </button>

      <!-- Source Dropdown -->
      <div v-if="showSourceDropdown" ref="sourceDropdown" class="dropdown-menu source-dropdown">
        <div class="dropdown-content">
          <div class="dropdown-header">Select Sources</div>
          <div
            v-for="source in availableSources"
            :key="source.id"
            @click="toggleSource(source.id)"
            class="dropdown-item source-item"
            :class="{ selected: selectedSources.includes(source.id) }"
          >
            <div class="item-checkbox">
              <svg v-if="selectedSources.includes(source.id)" viewBox="0 0 24 24" width="16" height="16">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            </div>
            <div class="item-name">{{ source.label }}</div>
          </div>
        </div>
      </div>

      <input
        ref="inputRef"
        v-model="query"
        type="text"
        placeholder="Ask anything..."
        class="search-input"
        :disabled="disabled"
        @focus="focused = true"
        @blur="handleBlur"
      />
      <button
        type="submit"
        class="search-button"
        :disabled="!query.trim() || disabled"
      >
        <span v-if="!disabled">Search</span>
        <span v-else class="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onBeforeUnmount } from 'vue'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  autoFocus: {
    type: Boolean,
    default: true
  },
  modelValue: {
    type: [Number, String],
    default: null
  },
  selectedSources: {
    type: Array,
    default: () => ['web']
  }
})

const emit = defineEmits(['submit', 'update:modelValue', 'update:selectedSources'])

const query = ref('')
const focused = ref(false)
const inputRef = ref(null)
const showModelDropdown = ref(false)
const showSourceDropdown = ref(false)
const modelDropdown = ref(null)
const sourceDropdown = ref(null)
const models = ref([])
const loading = ref(true)

const availableSources = [
  { id: 'web', label: 'Web' },
  { id: 'social', label: 'Social' },
  { id: 'academic', label: 'Academic Papers' }
]

const selectedModelName = computed(() => {
  const model = models.value.find(m => m.id === parseInt(props.modelValue))
  return model ? model.model_name : null
})

const selectedSourcesCount = computed(() => {
  return props.selectedSources.length
})

const selectedSourcesLabel = computed(() => {
  if (props.selectedSources.length === 0) return 'Select sources'
  if (props.selectedSources.length === 1) {
    const source = availableSources.find(s => s.id === props.selectedSources[0])
    return source ? source.label : '1 source'
  }
  return `${props.selectedSources.length} sources`
})

onMounted(async () => {
  if (props.autoFocus) {
    inputRef.value?.focus()
  }
  await fetchModels()
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})

async function fetchModels() {
  try {
    loading.value = true
    const response = await fetch('/api/llm/models/active')
    if (response.ok) {
      models.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching models:', error)
    models.value = []
  } finally {
    loading.value = false
  }
}

function selectModel(modelId) {
  emit('update:modelValue', modelId)
  showModelDropdown.value = false
}

function toggleSource(sourceId) {
  const current = [...props.selectedSources]
  const index = current.indexOf(sourceId)
  if (index > -1) {
    current.splice(index, 1)
  } else {
    current.push(sourceId)
  }
  emit('update:selectedSources', current)
}

function handleBlur() {
  focused.value = false
  // Delay closing dropdowns to allow clicks
  setTimeout(() => {
    if (!focused.value) {
      showModelDropdown.value = false
      showSourceDropdown.value = false
    }
  }, 200)
}

function handleClickOutside(event) {
  if (modelDropdown.value && !modelDropdown.value.contains(event.target) && 
      !event.target.closest('.model-icon')) {
    showModelDropdown.value = false
  }
  if (sourceDropdown.value && !sourceDropdown.value.contains(event.target) && 
      !event.target.closest('.source-icon')) {
    showSourceDropdown.value = false
  }
}

function handleSubmit() {
  if (query.value.trim() && !props.disabled) {
    emit('submit', query.value.trim())
    query.value = ''
  }
}

watch(() => props.modelValue, () => {
  // Keep dropdown open when selecting
})
</script>

<style scoped>
.search-bar {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.search-form {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--surface);
  border: 2px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 0.5rem;
  transition: all var(--transition-base);
  position: relative;
}

.search-form:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  transform: translateY(-1px);
}

.icon-button {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.5rem;
  background: transparent;
  border: none;
  border-radius: var(--radius);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-base);
  font-size: 0.75rem;
  white-space: nowrap;
  position: relative;
}

.icon-button:hover {
  background: var(--surface-hover);
  color: var(--text-primary);
  transform: scale(1.05);
}

.icon-button:active {
  transform: scale(0.95);
}

.icon-button svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.icon-label {
  font-size: 0.75rem;
  font-weight: 500;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.icon-badge {
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  font-weight: 600;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 0.5rem;
  font-size: 1rem;
  background: transparent;
  color: var(--text-primary);
  min-width: 0;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-button {
  padding: 0.75rem 1.5rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
  min-width: 80px;
  position: relative;
  overflow: hidden;
}

.search-button::after {
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

.search-button:active::after {
  width: 300px;
  height: 300px;
}

.search-button:hover:not(:disabled) {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.search-button:active:not(:disabled) {
  transform: translateY(0);
}

.search-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  margin-top: 0.5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-lg);
  max-height: 300px;
  overflow: hidden;
  animation: slideDown 0.2s var(--ease-out-cubic);
  transform-origin: top;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px) scaleY(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scaleY(1);
  }
}

.model-dropdown {
  left: 0;
  right: auto;
  min-width: 200px;
}

.source-dropdown {
  left: 0;
  right: auto;
  min-width: 220px;
}

.dropdown-content {
  max-height: 300px;
  overflow-y: auto;
}

.dropdown-header {
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border);
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  border-bottom: 1px solid var(--border);
  position: relative;
}

.dropdown-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--primary-color);
  transform: scaleX(0);
  transition: transform var(--transition-fast);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover:not(.disabled) {
  background-color: var(--surface-hover);
  padding-left: 1.25rem;
}

.dropdown-item:hover:not(.disabled)::before {
  transform: scaleX(1);
}

.dropdown-item.selected {
  background-color: rgba(59, 130, 246, 0.05);
}

.dropdown-item.disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.item-checkmark,
.item-checkbox {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;
  color: var(--primary-color);
  flex-shrink: 0;
}

.item-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.source-item {
  padding: 0.625rem 1rem;
}
</style>

