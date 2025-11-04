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
    'social': 'Social',
    'reddit': 'Social',
    'youtube': 'Social',
    'linkedin': 'Social',
    'twitter': 'Social',
    'github': 'Social',
    'academic': 'Academic Papers'
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
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  padding: 1rem;
  transition: all var(--transition-base);
  animation: fadeInScale 0.3s var(--ease-out-cubic);
  animation-fill-mode: both;
}

.source-card:nth-child(1) { animation-delay: 0.05s; }
.source-card:nth-child(2) { animation-delay: 0.1s; }
.source-card:nth-child(3) { animation-delay: 0.15s; }
.source-card:nth-child(4) { animation-delay: 0.2s; }
.source-card:nth-child(5) { animation-delay: 0.25s; }

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.source-card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
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
  background-color: var(--surface-hover);
  color: var(--primary-color);
  border: 1px solid var(--border);
}

.badge-reddit {
  background-color: var(--surface-hover);
  color: #ff6b6b;
  border: 1px solid var(--border);
}

.badge-youtube {
  background-color: var(--surface-hover);
  color: #ffd93d;
  border: 1px solid var(--border);
}

.badge-linkedin {
  background-color: var(--surface-hover);
  color: #0077b5;
  border: 1px solid var(--border);
}

.badge-twitter {
  background-color: var(--surface-hover);
  color: #1da1f2;
  border: 1px solid var(--border);
}

.badge-github {
  background-color: var(--surface-hover);
  color: #ffffff;
  border: 1px solid var(--border);
}

.badge-academic {
  background-color: var(--surface-hover);
  color: #8b5cf6;
  border: 1px solid var(--border);
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
  font-weight: 600;
}

.source-title a:hover {
  color: var(--primary-color);
  text-decoration: underline;
}

.source-snippet {
  margin: 0 0 0.75rem 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.6;
  opacity: 0.9;
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

