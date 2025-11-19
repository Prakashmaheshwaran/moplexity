import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import SearchBar from '../SearchBar.vue'

describe('SearchBar.vue', () => {
    it('renders correctly', () => {
        const wrapper = mount(SearchBar)
        expect(wrapper.find('input').exists()).toBe(true)
        expect(wrapper.find('button').exists()).toBe(true)
    })

    it('emits search event with query when submitted', async () => {
        const wrapper = mount(SearchBar)
        const input = wrapper.find('input')
        await input.setValue('test query')

        await wrapper.find('form').trigger('submit')

        expect(wrapper.emitted()).toHaveProperty('submit')
        expect(wrapper.emitted('submit')[0]).toEqual(['test query'])
    })

    it('does not emit submit if query is empty', async () => {
        const wrapper = mount(SearchBar)
        await wrapper.find('form').trigger('submit')
        expect(wrapper.emitted('submit')).toBeFalsy()
    })
})
