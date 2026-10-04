import { GRADES, repository, drState } from './index'
const grade = code => GRADES.find(item => item.code === code) || { short: '未评估', label: '未评估' }
export function assessmentView(bundle, localSelection = false) {
  const { examination, draft, images, patient } = bundle
  const hasCfp = images.some(item => item.modality === 'CFP')
  const hasOct = images.some(item => item.modality === 'OCT')
  const evaluated = !!draft && !localSelection
  const eyes = ['OD', 'OS'].map(eye => ({ key: eye === 'OD' ? 'right' : 'left', abbr: eye, label: eye === 'OD' ? '右眼' : '左眼', grade: evaluated ? draft.eyeResults[eye].drGrade : null }))
  return {
    eyes,
    stages: [
      { title: '资料汇集', description: hasCfp ? '已有影像资料' : '等待眼底资料', ready: hasCfp },
      { title: '共识草稿', description: evaluated ? '合成演示草稿' : '尚未推理', ready: evaluated },
      { title: '医生复核', description: examination.status === 'signed' ? '合成审核记录' : '待医生确认', ready: examination.status === 'signed' },
      { title: '报告与随访', description: examination.status === 'signed' ? '已签发合成示例' : '待签发后安排', ready: examination.status === 'signed' }
    ],
    agents: [
      { number: '01', name: '影像质量', description: '核对可评估性、眼别与图像质量。', status: evaluated ? '合成记录' : '待质控', tone: evaluated ? 'info' : '', result: evaluated ? '双眼分别记录质控状态' : '尚未评估' },
      { number: '02', name: '病灶与分级', description: '按左右眼组织 DR 候选分级证据。', status: evaluated ? '演示草稿' : '未评估', tone: evaluated ? 'warning' : '', result: evaluated ? '右眼 ' + grade(eyes[0].grade).short + ' / 左眼 ' + grade(eyes[1].grade).short : '尚未形成候选分级' },
      { number: '03', name: 'OCT 与黄斑', description: '结合 OCT 单独记录黄斑评估状态。', status: hasOct ? '待判读' : '资料缺失', tone: hasOct ? 'info' : '', result: 'DME 未评估' },
      { number: '04', name: '临床背景', description: '关联糖尿病病程与已提供的病史。', status: '待核对', tone: 'info', result: '病程 ' + (patient.duration == null ? '未填写' : patient.duration + ' 年') + ' · HbA1c ' + (patient.hba1c ? patient.hba1c + '%' : '未提供') },
      { number: '05', name: '纵向对照', description: '核对既往记录与当前证据的可比性。', status: '未评估', tone: '', result: '历史检查独立记录，未自动判断进展' },
      { number: '06', name: '共识协调', description: '汇总分歧、缺失证据与需人工复核项。', status: evaluated ? '待复核' : '待评估', tone: evaluated ? 'warning' : '', result: evaluated ? (draft.disagreements[0] || '双眼分级待复核 · DME 未评估') : '等待质量检查与模型输出' }
    ]
  }
}
export function examinationHistory(patientId) {
  return drState.examinations.filter(item => item.patientId === patientId).slice().sort((a, b) => b.performedAt.localeCompare(a.performedAt))
}
export function taskViews(bundle) {
  const tasks = bundle.tasks.map(task => ({ ...task, tone: task.type === 'preparation' ? 'info' : 'primary', recordable: task.type === 'preparation' }))
  if (!tasks.some(item => item.type === 'followup')) tasks.push({ id: bundle.examination.id + '-awaiting', title: '建立正式复查与随访任务', description: '由医生签发报告并确认计划后建立。', status: 'awaiting_signoff', tone: '', icon: 'el-icon-date', recordable: false, button: '待医生确认' })
  return tasks
}
export function portalView(patientId) { return repository.portal(patientId) }
export function regionView() { return repository.region() }
