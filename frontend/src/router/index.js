import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Settings from '../views/Settings.vue'
import LLMSettings from '../views/LLMSettings.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  },
  {
    path: '/llm-settings',
    name: 'LLMSettings',
    component: LLMSettings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

