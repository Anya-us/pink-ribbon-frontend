/* eslint-env jest */
import { shallowMount } from '@vue/test-utils'
import Vue from 'vue'
import Assess from '@/views/prediction/assess'
import Intake from '@/views/prediction/input'
import { demoState, patients, gradeInfo, selectPatient, setFile, saveIntake, setTaskState } from '@/data/retina-demo'

describe('演示病例边界', () => {
  let createUrl
  let revokeUrl
  beforeEach(() => {
    createUrl = jest.fn().mockReturnValueOnce('blob:first').mockReturnValue('blob:replacement')
    revokeUrl = jest.fn()
    URL.createObjectURL = createUrl
    URL.revokeObjectURL = revokeUrl
    selectPatient(patients[0])
  })
  afterEach(() => selectPatient(patients[0]))

  it('未评估与明确的 0 级始终区分', () => {
    [null, undefined, NaN, -1, 5, '0'].forEach(value => expect(gradeInfo(value).label).toBe('未评估'))
    expect(gradeInfo(0).label).toBe('无明显 DR')
  })

  it('选择文件但尚未提交时，不呈现预置病例的候选分级', async() => {
    const wrapper = shallowMount(Assess, { stubs: { 'el-button': true, 'router-link': true }})
    expect(wrapper.findAll('.summary-eye h3').at(0).text()).toBe('中度非增殖期')
    setFile('rightCfp', new File(['image'], 'test.png', { type: 'image/png' }))
    await Vue.nextTick()
    expect(wrapper.findAll('.summary-eye h3').wrappers.map(node => node.text())).toEqual(['未评估', '未评估'])
    expect(wrapper.find('.agent-grid').text()).toContain('尚未形成候选分级')
    wrapper.destroy()
  })

  it('确认本地资料不会生成 DR 或 DME 诊断', () => {
    setFile('rightCfp', new File(['image'], 'test.png', { type: 'image/png' }))
    saveIntake({ name: '本地演示', age: 58, sex: '男', duration: 12, hba1c: '7.8', bp: '' })
    expect(demoState.patient.rightGrade).toBeNull()
    expect(demoState.patient.leftGrade).toBeNull()
    expect(demoState.intake.fileKeys).toEqual(['rightCfp'])
    expect(demoState.patient.status).toBe('待评估')
  })

  it('切换病例清除上一病例文件、备注与任务进展', () => {
    setFile('rightCfp', new File(['image'], 'test.png', { type: 'image/png' }))
    demoState.profileNote = '上一病例的备注'
    setTaskState('records', { note: '上一病例的任务' })
    saveIntake({ name: '本地演示', age: 58, sex: '男' })
    selectPatient(patients[1])
    expect(demoState.files).toEqual({})
    expect(demoState.intake).toBeNull()
    expect(demoState.profileNote).toBe('')
    expect(demoState.taskStates).toEqual({})
    expect(demoState.patient.id).toBe(patients[1].id)
    expect(revokeUrl).toHaveBeenCalledWith('blob:first')
  })

  it('更换和移除影像时释放旧预览地址', () => {
    setFile('rightCfp', new File(['one'], 'one.png', { type: 'image/png' }))
    setFile('rightCfp', new File(['two'], 'two.png', { type: 'image/png' }))
    expect(revokeUrl).toHaveBeenCalledWith('blob:first')
    setFile('rightCfp', null)
    expect(revokeUrl).toHaveBeenCalledWith('blob:replacement')
    expect(demoState.files.rightCfp).toBeUndefined()
  })

  it('DICOM 文件不冒充可预览影像', () => {
    setFile('rightOct', new File(['dicom'], 'scan.dcm'))
    expect(demoState.files.rightOct.url).toBe('')
    expect(createUrl).not.toHaveBeenCalled()
  })

  it('采集页缓存到确认步骤后切换病例，必须重新核对基础信息', async() => {
    const wrapper = shallowMount(Intake, {
      stubs: ['el-button', 'el-steps', 'el-step', 'el-form', 'el-form-item', 'el-input', 'el-input-number', 'el-select', 'el-option', 'router-link']
    })
    wrapper.setData({ step: 2 })
    selectPatient(patients[1])
    await Vue.nextTick()
    expect(wrapper.find('.intake-footer').text()).toContain('步骤 1 / 3')
    expect(wrapper.vm.form.name).toBe(patients[1].name)
    expect(wrapper.vm.fileCount).toBe(0)
    wrapper.destroy()
  })
})
