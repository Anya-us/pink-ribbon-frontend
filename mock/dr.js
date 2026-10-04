const { createRepository } = require('../src/mock/dr/repository')
const repository = createRepository()
const endpoint = (url, type, operation) => ({
  url: '/dr/' + url + '(?:\\?.*)?$',
  type,
  response: config => {
    try { return { code: 20000, data: operation(config.query || {}, config.body || {}) } } catch (error) { return { code: 40000, message: error.message } }
  }
})
module.exports = [
  endpoint('patients', 'get', () => repository.snapshot().patients),
  endpoint('patient', 'get', query => repository.find('patients', query.patientId)),
  endpoint('examination', 'get', query => repository.bundle(query.patientId, query.examinationId)),
  endpoint('examinations', 'get', query => repository.db.examinations.filter(item => item.patientId === query.patientId)),
  endpoint('patient-service', 'get', query => repository.portal(query.patientId)),
  endpoint('region', 'get', () => repository.region())
]
