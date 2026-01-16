import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import router from '@/router'
import axios from 'axios'
import 'roboto-fontface/css/roboto/roboto-fontface.css'
import '@mdi/font/css/materialdesignicons.css'
import '@/assets/scss/main.scss'

import registerFilters from './util/Filters';
registerFilters(Vue)

// vee-validate 3
import { ValidationProvider, ValidationObserver, extend } from "vee-validate";
import { required, confirmed, min, email, alpha_dash } from "vee-validate/dist/rules";

// fa-icons
import '@fortawesome/fontawesome-free/css/all.css';

import VueSocialSharing from 'vue-social-sharing'

Vue.use(VueSocialSharing);

// Set favicon using @ alias
const faviconLink = document.querySelector("link[rel='icon']") || document.createElement('link')
faviconLink.rel = 'icon'
faviconLink.href = require('@/assets/favicon.png')
if (!document.querySelector("link[rel='icon']")) {
  document.head.appendChild(faviconLink)
} else {
  document.querySelector("link[rel='icon']").href = require('@/assets/favicon.png')
}

// Set Open Graph thumbnail using @ alias
const thumbnailUrl = require('@/assets/thumbnail-visualizer.png')
const ogImageMeta = document.querySelector("meta[property='og:image']")
const twitterImageMeta = document.querySelector("meta[name='twitter:image']")
if (ogImageMeta) {
  ogImageMeta.setAttribute('content', thumbnailUrl)
}
if (twitterImageMeta) {
  twitterImageMeta.setAttribute('content', thumbnailUrl)
}

// Add rules
extend('required', required)
extend('confirmed', confirmed)
extend('min', min)
extend('email', email)
extend('alpha_dash', alpha_dash)

// Custom rules
extend('no_spaces', {
  validate (value, args) {
    return value.indexOf(' ') < 0
  },
  message: 'Spaces not allowed'
})
extend('alpha_dash_custom', {
  validate (value, args) {
    var regexp = /^[a-zA-Z0-9-_]+$/;
    if (value.search(regexp) === -1)
        return false
    else
        return true
  },
  message: 'Only alphanumeric, hyphen and underscore characters allowed.'
})
extend('unique_trial_name', {
  validate (value, { trials, ignore_name }) {
    let trial_names = trials.map(trial => trial.name)
    if (ignore_name && value === ignore_name) {
      return true
    }
    return trial_names.indexOf(value) === -1
  },
  params: ['trials', 'ignore_name'],
  message: 'A trial with this name already exists in the session. Please choose a different name.'
})

Vue.component("ValidationProvider", ValidationProvider);
Vue.component("ValidationObserver", ValidationObserver);

import Toasted from 'vue-toasted'
import './registerServiceWorker'
Vue.use(Toasted, { 
  position: 'bottom-center', 
  duration: 1000,
  className: 'vue-toasted',
  // Show all toasts with Close button
  action : {
    text : 'Close',
    onClick : (e, toastObject) => {
        toastObject.goAway(0)
    }
  }
})

Vue.toasted.register('warning', (message) => {
  Vue.toasted.show(message, {
    type: 'warning',
    theme: 'toasted-primary',
    position: 'top-right',
    className: 'warning-toast'
  });
});

Vue.config.productionTip = false

new Vue({
  router,
  vuetify,
  render: h => h(App)
}).$mount('#app')

