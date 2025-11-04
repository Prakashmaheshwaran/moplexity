<template>
  <div class="focus-modes">
    <button
      v-for="mode in modes"
      :key="mode.id"
      @click="selectMode(mode.id)"
      class="focus-mode-btn"
      :class="{ active: selectedMode === mode.id }"
      :title="mode.description"
    >
      <span class="mode-icon">{{ mode.icon }}</span>
      <span class="mode-label">{{ mode.label }}</span>
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'web'
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectedMode = ref(props.modelValue)

const modes = [
  { id: 'web', label: 'Web', icon: '🌐', description: 'General web search' },
  { id: 'social', label: 'Social', icon: '💬', description: 'Social media & Reddit' },
  { id: 'academic', label: 'Academic', icon: '📚', description: 'Academic papers & research' }
]

function selectMode(modeId) {
  selectedMode.value = modeId
  emit('update:modelValue', modeId)
  emit('change', modeId)
}
</script>

<style scoped>
.focus-modes {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 1rem;
}

.focus-mode-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.focus-mode-btn:hover {
  background: var(--surface-hover);
  border-color: var(--border-hover);
  color: var(--text-primary);
  transform: translateY(-1px);
}

.focus-mode-btn.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
  box-shadow: var(--shadow);
}

.focus-mode-btn.active:hover {
  background: var(--primary-hover);
  border-color: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

.mode-icon {
  font-size: 1rem;
  line-height: 1;
}

.mode-label {
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .focus-modes {
    gap: 0.375rem;
  }

  .focus-mode-btn {
    padding: 0.375rem 0.75rem;
    font-size: 0.8125rem;
  }

  .mode-label {
    display: none;
  }
}
</style>

