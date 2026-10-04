const { clone } = require('./schema')

const institutions = [
  { id: 'ORG-001', name: '城南社区筛查点（演示）' },
  { id: 'ORG-002', name: '眼科门诊（演示）' }
]
const devices = [
  { id: 'DEV-CFP-001', name: '眼底相机 A（演示）', modality: 'CFP' },
  { id: 'DEV-OCT-001', name: 'OCT 设备 A（演示）', modality: 'OCT' }
]
const patientFixtures = [
  { id: 'DR-202610-001', name: '陈＊', age: 58, sex: '男', duration: 12, hba1c: '7.8', bp: '132 / 82', date: '2026-10-02', status: '待复核', tone: 'warning', cfp: true, oct: false, rightGrade: 2, leftGrade: 1, institutionId: 'ORG-001' },
  { id: 'DR-202610-002', name: '林＊', age: 64, sex: '女', duration: 16, hba1c: '8.1', bp: '138 / 86', date: '2026-10-02', status: '待采集', tone: 'info', cfp: false, oct: false, rightGrade: null, leftGrade: null, institutionId: 'ORG-001' },
  { id: 'DR-202610-003', name: '王＊', age: 52, sex: '女', duration: 8, hba1c: '7.2', bp: '126 / 78', date: '2026-10-01', status: '待复核', tone: 'warning', cfp: true, oct: true, rightGrade: 1, leftGrade: 1, institutionId: 'ORG-002' },
  { id: 'DR-202610-004', name: '赵＊', age: 67, sex: '男', duration: 20, hba1c: '8.6', bp: '142 / 88', date: '2026-10-01', status: '优先复核', tone: 'danger', cfp: true, oct: true, rightGrade: 3, leftGrade: null, institutionId: 'ORG-002' },
  { id: 'DR-202610-005', name: '周＊', age: 49, sex: '男', duration: 6, hba1c: '6.9', bp: '124 / 76', date: '2026-09-30', status: '随访准备', tone: 'primary', cfp: true, oct: false, rightGrade: 0, leftGrade: 0, institutionId: 'ORG-001' },
  { id: 'DR-202610-006', name: '吴＊', age: 61, sex: '女', duration: 14, hba1c: '7.6', bp: '130 / 80', date: '2026-09-30', status: '待采集', tone: 'info', cfp: false, oct: false, rightGrade: null, leftGrade: null, institutionId: 'ORG-001' }
]
const preparationTemplates = [
  { key: 'records', title: '整理既往眼科与糖尿病资料', description: '准备既往检查、用药记录和近期临床信息，供医生核对。', icon: 'el-icon-folder-opened' },
  { key: 'questions', title: '记录需要向医生确认的问题', description: '汇总报告疑问和资料缺失事项，供复核时确认。', icon: 'el-icon-edit-outline' }
]
function createFixtures() {
  const data = { version: 1, patients: clone(patientFixtures), examinations: [], images: [], drafts: [], reports: [], tasks: [], reviewRecords: [], institutions: clone(institutions), devices: clone(devices) }
  data.patients.forEach((patient, index) => {
    const examinationId = 'EX-202610-' + String(index + 1).padStart(3, '0')
    patient.currentExaminationId = examinationId
    patient.note = ''
    patient.isSynthetic = true
    const exam = { id: examinationId, patientId: patient.id, institutionId: patient.institutionId, performedAt: patient.date + 'T09:00:00+08:00', sourceType: 'synthetic', status: patient.cfp ? (index === 4 ? 'signed' : 'awaiting_review') : 'awaiting_collection', isSynthetic: true, eyes: {}}
    ;['OD', 'OS'].forEach(eye => {
      const imageIds = []
      ;['CFP', 'OCT'].forEach(modality => {
        if (!(modality === 'CFP' ? patient.cfp : patient.oct)) return
        const id = examinationId + '-' + eye + '-' + modality
        imageIds.push(id)
        data.images.push({ id, patientId: patient.id, examinationId, eye, modality, capturedAt: exam.performedAt, institutionId: patient.institutionId, deviceId: modality === 'CFP' ? 'DEV-CFP-001' : 'DEV-OCT-001', sourceType: 'synthetic', fileName: '合成' + eye + modality + '示例', previewUrl: modality === 'CFP' ? 'images/dr/synthetic-fundus.svg' : '', isSchematic: modality === 'CFP', isSynthetic: true, quality: index === 3 && eye === 'OS' ? 'retake' : 'passed' })
      })
      exam.eyes[eye] = { eye, imageIds, quality: { status: patient.cfp ? (index === 3 && eye === 'OS' ? 'retake' : 'passed') : 'missing', reason: index === 3 && eye === 'OS' ? '演示重拍情形：视野不完整，需要重新采集。' : patient.cfp ? '合成质控记录，不代表对示意图实际质控。' : '尚未提供眼底影像。' }, drGrade: eye === 'OD' ? patient.rightGrade : patient.leftGrade, dmeStatus: 'not_assessed' }
    })
    data.examinations.push(exam)
    if (patient.cfp) {
      data.drafts.push({ id: 'DRAFT-' + examinationId, examinationId, patientId: patient.id, status: index === 2 || index === 3 ? 'needs_review' : 'ready', modelVersion: '合成演示，未调用模型', createdAt: exam.performedAt, eyeResults: clone(exam.eyes), disagreements: index === 2 ? ['示例分歧：需医生核对候选等级。'] : [], isSynthetic: true })
    }
    preparationTemplates.forEach(template => data.tasks.push({ ...template, id: examinationId + '-' + template.key, patientId: patient.id, examinationId, reportId: null, type: 'preparation', status: 'preparing', note: '', dueAt: null, updatedAt: exam.performedAt, isSynthetic: true }))
  })
  const historical = { id: 'EX-202607-001', patientId: data.patients[0].id, institutionId: 'ORG-001', performedAt: '2026-07-01T09:00:00+08:00', sourceType: 'synthetic', status: 'signed', isSynthetic: true, eyes: { OD: { eye: 'OD', imageIds: [], quality: { status: 'passed', reason: '合成历史记录，原图未配置。' }, drGrade: 1, dmeStatus: 'not_assessed' }, OS: { eye: 'OS', imageIds: [], quality: { status: 'passed', reason: '合成历史记录，原图未配置。' }, drGrade: 1, dmeStatus: 'not_assessed' }}}
  data.examinations.push(historical)
  ;[historical, data.examinations[4]].forEach((exam, index) => {
    const id = 'REPORT-' + exam.id
    const draftId = 'DRAFT-' + exam.id
    if (!data.drafts.some(item => item.id === draftId)) data.drafts.push({ id: draftId, examinationId: exam.id, patientId: exam.patientId, status: 'ready', modelVersion: '合成演示，未调用模型', createdAt: exam.performedAt, eyeResults: clone(exam.eyes), disagreements: [], isSynthetic: true })
    data.reports.push({ id, examinationId: exam.id, patientId: exam.patientId, draftId, status: 'signed', version: 1, signedBy: '演示眼科医生', signedAt: exam.performedAt.slice(0, 10) + 'T10:00:00+08:00', eyeResults: clone(exam.eyes), conclusion: '本报告为明确标记的合成签发示例，仅展示报告结构。', plan: '演示计划由模拟签发记录提供，不用于实际诊疗安排。', isSynthetic: true })
    data.reviewRecords.push({ id: 'REVIEW-' + exam.id, examinationId: exam.id, reportId: id, actor: '演示眼科医生', action: '合成签发记录', comment: '模拟人工确认后的记录结构。', createdAt: exam.performedAt.slice(0, 10) + 'T10:00:00+08:00', isSynthetic: true })
    data.tasks.push({ id: 'TASK-' + exam.id, key: 'followup', patientId: exam.patientId, examinationId: exam.id, reportId: id, type: 'followup', title: '复查联系与资料准备（演示）', description: '展示已确认合成计划的任务状态，具体项目由临床医生决定。', icon: 'el-icon-date', status: index === 0 ? 'completed' : 'pending_contact', note: '', dueAt: index === 0 ? '2026-07-10' : '2026-10-18', updatedAt: exam.performedAt, isSynthetic: true })
  })
  return data
}
module.exports = { createFixtures, preparationTemplates }
