import Vue from 'vue'
import { repository, drState, GRADES } from '@/services/dr'

export const patients = drState.patients
export const grades = GRADES
const CONTEXT_KEY = 'retina-dr-context-v1'
function previousContext() {
  try {
    const saved = JSON.parse(window.localStorage.getItem(CONTEXT_KEY))
    if (saved) return repository.context(saved.patientId, saved.examinationId)
  } catch (error) { /* Fall back only when there is no explicit route context. */ }
  return repository.context(patients[0].id)
}
const initial = previousContext()
export const demoState = Vue.observable({
  patient: initial.patient,
  examinationId: initial.examination.id,
  intake: initial.examination.sourceType === 'local' ? { examinationId: initial.examination.id, savedAt: initial.examination.performedAt } : null,
  files: {},
  profileNote: initial.patient.note,
  taskStates: {}
})
export function gradeInfo(code) {
  return grades.find(item => item.code === code) || { label: '未评估', short: '未评估', tone: '' }
}
export function currentBundle() {
  return repository.bundle(demoState.patient.id, demoState.examinationId)
}
export function clearFiles() {
  Object.values(demoState.files).forEach(file => { if (file.url) URL.revokeObjectURL(file.url) })
  demoState.files = {}
}
function rememberContext() {
  try { window.localStorage.setItem(CONTEXT_KEY, JSON.stringify({ patientId: demoState.patient.id, examinationId: demoState.examinationId })) } catch (error) { /* The URL remains the source of route context. */ }
}
export function selectContext(patientId, examinationId) {
  const context = repository.context(patientId, examinationId)
  if (demoState.patient.id !== context.patient.id || demoState.examinationId !== context.examination.id) clearFiles()
  demoState.patient = context.patient
  demoState.examinationId = context.examination.id
  demoState.intake = context.examination.sourceType === 'local' ? { examinationId: context.examination.id, savedAt: context.examination.performedAt } : null
  demoState.profileNote = context.patient.note
  demoState.taskStates = {}
  rememberContext()
  return context
}
export function selectPatient(patient) {
  clearFiles()
  return selectContext(patient.id, patient.currentExaminationId)
}
export function resolveContext(query = {}) {
  const patientId = query.patientId
  const examinationId = query.examinationId
  if ((patientId !== undefined && (typeof patientId !== 'string' || !patientId)) || (examinationId !== undefined && (typeof examinationId !== 'string' || !examinationId))) throw new Error('病例链接中的编号无效')
  if (examinationId && !patientId) {
    const exam = repository.find('examinations', examinationId)
    return repository.context(exam.patientId, examinationId)
  }
  return repository.context(patientId || demoState.patient.id, examinationId || (patientId ? undefined : demoState.examinationId))
}
export function contextQuery(examinationId = demoState.examinationId) {
  return { patientId: demoState.patient.id, examinationId }
}
export function setFile(key, file) {
  const previous = demoState.files[key]
  if (previous && previous.url) URL.revokeObjectURL(previous.url)
  if (!file) { Vue.delete(demoState.files, key); return }
  Vue.set(demoState.files, key, { name: file.name, size: file.size, type: file.type, url: /\.(jpe?g|png)$/i.test(file.name) ? URL.createObjectURL(file) : '' })
}
export function updatePatient(patch) {
  repository.updatePatient(demoState.patient.id, patch)
  demoState.profileNote = demoState.patient.note
}
export function saveIntake(form) {
  const exam = repository.createIntake(demoState.patient.id, { ...form, note: form.notes || '' }, demoState.files)
  demoState.examinationId = exam.id
  demoState.intake = { ...form, examinationId: exam.id, fileKeys: Object.keys(demoState.files), savedAt: exam.performedAt }
  rememberContext()
}
export function setTaskState(key, value) {
  const task = drState.tasks.find(item => item.patientId === demoState.patient.id && item.examinationId === demoState.examinationId && (item.id === key || item.key === key))
  if (!task) throw new Error('当前检查没有对应任务')
  repository.updateTask(task.id, { status: 'self_reported', note: value.note || '' })
  Vue.set(demoState.taskStates, key, value)
}
