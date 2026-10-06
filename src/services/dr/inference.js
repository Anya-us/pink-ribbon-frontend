import axios from 'axios'

const inferenceClient = axios.create({
  baseURL: process.env.VUE_APP_DR_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 120000
})

function responseError(error) {
  const detail = error && error.response && error.response.data && error.response.data.detail
  if (detail) return new Error(detail)
  if (error && error.code === 'ECONNABORTED') return new Error('模型推理超时，请确认后端仍在运行。')
  return new Error('无法连接本机推理服务。请先运行“启动演示.cmd”，并保持推理服务窗口开启。')
}

export async function predictFundusImage(file) {
  if (!file || !file.raw) throw new Error('未找到可用于推理的眼底彩照，请重新选择文件。')
  const body = new FormData()
  body.append('image', file.raw, file.name)
  try {
    const response = await inferenceClient.post('/api/ai/predict', body)
    if (!response.data || !response.data.success || !response.data.result) throw new Error('推理服务没有返回有效结果。')
    return response.data.result
  } catch (error) {
    if (error && error.message === '推理服务没有返回有效结果。') throw error
    throw responseError(error)
  }
}

export async function predictFundusEyes(files) {
  const eyes = Object.keys(files)
  const values = await Promise.all(eyes.map(async eye => [eye, await predictFundusImage(files[eye])]))
  return values.reduce((result, [eye, prediction]) => ({ ...result, [eye]: prediction }), {})
}
