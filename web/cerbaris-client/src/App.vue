<template>
  <div id="app">
    <sensor-panel></sensor-panel>
    <div class="d-flex flex-wrap flex-lg-nowrap">
      <vision-panel class="flex-fill"></vision-panel>
      <state-panel class="flex-fill"></state-panel>
    </div>
    <behavior-tree-diagram></behavior-tree-diagram>
  </div>
</template>

<script>
  import Pusher from 'pusher-js';
  import SensorPanel from '@/components/SensorPanel'
  import VisionPanel from '@/components/VisionPanel'
  import StatePanel from '@/components/StatePanel'
  import BehaviorTreeDiagram from '@/components/BehaviorTreeDiagram'

  const App = {
    components: {SensorPanel, VisionPanel, StatePanel, BehaviorTreeDiagram},
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
