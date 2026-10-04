const EYES = ['OD', 'OS']
const GRADES = [
  { code: 0, label: '无明显 DR', short: '无明显 DR', tone: 'success' },
  { code: 1, label: '轻度非增殖期', short: '轻度 NPDR', tone: 'info' },
  { code: 2, label: '中度非增殖期', short: '中度 NPDR', tone: 'warning' },
  { code: 3, label: '重度非增殖期', short: '重度 NPDR', tone: 'danger' },
  { code: 4, label: '增殖期', short: 'PDR', tone: 'danger' }
]
const QUALITY_STATES = {
  passed: { label: '质控通过', tone: 'success' },
  retake: { label: '需要重拍', tone: 'warning' },
  ungradable: { label: '不可判读', tone: 'danger' },
  missing: { label: '资料缺失', tone: '' },
  pending: { label: '待质控', tone: 'info' },
  unknown_device: { label: '设备未知', tone: 'warning' },
  error: { label: '服务异常', tone: 'danger' }
}
const TASK_STATES = {
  preparing: { label: '待准备', tone: 'info' },
  self_reported: { label: '已自报 · 待核实', tone: 'info' },
  awaiting_signoff: { label: '待医生签发', tone: '' },
  pending_contact: { label: '待联系', tone: 'warning' },
  reminded: { label: '已提醒', tone: 'info' },
  scheduled: { label: '已预约', tone: 'primary' },
  completed: { label: '已完成', tone: 'success' },
  overdue: { label: '逾期', tone: 'danger' },
  lost: { label: '失访', tone: 'danger' }
}
const clone = value => JSON.parse(JSON.stringify(value))
module.exports = { EYES, GRADES, QUALITY_STATES, TASK_STATES, clone }
