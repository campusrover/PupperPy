<template>
  <div id="app">
    <sensor-panel></sensor-panel>
    <div class="d-flex flex-wrap flex-md-nowrap">
      <vision-panel class="flex-fill"></vision-panel>
      <state-panel class="flex-fill"></state-panel>
    </div>
  </div>
</template>

<script>
  import Pusher from 'pusher-js';
  import SensorPanel from '@/components/SensorPanel'
  import VisionPanel from '@/components/VisionPanel'
  import StatePanel from '@/components/StatePanel'

  const App = {
    components: {SensorPanel, VisionPanel, StatePanel},
  }

  export default App;
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

canvas {
  border: .5px solid gray;
}

.card {
  margin: .5em;
}
</style>
