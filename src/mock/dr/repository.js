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
      return { ...institution, patients: db.patients.filter(item => item.institutionId === institution.id).length, examinations: exams.length, qualityPassed: exams.filter(item => EYES.every(eye => item.eyes[eye].quality.status === 'passed')).length, retake: exams.filter(item => EYES.some(eye => ['retake', 'ungradable', 'unknown_device'].includes(item.eyes[eye].quality.status))).length, awaitingReview: exams.filter(item => item.status === 'awaiting_review').length, signedReports: db.reports.filter(item => item.status === 'signed' && examIds.has(item.examinationId)).length, openTasks: tasks.filter(item => item.status !== 'completed').length, completedTasks: tasks.filter(item => item.status === 'completed').length, pendingContact: tasks.filter(item => item.status === 'pending_contact').length, reminded: tasks.filter(item => item.status === 'reminded').length, scheduled: tasks.filter(item => item.status === 'scheduled').length, overdueOrLost: tasks.filter(item => ['overdue', 'lost'].includes(item.status)).length, patientConfirmed: tasks.filter(item => !!item.patientConfirmedAt).length, feedbackReceived: tasks.filter(item => !!item.patientFeedbackAt).length }
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
    if (task.type !== 'preparation' && patch.status && patch.status !== task.status) {
      const transitions = {
        pending_contact: ['reminded', 'scheduled', 'overdue', 'lost'],
        reminded: ['scheduled', 'completed', 'overdue', 'lost'],
        scheduled: ['reminded', 'completed', 'overdue', 'lost'],
        overdue: ['reminded', 'scheduled', 'completed', 'lost'],
        lost: ['reminded', 'scheduled'],
        completed: []
      }
      if (!(transitions[task.status] || []).includes(patch.status)) throw new Error('该随访状态不能直接这样流转')
    }
    if (task.type !== 'preparation' && task.reportId) {
      const report = find('reports', task.reportId)
      if (report.status !== 'signed' || report.patientId !== task.patientId || report.examinationId !== task.examinationId) throw new Error('随访任务必须关联同一患者的已签发报告')
    }
    ['status', 'note', 'dueAt', 'plan', 'planType', 'patientConfirmedAt', 'patientFeedback', 'patientFeedbackAt'].forEach(key => { if (Object.prototype.hasOwnProperty.call(patch, key)) task[key] = patch[key] })
    if (Object.prototype.hasOwnProperty.call(patch, 'patientFeedback') && patch.patientFeedback && !Object.prototype.hasOwnProperty.call(patch, 'patientFeedbackAt')) task.patientFeedbackAt = new Date().toISOString()
    task.updatedAt = new Date().toISOString()
    onChange(db)
    return clone(task)
  }
  function createIntake(patientId, form, files, capture = {}) {
    const patient = find('patients', patientId)
    const id = 'EX-LOCAL-' + Date.now() + '-' + (db.examinations.length + 1)
    const capturedAt = capture.capturedAt || new Date().toISOString()
    const selectedEyes = EYES.filter(eye => (capture.eyes || []).includes(eye))
    const qualityScenario = capture.deviceId ? (capture.qualityScenario || 'pending') : 'unknown_device'
    const qualityInfo = {
      passed: { status: 'passed', reason: '演示质控通过：图像与采集信息满足进入人工复核的基础条件。' },
      retake: { status: 'retake', reason: '演示质控提示：视野或清晰度不足，建议改善对焦后重新采集。' },
      ungradable: { status: 'ungradable', reason: '演示质控提示：图像严重不可判读，本次不进入候选分级。' },
      unknown_device: { status: 'unknown_device', reason: '未登记采集设备，需补录设备信息后再进入医生复核。' },
      pending: { status: 'pending', reason: '已提交本地影像，等待模型技术检查。' }
    }[qualityScenario] || { status: 'pending', reason: '本地资料已选择，等待质控。' }
    const device = capture.deviceId ? find('devices', capture.deviceId) : null
    const exam = { id, patientId, institutionId: patient.institutionId, performedAt: capturedAt, sourceType: 'local', source: capture.source || '现场采集', deviceId: capture.deviceId || null, deviceName: device ? device.name : '未登记', captureQualityScenario: capture.qualityScenario || '', status: 'pending_quality', isSynthetic: false, eyes: {}}
    EYES.forEach(eye => {
      const imageIds = []
      const prefix = eye === 'OD' ? 'right' : 'left'
      ;['CFP', 'OCT'].forEach(modality => {
        const file = files[prefix + (modality === 'CFP' ? 'Cfp' : 'Oct')]
        if (!file) return
        const imageId = id + '-' + eye + '-' + modality
        imageIds.push(imageId)
        db.images.push({ id: imageId, patientId, examinationId: id, eye, modality, capturedAt, institutionId: patient.institutionId, deviceId: capture.deviceId || null, sourceType: 'local', fileName: file.name, previewUrl: '', isSchematic: false, isSynthetic: false, quality: selectedEyes.includes(eye) ? qualityInfo.status : 'missing' })
      })
      const suppliedCfp = !!files[prefix + 'Cfp']
      exam.eyes[eye] = { eye, imageIds, quality: { status: suppliedCfp && selectedEyes.includes(eye) ? qualityInfo.status : 'missing', reason: suppliedCfp && selectedEyes.includes(eye) ? qualityInfo.reason : '该眼未纳入本次采集，相关评估保持未提供 / 未评估。' }, drGrade: null, dmeStatus: 'not_assessed' }
    })
    const collectedEyes = selectedEyes.filter(eye => exam.eyes[eye].imageIds.length)
    exam.status = collectedEyes.length && collectedEyes.every(eye => exam.eyes[eye].quality.status === 'passed') ? 'awaiting_review' : 'pending_quality'
    db.examinations.push(exam)
    preparationTemplates.forEach(template => db.tasks.push({ ...template, id: id + '-' + template.key, patientId, examinationId: id, reportId: null, type: 'preparation', status: 'preparing', note: '', dueAt: null, plan: '', planType: '', patientConfirmedAt: '', patientFeedback: '', patientFeedbackAt: '', updatedAt: capturedAt, isSynthetic: false }))
    updatePatient(patientId, form)
    Object.assign(patient, { currentExaminationId: id, rightGrade: null, leftGrade: null, status: '待评估', tone: 'info', date: capturedAt.slice(0, 10), cfp: !!(files.rightCfp || files.leftCfp), oct: !!(files.rightOct || files.leftOct) })
    onChange(db)
    return clone(exam)
  }
  function attachInference(examinationId, eyePredictions) {
    const exam = find('examinations', examinationId)
    const patient = find('patients', exam.patientId)
    const updatedEyes = []
    const disagreementNotes = []
    EYES.forEach(eye => {
      const prediction = eyePredictions[eye]
      if (!prediction) return
      const technical = prediction.technical_check || {}
      const consensus = prediction.consensus || {}
      const manualQuality = ['retake', 'ungradable'].includes(exam.captureQualityScenario)
      const modelQuality = technical.status === 'pass' ? 'passed' : 'retake'
      const priorQuality = exam.eyes[eye].quality
      let status = modelQuality
      let reason = (technical.message || '模型技术检查未返回说明。') + '（研究演示，非临床质量认证）'
      if (!exam.deviceId) {
        status = 'unknown_device'
        reason = '设备未登记；' + reason
      } else if (manualQuality) {
        status = priorQuality.status
        reason = priorQuality.reason + ' 模型技术检查结果：' + (technical.message || '未返回说明。')
      }
      exam.eyes[eye].quality = { status, reason }
      exam.eyes[eye].drGrade = Number.isInteger(prediction.predicted_grade) ? prediction.predicted_grade : null
      exam.eyes[eye].dmeStatus = 'not_assessed'
      exam.eyes[eye].inference = {
        source: 'algorithm7_local_api',
        modelVersion: prediction.model_version || '模型版本未返回',
        confidence: prediction.confidence,
        probabilities: prediction.probabilities || [],
        technicalCheck: technical,
        consensus,
        phase3: prediction.phase3 || { status: 'not_available' },
        lesionEvidence: prediction.lesion_evidence || { status: 'not_available' },
        needsReview: prediction.needs_review !== false,
        decisionReason: prediction.decision_reason || '研究推理草稿，需医生复核。'
      }
      if (consensus.status !== 'accept' || prediction.needs_review !== false) disagreementNotes.push((eye === 'OD' ? '右眼 OD' : '左眼 OS') + '：' + exam.eyes[eye].inference.decisionReason)
      updatedEyes.push(eye)
    })
    if (!updatedEyes.length) throw new Error('模型没有返回可用的逐眼推理结果')
    const allCollectedEyes = EYES.filter(eye => exam.eyes[eye].imageIds.some(id => find('images', id).modality === 'CFP'))
    const allQualityPassed = allCollectedEyes.length && allCollectedEyes.every(eye => exam.eyes[eye].quality.status === 'passed')
    exam.status = allQualityPassed ? 'awaiting_review' : 'pending_quality'
    const modelVersions = [...new Set(updatedEyes.map(eye => exam.eyes[eye].inference.modelVersion))]
    const draft = {
      id: 'DRAFT-' + examinationId,
      examinationId,
      patientId: patient.id,
      status: 'needs_review',
      source: 'algorithm7_local_api',
      modelVersion: modelVersions.join('；'),
      createdAt: new Date().toISOString(),
      eyeResults: clone(exam.eyes),
      disagreements: disagreementNotes,
      isSynthetic: false,
      researchOnly: true,
      notice: '由本机算法创新7接口生成的研究推理草稿，不能用于临床诊断或治疗决策。'
    }
    const existing = db.drafts.find(item => item.examinationId === examinationId)
    if (existing) Object.assign(existing, draft)
    else db.drafts.push(draft)
    patient.status = allQualityPassed ? '待医生复核' : '待补全质控'
    patient.tone = allQualityPassed ? 'warning' : 'info'
    patient.rightGrade = exam.eyes.OD.drGrade
    patient.leftGrade = exam.eyes.OS.drGrade
    onChange(db)
    return clone(bundle(patient.id, examinationId))
  }
  function submitReview(examinationId, review) {
    const exam = find('examinations', examinationId)
    const patient = find('patients', exam.patientId)
    const action = review.action
    const doctor = String(review.doctor || '').trim()
    const opinion = String(review.opinion || '').trim()
    const modificationReason = String(review.modificationReason || '').trim()
    if (!['accepted', 'modified', 'returned'].includes(action)) throw new Error('审核操作无效')
    if (!doctor) throw new Error('请填写审核医生')
    const collectedEyes = EYES.filter(eye => exam.eyes[eye].imageIds.some(id => find('images', id).modality === 'CFP'))
    if (!collectedEyes.length) throw new Error('当前检查未提供眼底彩照，不能提交医生审核')
    const allQualityPassed = collectedEyes.every(eye => exam.eyes[eye].quality.status === 'passed')
    const now = new Date().toISOString()
    const record = { id: 'REVIEW-' + examinationId + '-' + Date.now(), examinationId, reportId: null, actor: doctor, action: '', comment: opinion || '未填写审核意见。', createdAt: now, isSynthetic: true, decision: action, modificationReason, eyeResults: null }
    if (action === 'returned') {
      exam.status = 'awaiting_collection'
      exam.review = { action, doctor, opinion, modificationReason, updatedAt: now, signedAt: '' }
      record.action = '退回补采 / 重拍（演示）'
      db.reviewRecords.push(record)
      patient.status = '待补全采集'
      patient.tone = 'warning'
      onChange(db)
      return clone(bundle(patient.id, examinationId))
    }
    if (!allQualityPassed) throw new Error('当前存在需重拍、不可判读或设备未知的眼别，不能签发；请先补全采集资料。')
    const draft = db.drafts.find(item => item.examinationId === examinationId)
    if (action === 'accepted' && !draft) throw new Error('本次本地资料未调用模型，没有可接受的 AI 草稿；请改为医生修改分级后签发。')
    const eyeResults = clone(draft ? draft.eyeResults : exam.eyes)
    if (action === 'modified') {
      if (!modificationReason) throw new Error('修改分级时请填写修改原因')
      collectedEyes.forEach(eye => {
        const grade = review.eyeGrades && review.eyeGrades[eye]
        if (!Number.isInteger(grade) || grade < 0 || grade > 4) throw new Error('请为已采集的' + eye + '填写最终 ICDR 等级')
        eyeResults[eye].drGrade = grade
      })
    }
    if (!review.sign) {
      exam.status = 'awaiting_review'
      exam.review = { action, doctor, opinion, modificationReason, eyeResults, updatedAt: now, signedAt: '' }
      record.action = action === 'accepted' ? '接受草稿，待签发（演示）' : '修改分级，待签发（演示）'
      record.eyeResults = clone(eyeResults)
      db.reviewRecords.push(record)
      onChange(db)
      return clone(bundle(patient.id, examinationId))
    }
    const confirmedPlan = String(review.plan || '').trim()
    const planType = review.planType || 'followup'
    if (!confirmedPlan) throw new Error('请填写医生已确认的转诊 / 复查安排后再签发')
    if (!['followup', 'referral', 'both'].includes(planType)) throw new Error('转诊 / 复查类型无效')
    const dueAt = String(review.dueAt || '').trim() || null
    let reportDraft = draft
    if (!reportDraft) {
      reportDraft = { id: 'DRAFT-' + examinationId, examinationId, patientId: patient.id, status: 'manual', modelVersion: '医生人工分级（演示）', createdAt: now, eyeResults: clone(eyeResults), disagreements: [], isSynthetic: true }
      db.drafts.push(reportDraft)
    }
    const existing = db.reports.find(item => item.examinationId === examinationId && item.status === 'signed')
    const reportId = existing ? existing.id : 'REPORT-' + examinationId + '-' + Date.now()
    const researchInference = reportDraft.source === 'algorithm7_local_api'
    const report = { id: reportId, examinationId, patientId: patient.id, draftId: reportDraft.id, status: 'signed', version: existing ? existing.version + 1 : 1, signedBy: doctor, signedAt: now, eyeResults: clone(eyeResults), conclusion: opinion || (researchInference ? '本报告由本机研究模型草稿经人工确认后生成，仅供竞赛演示，不能用于临床诊断或治疗决策。' : '本报告为明确标记的演示签发记录，仅用于展示医生审核与签发流程。'), plan: confirmedPlan, planType, dueAt, isSynthetic: !researchInference, researchInference }
    if (existing) Object.assign(existing, report)
    else db.reports.push(report)
    exam.status = 'signed'
    exam.review = { action, doctor, opinion, modificationReason, eyeResults: clone(eyeResults), updatedAt: now, signedAt: now }
    record.reportId = reportId
    record.action = action === 'accepted' ? '接受草稿并签发（演示）' : '修改分级并签发（演示）'
    record.eyeResults = clone(eyeResults)
    db.reviewRecords.push(record)
    const existingTask = db.tasks.find(item => item.examinationId === examinationId && item.type === 'followup')
    if (!existingTask) db.tasks.push({ id: 'TASK-' + examinationId + '-' + Date.now(), key: 'followup', patientId: patient.id, examinationId, reportId, type: 'followup', title: planType === 'referral' ? '转诊联系与资料准备（演示）' : planType === 'both' ? '转诊与复查随访（演示）' : '复查联系与资料准备（演示）', description: confirmedPlan, icon: 'el-icon-date', status: 'pending_contact', note: '', dueAt, plan: confirmedPlan, planType, patientConfirmedAt: '', patientFeedback: '', patientFeedbackAt: '', updatedAt: now, isSynthetic: true })
    else Object.assign(existingTask, { reportId, title: planType === 'referral' ? '转诊联系与资料准备（演示）' : planType === 'both' ? '转诊与复查随访（演示）' : '复查联系与资料准备（演示）', description: confirmedPlan, dueAt, plan: confirmedPlan, planType, updatedAt: now })
    patient.status = '已签发'
    patient.tone = 'success'
    patient.rightGrade = eyeResults.OD.drGrade
    patient.leftGrade = eyeResults.OS.drGrade
    onChange(db)
    return clone(bundle(patient.id, examinationId))
  }
  return { db, find, context, bundle, portal, region, updatePatient, updateTask, createIntake, attachInference, submitReview, snapshot: () => clone(db) }
}
module.exports = { createRepository, assertGraph }
