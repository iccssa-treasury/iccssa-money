<script lang="ts">
export default {};
</script>

<template>
  <div class="banner">
    <div class="center">
      <!-- <h1 class="ui header">帝国财务</h1> -->
    </div>
  </div>
</template>

<style scoped>
.banner {
  min-height: 100%;
  width: 100%;
  background-image: url('@/assets/imperial.jpeg'); 
  background-size: cover;
  background-position: 30% 40%;
}

.banner h1.ui.header {
  font-size: 60px;
  font-weight: 400;
}

.banner .center {
  padding: 1em 0;
  min-height: 80vh;
  margin: 0 auto;
  text-align: center;
}

@media screen and (max-width: 1200px) {
  .banner h1.ui.header {
    font-size: 54px;
  }
}

@media screen and (max-width: 991px) {
  .banner h1.ui.header {
    font-size: 50px;
  }
}

@media screen and (max-width: 767px) {
  .banner h1.ui.header {
    font-size: 50px;
  }
}

@media screen and (max-width: 479px) {
  .banner h1.ui.header {
    font-size: 48px;
  }
}

@media screen and (max-width: 379px) {
  .banner h1.ui.header {
    font-size: 40px;
  }
}
</style>
