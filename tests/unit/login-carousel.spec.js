/* eslint-env jest */
import { shallowMount } from '@vue/test-utils'
import Vue from 'vue'
import ClinicalPhotoCarousel from '@/components/ClinicalPhotoCarousel'

const slides = [
  { src: '/first.jpg', alt: '眼科检查' },
  { src: '/second.jpg', alt: '医患交流' },
  { src: '/third.jpg', alt: '眼部检查' }
]

describe('登录页照片连续轮换', () => {
  let wrapper
  let mediaQuery
  let hiddenDescriptor
  let originalMatchMedia
  let originalRequestFrame
  let originalCancelFrame

  beforeEach(() => {
    jest.useFakeTimers()
    hiddenDescriptor = Object.getOwnPropertyDescriptor(document, 'hidden')
    Object.defineProperty(document, 'hidden', { configurable: true, value: false })
    originalMatchMedia = window.matchMedia
    originalRequestFrame = window.requestAnimationFrame
    originalCancelFrame = window.cancelAnimationFrame
    mediaQuery = { matches: false, addEventListener: jest.fn(), removeEventListener: jest.fn() }
    window.matchMedia = jest.fn(() => mediaQuery)
    window.requestAnimationFrame = callback => window.setTimeout(callback, 16)
    window.cancelAnimationFrame = id => window.clearTimeout(id)
  })

  afterEach(() => {
    if (wrapper && !wrapper.vm._isDestroyed) wrapper.destroy()
    wrapper = null
    if (hiddenDescriptor) Object.defineProperty(document, 'hidden', hiddenDescriptor)
    else delete document.hidden
    window.matchMedia = originalMatchMedia
    window.requestAnimationFrame = originalRequestFrame
    window.cancelAnimationFrame = originalCancelFrame
    jest.clearAllTimers()
    jest.useRealTimers()
  })

  function mount() {
    wrapper = shallowMount(ClinicalPhotoCarousel, { propsData: { slides }})
    return wrapper
  }

  async function loadPhoto(index, decode = () => Promise.resolve()) {
    const photo = wrapper.findAll('img').at(index)
    Object.defineProperty(photo.element, 'naturalWidth', { configurable: true, value: 1600 })
    Object.defineProperty(photo.element, 'complete', { configurable: true, value: true })
    photo.element.decode = decode
    await photo.trigger('load')
    await Vue.nextTick()
  }

  async function startFade() {
    jest.advanceTimersByTime(6000)
    await Vue.nextTick()
    jest.advanceTimersByTime(32)
    await Vue.nextTick()
  }

  it('下一张尚未解码时保持当前照片，不开始空白轮换', async() => {
    mount()
    await loadPhoto(0)
    let finishDecode
    await loadPhoto(1, () => new Promise(resolve => { finishDecode = resolve }))
    jest.advanceTimersByTime(12000)
    expect(wrapper.findAll('.is-active').length).toBe(1)
    expect(wrapper.find('.is-active').attributes('src')).toBe('/first.jpg')
    expect(wrapper.find('.is-entering').exists()).toBe(false)
    finishDecode()
    await Vue.nextTick()
    await Vue.nextTick()
    await startFade()
    expect(wrapper.find('.is-entering').attributes('src')).toBe('/second.jpg')
  })

  it('跳过失败照片，渐变时保留不透明底层，并能循环回到首张', async() => {
    mount()
    await loadPhoto(0)
    await wrapper.findAll('img').at(1).trigger('error')
    await loadPhoto(2)
    await startFade()
    expect(wrapper.find('.is-active').attributes('src')).toBe('/first.jpg')
    expect(wrapper.find('.is-entering.is-visible').attributes('src')).toBe('/third.jpg')
    await wrapper.findAll('img').at(2).trigger('transitionend', { propertyName: 'opacity' })
    expect(wrapper.find('.is-active').attributes('src')).toBe('/third.jpg')
    await startFade()
    expect(wrapper.find('.is-active').attributes('src')).toBe('/third.jpg')
    expect(wrapper.find('.is-entering.is-visible').attributes('src')).toBe('/first.jpg')
  })

  it('下一张出现加载错误时继续保留当前画面', async() => {
    mount()
    await loadPhoto(0)
    await loadPhoto(1)
    await startFade()
    await wrapper.findAll('img').at(1).trigger('error')
    expect(wrapper.find('.is-active').attributes('src')).toBe('/first.jpg')
    expect(wrapper.find('.is-entering').exists()).toBe(false)
    jest.advanceTimersByTime(20000)
    expect(wrapper.find('.is-active').attributes('src')).toBe('/first.jpg')
  })

  it('标签页隐藏后保持画面，返回后从完整停留时间开始轮换', async() => {
    mount()
    await loadPhoto(0)
    await loadPhoto(1)
    Object.defineProperty(document, 'hidden', { configurable: true, value: true })
    document.dispatchEvent(new Event('visibilitychange'))
    jest.advanceTimersByTime(20000)
    expect(wrapper.find('.is-entering').exists()).toBe(false)
    Object.defineProperty(document, 'hidden', { configurable: true, value: false })
    document.dispatchEvent(new Event('visibilitychange'))
    await startFade()
    expect(wrapper.find('.is-entering').attributes('src')).toBe('/second.jpg')
  })

  it('减少动态效果时不自动播放，手动选择直接显示完整照片', async() => {
    mediaQuery.matches = true
    mount()
    await loadPhoto(0)
    await loadPhoto(1)
    jest.advanceTimersByTime(20000)
    expect(wrapper.find('.is-entering').exists()).toBe(false)
    await wrapper.findAll('.photo-selectors button').at(1).trigger('click')
    expect(wrapper.find('.is-active').attributes('src')).toBe('/second.jpg')
    expect(wrapper.find('.is-entering').exists()).toBe(false)
  })

  it('离开页面会移除监听，延迟完成的解码不会启动轮换', async() => {
    const removeListener = jest.spyOn(document, 'removeEventListener')
    mount()
    await loadPhoto(0)
    let finishDecode
    await loadPhoto(1, () => new Promise(resolve => { finishDecode = resolve }))
    const vm = wrapper.vm
    wrapper.destroy()
    finishDecode()
    await Vue.nextTick()
    expect(removeListener).toHaveBeenCalledWith('visibilitychange', vm.onVisibilityChange)
    expect(mediaQuery.removeEventListener).toHaveBeenCalledWith('change', vm.onMotionChange)
    expect(vm.readyCount).toBe(1)
    removeListener.mockRestore()
  })
})
