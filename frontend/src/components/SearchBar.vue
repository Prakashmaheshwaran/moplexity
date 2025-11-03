<template>
  <div class="search-bar">
    <form @submit.prevent="handleSubmit" class="search-form">
      <input
        ref="inputRef"
        v-model="query"
        type="text"
        placeholder="Ask anything..."
        class="search-input"
        :disabled="disabled"
        @focus="focused = true"
        @blur="focused = false"
      />
      <button
        type="submit"
        class="search-button"
        :disabled="!query.trim() || disabled"
      >
        <span v-if="!disabled">Search</span>
        <span v-else class="loading"></span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  autoFocus: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['submit'])

const query = ref('')
const focused = ref(false)
const inputRef = ref(null)

onMounted(() => {
  if (props.autoFocus) {
    inputRef.value?.focus()
  }
})

function handleSubmit() {
  if (query.value.trim() && !props.disabled) {
    emit('submit', query.value.trim())
    query.value = ''
  }
}
</script>

<style scoped>
.search-bar {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.search-form {
  display: flex;
  gap: 0.5rem;
  background: white;
  border: 2px solid var(--border);
  border-radius: 0.75rem;
  padding: 0.5rem;
  transition: border-color 0.2s;
}

.search-form:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 0.5rem;
  font-size: 1rem;
  background: transparent;
}

.search-input::placeholder {
  color: var(--text-secondary);
}

.search-button {
  padding: 0.75rem 1.5rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  min-width: 80px;
}

.search-button:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.search-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

