import Vue from 'vue'
import App from './App.vue'
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import stationList from './stations'

import FuelPredictByStation from './components/FuelPredictByStation.vue'

Vue.config.productionTip = false
// Vue.config.js.runtimeCompiler = true
Vue.use(BootstrapVue)

import Autocomplete from 'v-autocomplete'

import 'v-autocomplete/dist/v-autocomplete.css'

Vue.use(Autocomplete)

import 'vue-suggestion/dist/vue-suggestion.css'
import VueRouter from 'vue-router'

const routes = [
  // {path: '/', component: App, children: [
  //   {path: 'predictByStation', component: FuelPredictByStation, props: {hardcodedStationList: stationList}}
  // ]}
  {path: '/predictByStation', component: FuelPredictByStation, props: {hardcodedStationList: stationList}}
]

const router = new VueRouter({
  routes,
  mode: 'history'
})

Vue.use(VueRouter)

new Vue({
  router,
  el: '#app',
  render: h => h(App)
})
