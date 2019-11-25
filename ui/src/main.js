import Vue from 'vue'
import App from './App.vue'
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import stationList from './stations'

Vue.config.productionTip = false
// Vue.config.js.runtimeCompiler = true
Vue.use(BootstrapVue)

import Autocomplete from 'v-autocomplete'

import 'v-autocomplete/dist/v-autocomplete.css'

Vue.use(Autocomplete)

import 'vue-suggestion/dist/vue-suggestion.css'

new Vue({
  el: '#app',
  template: '<App />',
  components: {App},
  render: h => h(App, {
    props: {
      hardcodedStationList: stationList
    }
  })
})
