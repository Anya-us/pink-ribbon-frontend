/** When your routing table is too long, you can split it into small modules **/

import Layout from '@/layout'

const predictionRouter = {
  path: '/prediction',
  component: Layout,
  redirect: 'noRedirect',
  name: 'Prediction',
  meta: {
    title: '疾病预测',
    icon: 'el-icon-s-marketing'
  },
  children: [
    {
      path: 'input',      
      name: 'Input',
      component: () => import('@/views/prediction/input/index'), 
      meta: { title: '数据录入', icon: 'el-icon-edit' }
    },
    {
      path: 'assess',
      name: 'Assess',
      component: () => import('@/views/prediction/assess/index'),
      meta: { title: '风险评估', icon: 'el-icon-warning-outline' }
    },
    {
      path: 'subtype',
      name: 'Subtype',
      component: () => import('@/views/prediction/subtype/index'),
      meta: { title: '亚型预测', icon: 'el-icon-document'}
    }
  ]
}

export default predictionRouter
