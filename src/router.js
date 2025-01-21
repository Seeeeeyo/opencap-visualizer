import Vue from 'vue'
import VueRouter from 'vue-router'
import Session from '@/components/pages/Session'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Session
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
