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
  const adminToken = ref('')
  const streamingEnabled = ref(true)
  const proMode = ref(false)
  const defaultFocusSources = ref(['web'])

  // Load settings from localStorage
  function loadSettings() {
    const saved = localStorage.getItem('moplexity-settings')
    if (saved) {
      const parsed = JSON.parse(saved)
      apiKeys.value = { ...apiKeys.value, ...parsed.apiKeys }
      streamingEnabled.value = parsed.streamingEnabled ?? true
      proMode.value = parsed.proMode ?? false
      adminToken.value = parsed.adminToken || ''
      defaultFocusSources.value = Array.isArray(parsed.defaultFocusSources) ? parsed.defaultFocusSources : ['web']
    }
  }

  // Save settings to localStorage
  function saveSettings() {
    const settings = {
      apiKeys: apiKeys.value,
      streamingEnabled: streamingEnabled.value,
      proMode: proMode.value,
      adminToken: adminToken.value,
      defaultFocusSources: defaultFocusSources.value
    }
    localStorage.setItem('moplexity-settings', JSON.stringify(settings))
  }

  // Update API key
  function updateApiKey(key, value) {
    apiKeys.value[key] = value
    saveSettings()
  }

  function updateAdminToken(token) {
    adminToken.value = token
    saveSettings()
  }

  function updateDefaultFocusSources(sources) {
    defaultFocusSources.value = sources && sources.length ? sources : ['web']
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
    adminToken,
    streamingEnabled,
    proMode,
    defaultFocusSources,
    loadSettings,
    saveSettings,
    updateApiKey,
    updateAdminToken,
    updateDefaultFocusSources,
    toggleStreaming,
    toggleProMode
  }
})
