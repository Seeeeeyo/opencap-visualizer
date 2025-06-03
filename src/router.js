import Vue from 'vue'
import VueRouter from 'vue-router'
import Session from '@/components/pages/Session'
// import HeadlessRenderer from '@/components/pages/HeadlessRenderer'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Session
  },
  {
    path: '/samples',
    name: 'Samples',
    component: Session
  },

]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
