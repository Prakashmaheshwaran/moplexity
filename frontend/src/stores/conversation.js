import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useConversationStore = defineStore('conversation', () => {
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([])
  const sources = ref([])
  const loading = ref(false)
  const streaming = ref(false)
  const error = ref(null)

  const API_BASE = '/api'

  // Fetch all conversations
  async function fetchConversations() {
    try {
      const response = await axios.get(`${API_BASE}/conversations/`)
      conversations.value = response.data
    } catch (err) {
      console.error('Error fetching conversations:', err)
      error.value = 'Failed to fetch conversations'
    }
  }

  // Fetch specific conversation
  async function fetchConversation(id) {
    try {
      loading.value = true
      const response = await axios.get(`${API_BASE}/conversations/${id}`)
      currentConversation.value = response.data
      messages.value = response.data.messages || []
      error.value = null
    } catch (err) {
      console.error('Error fetching conversation:', err)
      error.value = 'Failed to fetch conversation'
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
  async function sendMessage(query, proMode = false, modelId = null) {
    try {
      loading.value = true
      error.value = null

      const response = await axios.post(`${API_BASE}/chat/`, {
        query,
        conversation_id: currentConversation.value?.id,
        model_id: modelId,
        pro_mode: proMode
      })

      // Update conversation
      if (!currentConversation.value) {
        currentConversation.value = { id: response.data.conversation_id }
        await fetchConversations()
      }

      // Add messages
      messages.value.push({
        id: Date.now(),
        role: 'user',
        content: query,
        created_at: new Date().toISOString()
      })

      messages.value.push({
        id: response.data.message_id,
        role: 'assistant',
        content: response.data.content,
        created_at: new Date().toISOString(),
        sources: response.data.sources
      })

      sources.value = response.data.sources

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
  async function sendMessageStreaming(query, proMode = false, modelId = null) {
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
        sources: []
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
          pro_mode: proMode
        })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6))

            if (data.type === 'conversation_id') {
              if (!currentConversation.value) {
                currentConversation.value = { id: data.conversation_id }
                await fetchConversations()
              }
            } else if (data.type === 'sources') {
              sources.value = data.sources
              assistantMessage.sources = data.sources
            } else if (data.type === 'content') {
              assistantMessage.content += data.content
            } else if (data.type === 'done') {
              assistantMessage.id = data.message_id
            } else if (data.type === 'error') {
              error.value = data.message
            }
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
  }

  return {
    conversations,
    currentConversation,
    messages,
    sources,
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

