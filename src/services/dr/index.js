import Vue from 'vue'
import { createFixtures } from '@/mock/dr/fixtures'
import { createRepository, assertGraph } from '@/mock/dr/repository'
import { EYES, GRADES, TASK_STATES, QUALITY_STATES, clone } from '@/mock/dr/schema'

const STORAGE_KEY = 'retina-dr-demo-v1'
export const storageState = Vue.observable({ available: true })
function initialData() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      assertGraph(parsed)
      return parsed
    }
  } catch (error) {
    storageState.available = false
  }
  return createFixtures()
}
function persist(data) {
  try { window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data)) } catch (error) { storageState.available = false }
}
export const repository = createRepository(initialData(), persist)
export const drState = Vue.observable(repository.db)
const response = operation => Promise.resolve().then(() => clone(operation()))
export const drService = {
  listPatients: () => response(() => drState.patients),
  getPatient: id => response(() => repository.find('patients', id)),
  getExamination: (patientId, examinationId) => response(() => repository.bundle(patientId, examinationId)),
  listExaminations: patientId => response(() => drState.examinations.filter(item => item.patientId === patientId)),
  getPatientService: patientId => response(() => repository.portal(patientId)),
  getRegion: () => response(() => repository.region()),
  updatePatient: (id, patch) => response(() => repository.updatePatient(id, patch)),
  updateTask: (id, patch) => response(() => repository.updateTask(id, patch)),
  createIntake: (patientId, form, files) => response(() => repository.createIntake(patientId, form, files))
}
export { EYES, GRADES, TASK_STATES, QUALITY_STATES, clone }
