import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const apiKeys = ref({
    openai_api_key: '',
    anthropic_api_key: '',
    google_api_key: '',
    bing_search_api_key: '',
    google_search_api_key: '',
    google_cse_id: ''
  })

  const model = ref('gpt-3.5-turbo')
  const streamingEnabled = ref(true)
  const proMode = ref(false)

  // Load settings from localStorage
  function loadSettings() {
    const saved = localStorage.getItem('moplexity-settings')
    if (saved) {
      const parsed = JSON.parse(saved)
      apiKeys.value = { ...apiKeys.value, ...parsed.apiKeys }
      model.value = parsed.model || model.value
      streamingEnabled.value = parsed.streamingEnabled ?? true
      proMode.value = parsed.proMode ?? false
    }
  }

  // Save settings to localStorage
  function saveSettings() {
    const settings = {
      apiKeys: apiKeys.value,
      model: model.value,
      streamingEnabled: streamingEnabled.value,
      proMode: proMode.value
    }
    localStorage.setItem('moplexity-settings', JSON.stringify(settings))
  }

  // Update API key
  function updateApiKey(key, value) {
    apiKeys.value[key] = value
    saveSettings()
  }

  // Update model
  function updateModel(newModel) {
    model.value = newModel
    saveSettings()
  }

  // Toggle streaming
  function toggleStreaming() {
    streamingEnabled.value = !streamingEnabled.value
    saveSettings()
  }

  // Toggle pro mode
  function toggleProMode() {
    proMode.value = !proMode.value
    saveSettings()
  }

  // Initialize
  loadSettings()

  return {
    apiKeys,
    model,
    streamingEnabled,
    proMode,
    loadSettings,
    saveSettings,
    updateApiKey,
    updateModel,
    toggleStreaming,
    toggleProMode
  }
})

