/* eslint-env jest */
import { createFixtures } from '@/mock/dr/fixtures'
import { createRepository, assertGraph } from '@/mock/dr/repository'
import { TASK_STATES } from '@/mock/dr/schema'
import { drService } from '@/services/dr'
import { resolveContext, selectContext, demoState } from '@/data/retina-demo'
describe('DR 共用业务底座', () => {
  let repository
  beforeEach(() => { repository = createRepository() })
  it('所有合成实体具备稳定关联且逐眼记录独立', () => {
    const data = createFixtures()
    expect(assertGraph(data)).toBe(true)
    expect(data.patients).toHaveLength(6)
    const exam = data.examinations[0]
    expect(exam.eyes.OD.drGrade).toBe(2)
    expect(exam.eyes.OS.drGrade).toBe(1)
    expect(data.images.every(image => ['OD', 'OS'].includes(image.eye))).toBe(true)
    expect(data.tasks.every(task => TASK_STATES[task.status])).toBe(true)
  })
  it('无效或不匹配的路由上下文被拒绝，不静默选择默认患者', () => {
    expect(() => resolveContext({ patientId: 'DR-202610-002', examinationId: 'EX-202610-001' })).toThrow('不匹配')
    expect(() => resolveContext({ patientId: 'does-not-exist' })).toThrow()
    expect(() => resolveContext({ patientId: ['DR-202610-001'] })).toThrow()
    expect(() => resolveContext({ patientId: '' })).toThrow()
    const context = resolveContext({ examinationId: 'EX-202610-004' })
    expect(context.patient.id).toBe('DR-202610-004')
    selectContext(context.patient.id, context.examination.id)
    expect(demoState.examinationId).toBe('EX-202610-004')
  })
  it('患者服务隔离其他患者、未签发草稿和准备清单', () => {
    const view = repository.portal('DR-202610-005')
    expect(view.reports).toHaveLength(1)
    expect(view.reports.every(report => report.status === 'signed' && report.patientId === view.patient.id)).toBe(true)
    expect(view.tasks.every(task => task.reportId === view.reports[0].id && task.type !== 'preparation')).toBe(true)
    expect(view.drafts).toBeUndefined()
    expect(repository.portal('DR-202610-002').reports).toEqual([])
    expect(repository.portal('DR-202610-002').tasks).toEqual([])
  })
  it('拒绝把未签发草稿建立为正式任务，或把另一眼影像关联到当前眼', () => {
    const draftTask = createFixtures()
    draftTask.tasks[0].type = 'followup'
    expect(() => assertGraph(draftTask)).toThrow('任务')
    const swapped = createFixtures()
    swapped.images[0].eye = 'OS'
    expect(() => assertGraph(swapped)).toThrow('影像')
  })
  it('档案编辑同步到列表与检查视图，区域数字由同一数据汇总', () => {
    repository.updatePatient('DR-202610-005', { name: '同步演示', age: 50, id: 'forbidden' })
    expect(repository.db.patients[4].name).toBe('同步演示')
    expect(repository.bundle('DR-202610-005').patient.age).toBe(50)
    expect(repository.db.patients[4].id).toBe('DR-202610-005')
    const before = repository.region().find(row => row.id === 'ORG-001')
    const task = repository.db.tasks.find(item => item.patientId === 'DR-202610-005' && item.type === 'followup')
    repository.updateTask(task.id, { status: 'completed' })
    const after = repository.region().find(row => row.id === 'ORG-001')
    expect(after.openTasks).toBe(before.openTasks - 1)
    expect(after.completedTasks).toBe(before.completedTasks + 1)
    expect(repository.portal(task.patientId).tasks[0].status).toBe('completed')
    expect(() => repository.updateTask(task.id, { status: 'unknown' })).toThrow()
    expect(() => repository.updateTask(task.id, { status: null })).toThrow()
  })
  it('新采集不伪造诊断，不持久化 blob URL，准备状态与正式随访分开', () => {
    const exam = repository.createIntake('DR-202610-002', { name: '采集演示', age: 64, sex: '女' }, { rightCfp: { name: 'demo.png', url: 'blob:never-store' }})
    expect(exam.eyes.OD.drGrade).toBeNull()
    expect(exam.eyes.OS.drGrade).toBeNull()
    expect(exam.eyes.OD.quality.status).toBe('pending')
    expect(exam.eyes.OS.quality.status).toBe('missing')
    expect(repository.portal(exam.patientId).reports).toEqual([])
    expect(JSON.stringify(repository.snapshot())).not.toContain('blob:')
    const task = repository.db.tasks.find(item => item.examinationId === exam.id)
    expect(() => repository.updateTask(task.id, { status: 'completed' })).toThrow('准备任务')
    expect(assertGraph(repository.snapshot())).toBe(true)
  })
  it('序列化后的合成数据可重新构建并恢复指定检查', () => {
    const restored = createRepository(JSON.parse(JSON.stringify(repository.snapshot())))
    expect(restored.context('DR-202610-001', 'EX-202607-001').examination.eyes.OD.drGrade).toBe(1)
    const broken = restored.snapshot()
    broken.reports[0].draftId = 'missing'
    expect(() => createRepository(broken)).toThrow()
  })
  it('异步服务返回副本，并通过 rejected Promise 返回无效编号', async() => {
    await expect(drService.getPatient('missing')).rejects.toThrow()
    const list = await drService.listPatients()
    list[0].name = '不得影响仓库'
    expect((await drService.getPatient(list[0].id)).name).not.toBe('不得影响仓库')
  })
})
