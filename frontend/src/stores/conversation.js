import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useConversationStore = defineStore('conversation', () => {
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([])
  const sources = ref([])
  const followUpQuestions = ref([])
  const loading = ref(false)
  const streaming = ref(false)
  const error = ref(null)

  const API_BASE = '/api'

  // Fetch all conversations
  async function fetchConversations() {
    try {
      error.value = null
      const response = await axios.get(`${API_BASE}/conversations/`)
      if (response.data && Array.isArray(response.data)) {
        conversations.value = response.data
      } else {
        conversations.value = []
        console.warn('Unexpected response format:', response.data)
      }
    } catch (err) {
      console.error('Error fetching conversations:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch conversations'
      conversations.value = []
    }
  }

  // Fetch specific conversation
  async function fetchConversation(id) {
    try {
      loading.value = true
      error.value = null
      const response = await axios.get(`${API_BASE}/conversations/${id}`)
      currentConversation.value = response.data
      messages.value = response.data.messages || []
      sources.value = []
      // Extract sources from messages
      response.data.messages?.forEach(msg => {
        if (msg.sources && msg.sources.length > 0) {
          sources.value = [...sources.value, ...msg.sources]
        }
      })
      // Refresh conversations list to update selected state
      await fetchConversations()
    } catch (err) {
      console.error('Error fetching conversation:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch conversation'
      currentConversation.value = null
      messages.value = []
    } finally {
      loading.value = false
    }
  }

  // Create new conversation
  async function createConversation(title) {
    try {
      const response = await axios.post(`${API_BASE}/conversations/`, { title })
      currentConversation.value = response.data
      conversations.value.unshift(response.data)
      return response.data
    } catch (err) {
      console.error('Error creating conversation:', err)
      error.value = 'Failed to create conversation'
      return null
    }
  }

  // Delete conversation
  async function deleteConversation(id) {
    try {
      await axios.delete(`${API_BASE}/conversations/${id}`)
      conversations.value = conversations.value.filter(c => c.id !== id)
      if (currentConversation.value?.id === id) {
        currentConversation.value = null
        messages.value = []
      }
    } catch (err) {
      console.error('Error deleting conversation:', err)
      error.value = 'Failed to delete conversation'
    }
  }

  // Send chat message (non-streaming)
  async function sendMessage(query, proMode = false, modelId = null, focusModes = ['web']) {
    try {
      loading.value = true
      error.value = null

      const response = await axios.post(`${API_BASE}/chat/`, {
        query,
        conversation_id: currentConversation.value?.id,
        model_id: modelId,
        pro_mode: proMode,
        focus_modes: focusModes
      })

      // Update conversation
      if (!currentConversation.value) {
        currentConversation.value = { id: response.data.conversation_id }
      }
      // Always refresh conversations to show updated list
      await fetchConversations()

      // Add messages
      messages.value.push({
        id: Date.now(),
        role: 'user',
        content: query,
        created_at: new Date().toISOString()
      })

      const assistantMsg = {
        id: response.data.message_id,
        role: 'assistant',
        content: response.data.content,
        created_at: new Date().toISOString(),
        sources: response.data.sources,
        follow_up_questions: response.data.follow_up_questions || []
      }
      messages.value.push(assistantMsg)

      sources.value = response.data.sources
      followUpQuestions.value = response.data.follow_up_questions || []

      return response.data
    } catch (err) {
      console.error('Error sending message:', err)
      error.value = 'Failed to send message'
      return null
    } finally {
      loading.value = false
    }
  }

  // Send chat message (streaming)
  async function sendMessageStreaming(query, proMode = false, modelId = null, focusModes = ['web']) {
    try {
      streaming.value = true
      error.value = null

      // Add user message immediately
      messages.value.push({
        id: Date.now(),
        role: 'user',
        content: query,
        created_at: new Date().toISOString()
      })

      // Create assistant message placeholder
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
        sources: [],
        follow_up_questions: []
      }
      messages.value.push(assistantMessage)

      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          conversation_id: currentConversation.value?.id,
          model_id: modelId,
          pro_mode: proMode,
          focus_modes: focusModes
        })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        const events = buffer.split('\n\n')
        buffer = events.pop() || ''

        for (const event of events) {
          const dataLines = event.split('\n').filter(l => l.startsWith('data: '))
          if (dataLines.length === 0) continue
          const payload = dataLines.map(l => l.slice(6)).join('')
          let data
          try {
            data = JSON.parse(payload)
          } catch (e) {
            continue
          }

          if (data.type === 'conversation_id') {
            if (!currentConversation.value) {
              currentConversation.value = { id: data.conversation_id }
            }
            await fetchConversations()
          } else if (data.type === 'sources') {
            sources.value = data.sources
            assistantMessage.sources = data.sources
          } else if (data.type === 'content') {
            assistantMessage.content += data.content
          } else if (data.type === 'follow_up_questions') {
            assistantMessage.follow_up_questions = data.questions || []
            followUpQuestions.value = data.questions || []
          } else if (data.type === 'done') {
            assistantMessage.id = data.message_id
          } else if (data.type === 'error') {
            error.value = data.message
          }
        }
      }

    } catch (err) {
      console.error('Error streaming message:', err)
      error.value = 'Failed to stream message'
    } finally {
      streaming.value = false
    }
  }

  // Reset current conversation
  function resetConversation() {
    currentConversation.value = null
    messages.value = []
    sources.value = []
    followUpQuestions.value = []
  }

  return {
    conversations,
    currentConversation,
    messages,
    sources,
    followUpQuestions,
    loading,
    streaming,
    error,
    fetchConversations,
    fetchConversation,
    createConversation,
    deleteConversation,
    sendMessage,
    sendMessageStreaming,
    resetConversation
  }
})

