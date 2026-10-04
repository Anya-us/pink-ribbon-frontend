import Vue from 'vue'
import Router from 'vue-router'
import Layout from '@/layout'
import { Message } from 'element-ui'
import drRoutes from './modules/dr'
import { resolveContext, selectContext } from '@/data/retina-demo'

Vue.use(Router)
const redirectTo = path => to => ({ path, query: to.query })
export const constantRoutes = [
  { path: '/login', component: () => import('@/views/login/index'), hidden: true },
  { path: '/404', component: () => import('@/views/error-page/404'), hidden: true },
  { path: '/homepage', redirect: '/dashboard', hidden: true },
  { path: '/redirect', component: Layout, hidden: true, children: [{ path: '/redirect/:path(.*)', component: () => import('@/views/redirect/index') }] },
  { path: '/', component: Layout, redirect: '/dashboard', children: [{ path: 'dashboard', component: () => import('@/views/dashboard/index'), name: 'Dashboard', meta: { title: '诊疗工作台', icon: 'el-icon-s-home', affix: true }}] }
]
export const asyncRoutes = [
  ...drRoutes,
  ...[
    ['/personal', '/patients/index'], ['/personal/index', '/patients/index'],
    ['/prediction', '/screening/intake'], ['/prediction/input', '/screening/intake'],
    ['/prediction/assess', '/screening/consensus'], ['/prediction/subtype', '/screening/evidence'],
    ['/advice', '/followup/index'], ['/advice/index', '/followup/index'],
    ['/chat', '/patient/help'], ['/chat/index', '/patient/help']
  ].map(([path, target]) => ({ path, redirect: redirectTo(target), hidden: true })),
  { path: '*', redirect: '/404', hidden: true }
]
const createRouter = () => new Router({ scrollBehavior: () => ({ y: 0 }), routes: constantRoutes })
const router = createRouter()
router.beforeResolve((to, from, next) => {
  if (!to.meta.drContext) return next()
  try {
    const { patient, examination } = resolveContext(to.query)
    selectContext(patient.id, examination.id)
    if (to.query.patientId !== patient.id || to.query.examinationId !== examination.id) {
      return next({ path: to.path, query: { ...to.query, patientId: patient.id, examinationId: examination.id }, replace: true })
    }
    next()
  } catch (error) {
    Message.error(error.message)
    next('/404')
  }
})
export function resetRouter() { router.matcher = createRouter().matcher }
export default router
