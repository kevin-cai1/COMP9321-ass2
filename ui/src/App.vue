<template>
  <div>
    <b-navbar toggleable="lg" type="dark" variant="primary">
      <b-navbar-brand href="#">FuelPredict</b-navbar-brand>
    </b-navbar>
    <div class="container" style="padding: 30px 0 0 0;">
    <div class="row">
      <div class="col-md-12">
        <h2>Fuel Pricing by Station</h2>
        <label>Start typing the name of a fuel station and the field will auto-complete</label>
      <v-autocomplete :items="items" v-model="item" :get-label="setLabel" :component-item="itemTemplate" @update-items="inputChange" @item-selected="itemSelected"></v-autocomplete>
      </div>
    </div>
    </div>
  </div>
</template>

<script>
import itemTemplate from './ItemTemplate.vue';
import Autocomplete from 'v-autocomplete';
export default {
  name: 'App',
  data: function() {
    return {
      item: {},
      itemTemplate,
      items: this.hardcodedStationList
    }
  },
  components: {
    'v-autocomplete': Autocomplete
  },
  props: {
    hardcodedStationList: Array
  },
  methods: {
    itemSelected (item) {
      this.item = item;
    },
    setLabel (item) {
      return item.name;
    },
    inputChange (text) {
      // your search method
      this.items = this.hardcodedStationList.filter(item => item.name.toLowerCase().includes(text.toLowerCase()));
      // now `items` will be showed in the suggestion list
    },
  }
}
</script>

<style lang="stylus">
.v-autocomplete
  .v-autocomplete-input-group
    .v-autocomplete-input
      padding 10px 15px
      box-shadow none
      border 1px solid #428bca
      width calc(100%)
      outline none
      background-color #eee
    &.v-autocomplete-selected
      .v-autocomplete-input
        color green
        background-color #f2fff2
  .v-autocomplete-list
    width 100%
    text-align left
    border none
    border-top none
    max-height 400px
    overflow-y auto
    border-bottom 1px solid #157977
    .v-autocomplete-list-item
      cursor pointer
      background-color #fff
      padding 10px
      border-bottom 1px solid #157977
      border-left 1px solid #157977
      border-right 1px solid #157977
      &:last-child
        border-bottom none
      &:hover
        background-color #eee
      abbr
        opacity 0.8
        font-size 0.8em
        display block
        font-family sans-serif
</style>