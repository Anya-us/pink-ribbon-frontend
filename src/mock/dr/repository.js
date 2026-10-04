const { EYES, TASK_STATES, QUALITY_STATES, clone } = require('./schema')
const { createFixtures, preparationTemplates } = require('./fixtures')
function assertGraph(data) {
  const collections = ['patients', 'examinations', 'images', 'drafts', 'reports', 'tasks', 'reviewRecords', 'institutions', 'devices']
  if (!data || data.version !== 1) throw new Error('模拟数据版本无效')
  collections.forEach(key => {
    if (!Array.isArray(data[key]) || new Set(data[key].map(item => item.id)).size !== data[key].length) throw new Error('模拟数据集合无效：' + key)
    if (data[key].some(item => !item.id)) throw new Error('模拟数据编号缺失')
  })
  const exists = (key, id) => data[key].find(item => item.id === id)
  data.patients.forEach(patient => {
    const exam = exists('examinations', patient.currentExaminationId)
    if (!exam || exam.patientId !== patient.id || !exists('institutions', patient.institutionId)) throw new Error('患者与当前检查不匹配')
  })
  data.examinations.forEach(exam => {
    if (!exists('patients', exam.patientId) || !exists('institutions', exam.institutionId)) throw new Error('检查关联缺失')
    EYES.forEach(eye => {
      const result = exam.eyes && exam.eyes[eye]
      if (!result || result.eye !== eye || !QUALITY_STATES[result.quality.status]) throw new Error('眼别或质控状态无效')
      if (result.drGrade !== null && (!Number.isInteger(result.drGrade) || result.drGrade < 0 || result.drGrade > 4)) throw new Error('DR 等级无效')
      result.imageIds.forEach(id => { const image = exists('images', id); if (!image || image.examinationId !== exam.id || image.eye !== eye) throw new Error('逐眼影像关联错误') })
    })
  })
  data.images.forEach(image => {
    const exam = exists('examinations', image.examinationId)
    if (!exam || exam.patientId !== image.patientId || !EYES.includes(image.eye) || !['CFP', 'OCT'].includes(image.modality) || !QUALITY_STATES[image.quality] || (image.deviceId && !exists('devices', image.deviceId))) throw new Error('影像关联或状态无效')
  })
  data.drafts.forEach(draft => {
    const exam = exists('examinations', draft.examinationId)
    if (!exam || exam.patientId !== draft.patientId || !EYES.every(eye => draft.eyeResults[eye] && draft.eyeResults[eye].eye === eye)) throw new Error('草稿关联错误')
  })
  data.reports.forEach(report => {
    const draft = exists('drafts', report.draftId)
    if (!draft || draft.examinationId !== report.examinationId || draft.patientId !== report.patientId || (report.status === 'signed' && (!report.signedBy || !report.signedAt))) throw new Error('报告关联或签发记录无效')
  })
  data.tasks.forEach(task => {
    const exam = exists('examinations', task.examinationId)
    const report = task.reportId && exists('reports', task.reportId)
    if (!exam || exam.patientId !== task.patientId || !TASK_STATES[task.status] || (task.type !== 'preparation' && (!report || report.status !== 'signed' || report.patientId !== task.patientId || report.examinationId !== task.examinationId))) throw new Error('任务与签发报告不匹配')
  })
  data.reviewRecords.forEach(record => {
    const exam = exists('examinations', record.examinationId)
    const report = record.reportId && exists('reports', record.reportId)
    if (!exam || (record.reportId && (!report || report.examinationId !== exam.id))) throw new Error('审核记录关联错误')
  })
  return true
}
function createRepository(seed = createFixtures(), onChange = () => {}) {
  assertGraph(seed)
  const db = clone(seed)
  const find = (key, id) => {
    const item = db[key].find(row => row.id === id)
    if (!item) throw new Error('未找到对应' + ({ patients: '患者', examinations: '检查', tasks: '任务' }[key] || '记录'))
    return item
  }
  function context(patientId, examinationId) {
    const patient = find('patients', patientId)
    const examination = find('examinations', examinationId || patient.currentExaminationId)
    if (examination.patientId !== patient.id) throw new Error('患者与检查编号不匹配')
    return { patient, examination }
  }
  function bundle(patientId, examinationId) {
    const { patient, examination } = context(patientId, examinationId)
    return { patient, examination, institution: find('institutions', examination.institutionId), images: db.images.filter(item => item.examinationId === examination.id).map(image => ({ ...image, device: image.deviceId ? find('devices', image.deviceId) : null })), draft: db.drafts.find(item => item.examinationId === examination.id) || null, reports: db.reports.filter(item => item.examinationId === examination.id), tasks: db.tasks.filter(item => item.examinationId === examination.id), reviewRecords: db.reviewRecords.filter(item => item.examinationId === examination.id) }
  }
  function portal(patientId) {
    find('patients', patientId)
    const reports = db.reports.filter(item => item.patientId === patientId && item.status === 'signed')
    return { patient: find('patients', patientId), reports, tasks: db.tasks.filter(item => item.patientId === patientId && reports.some(report => report.id === item.reportId) && item.type !== 'preparation') }
  }
  function region() {
    return db.institutions.map(institution => {
      const exams = db.examinations.filter(item => item.institutionId === institution.id)
      const examIds = new Set(exams.map(item => item.id))
      const tasks = db.tasks.filter(item => item.type !== 'preparation' && examIds.has(item.examinationId))
      return { ...institution, patients: db.patients.filter(item => item.institutionId === institution.id).length, examinations: exams.length, qualityPassed: exams.filter(item => EYES.every(eye => item.eyes[eye].quality.status === 'passed')).length, retake: exams.filter(item => EYES.some(eye => ['retake', 'ungradable'].includes(item.eyes[eye].quality.status))).length, awaitingReview: exams.filter(item => item.status === 'awaiting_review').length, signedReports: db.reports.filter(item => item.status === 'signed' && examIds.has(item.examinationId)).length, openTasks: tasks.filter(item => item.status !== 'completed').length, completedTasks: tasks.filter(item => item.status === 'completed').length }
    })
  }
  function updatePatient(id, patch) {
    const patient = find('patients', id)
    ;['name', 'age', 'sex', 'duration', 'hba1c', 'bp', 'note'].forEach(key => { if (Object.prototype.hasOwnProperty.call(patch, key)) patient[key] = patch[key] })
    onChange(db)
    return clone(patient)
  }
  function updateTask(id, patch) {
    const task = find('tasks', id)
    if (Object.prototype.hasOwnProperty.call(patch, 'status') && !TASK_STATES[patch.status]) throw new Error('任务状态无效')
    if (task.type === 'preparation' && patch.status && !['preparing', 'self_reported'].includes(patch.status)) throw new Error('准备任务不能替代正式随访')
    ;['status', 'note'].forEach(key => { if (Object.prototype.hasOwnProperty.call(patch, key)) task[key] = patch[key] })
    task.updatedAt = new Date().toISOString()
    onChange(db)
    return clone(task)
  }
  function createIntake(patientId, form, files) {
    const patient = find('patients', patientId)
    const id = 'EX-LOCAL-' + Date.now() + '-' + (db.examinations.length + 1)
    const capturedAt = new Date().toISOString()
    const exam = { id, patientId, institutionId: patient.institutionId, performedAt: capturedAt, sourceType: 'local', status: 'pending_quality', isSynthetic: true, eyes: {}}
    EYES.forEach(eye => {
      const imageIds = []
      const prefix = eye === 'OD' ? 'right' : 'left'
      ;['CFP', 'OCT'].forEach(modality => {
        const file = files[prefix + (modality === 'CFP' ? 'Cfp' : 'Oct')]
        if (!file) return
        const imageId = id + '-' + eye + '-' + modality
        imageIds.push(imageId)
        db.images.push({ id: imageId, patientId, examinationId: id, eye, modality, capturedAt, institutionId: patient.institutionId, deviceId: null, sourceType: 'local', fileName: file.name, previewUrl: '', isSchematic: false, isSynthetic: true, quality: 'pending' })
      })
      exam.eyes[eye] = { eye, imageIds, quality: { status: imageIds.length ? 'pending' : 'missing', reason: imageIds.length ? '本地选择，尚未质控；文件内容不保存到模拟服务。' : '尚未提供该眼影像。' }, drGrade: null, dmeStatus: 'not_assessed' }
    })
    db.examinations.push(exam)
    preparationTemplates.forEach(template => db.tasks.push({ ...template, id: id + '-' + template.key, patientId, examinationId: id, reportId: null, type: 'preparation', status: 'preparing', note: '', dueAt: null, updatedAt: capturedAt, isSynthetic: true }))
    updatePatient(patientId, form)
    Object.assign(patient, { currentExaminationId: id, rightGrade: null, leftGrade: null, status: '待评估', tone: 'info', date: capturedAt.slice(0, 10), cfp: !!(files.rightCfp || files.leftCfp), oct: !!(files.rightOct || files.leftOct) })
    onChange(db)
    return clone(exam)
  }
  return { db, find, context, bundle, portal, region, updatePatient, updateTask, createIntake, snapshot: () => clone(db) }
}
module.exports = { createRepository, assertGraph }
