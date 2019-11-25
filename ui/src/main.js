import Vue from 'vue'
import App from './App.vue'
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import stationList from './stations'
import * as VueGoogleMaps from 'vue2-google-maps'

import FuelPredictByStation from './components/FuelPredictByStation.vue'
import FuelPredictBySuburb from './components/PredictionBySuburb.vue'

Vue.config.productionTip = false
// Vue.config.js.runtimeCompiler = true
Vue.use(BootstrapVue)

import Autocomplete from 'v-autocomplete'

import 'v-autocomplete/dist/v-autocomplete.css'

Vue.use(Autocomplete)

import 'vue-suggestion/dist/vue-suggestion.css'
import VueRouter from 'vue-router'

const routes = [
  {path: '/predictByStation', component: FuelPredictByStation, props: {hardcodedStationList: stationList}},
  {path: '/predictBySuburb', component: FuelPredictBySuburb}
]

const router = new VueRouter({
  routes,
  mode: 'history'
})

Vue.use(VueRouter)

Vue.use(VueGoogleMaps, {
  load: {
    key: 'AIzaSyARbPDMOjgywxNnHQ3c6PMTV-Wr5diWbZA',
    libraries: 'places'
  },
  installComponents: true
})

new Vue({
  router,
  el: '#app',
  render: h => h(App)
})
