<template>
  <div class="source-card">
    <div class="source-header">
      <span class="source-badge" :class="`badge-${source.source_type}`">
        {{ sourceTypeLabel }}
      </span>
      <span class="source-index">[{{ index }}]</span>
    </div>
    <h4 class="source-title">
      <a :href="source.url" target="_blank" rel="noopener noreferrer">
        {{ source.title }}
      </a>
    </h4>
    <p class="source-snippet">{{ truncatedSnippet }}</p>
    <a :href="source.url" target="_blank" rel="noopener noreferrer" class="source-link">
      {{ displayUrl }}
    </a>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  source: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  }
})

const sourceTypeLabel = computed(() => {
  const labels = {
    'web': 'Web',
    'reddit': 'Reddit',
    'youtube': 'YouTube'
  }
  return labels[props.source.source_type] || 'Web'
})

const truncatedSnippet = computed(() => {
  if (!props.source.snippet) return ''
  return props.source.snippet.length > 200
    ? props.source.snippet.substring(0, 200) + '...'
    : props.source.snippet
})

const displayUrl = computed(() => {
  try {
    const url = new URL(props.source.url)
    return url.hostname
  } catch {
    return props.source.url
  }
})
</script>

<style scoped>
.source-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  padding: 1rem;
  transition: all 0.2s;
}

.source-card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow);
}

.source-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.source-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.badge-web {
  background-color: #dbeafe;
  color: #1e40af;
}

.badge-reddit {
  background-color: #fee2e2;
  color: #991b1b;
}

.badge-youtube {
  background-color: #fef3c7;
  color: #92400e;
}

.source-index {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.source-title {
  margin: 0 0 0.5rem 0;
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.4;
}

.source-title a {
  color: var(--text-primary);
  text-decoration: none;
}

.source-title a:hover {
  color: var(--primary-color);
}

.source-snippet {
  margin: 0 0 0.75rem 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.source-link {
  display: inline-block;
  font-size: 0.8125rem;
  color: var(--primary-color);
  text-decoration: none;
}

.source-link:hover {
  text-decoration: underline;
}
</style>

