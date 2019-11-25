<template>
  <div>
    <b-navbar toggleable="lg" type="dark" variant="primary">
      <b-navbar-brand href="/">FuelPredict</b-navbar-brand>
      <b-collapse id="nav-collapse" is-nav>
        <b-navbar-nav>
          <b-nav-item href="/predictByStation">Predict By Station</b-nav-item>
          <b-nav-item href="/predictBySuburb">Predict By Suburb</b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
    <div class="container" style="padding: 30px 0 0 0;">
    <router-view><h1>Fuel Predict Homepage</h1></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>