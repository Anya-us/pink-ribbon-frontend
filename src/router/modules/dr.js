import Layout from '@/layout'
const leaf = (path, name, title, icon, component, drContext = true) => ({ path, name, component, meta: { title, icon, drContext }})
export default [
  { path: '/patients', component: Layout, redirect: '/patients/index', children: [leaf('index', 'Personal', '患者档案', 'el-icon-user', () => import('@/views/personal/index'))] },
  { path: '/screening', component: Layout, redirect: '/screening/intake', meta: { title: '筛查采集', icon: 'el-icon-view' }, children: [
    leaf('intake', 'Input', '影像与数据采集', 'el-icon-upload2', () => import('@/views/prediction/input/index')),
    leaf('consensus', 'Assess', '质控与共识草稿', 'el-icon-connection', () => import('@/views/prediction/assess/index')),
    leaf('evidence', 'Subtype', '双眼分级与证据', 'el-icon-document', () => import('@/views/prediction/subtype/index'))
  ] },
  { path: '/review', component: Layout, redirect: '/review/index', children: [leaf('index', 'DoctorReview', '医生审核', 'el-icon-document-checked', () => import('@/views/review/index'))] },
  { path: '/followup', component: Layout, redirect: '/followup/index', children: [leaf('index', 'Advice', '转诊与随访', 'el-icon-date', () => import('@/views/advice/index'))] },
  { path: '/patient', component: Layout, redirect: '/patient/index', children: [
    leaf('index', 'PatientService', '患者服务', 'el-icon-chat-dot-round', () => import('@/views/patient/index')),
    { ...leaf('help', 'Chat', '眼健康助手', 'el-icon-question', () => import('@/views/chat/index')), hidden: true }
  ] },
  { path: '/region', component: Layout, redirect: '/region/index', children: [leaf('index', 'RegionDashboard', '区域看板', 'el-icon-data-analysis', () => import('@/views/region/index'), false)] }
]
