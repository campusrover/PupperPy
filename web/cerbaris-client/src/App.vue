<template>
  <div id="app">
    <p class="m-3">Press enter to toggle between panels and behavior tree</p>
    <sensor-panel class="toggle-enter"></sensor-panel>
    <div class="d-flex flex-wrap flex-lg-nowrap">
      <vision-panel class="toggle-enter flex-fill"></vision-panel>
      <state-panel class="toggle-enter flex-fill"></state-panel>
    </div>
    <behavior-tree-diagram class="d-none-on-mount toggle-enter"></behavior-tree-diagram>
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
    mounted() {
      Array.from(document.querySelectorAll('.d-none-on-mount')).forEach(elt => {
        elt.classList.add('d-none')
      })
      document.onkeydown = function(e) {
        if (e.key === 'Enter') {
          Array.from(document.querySelectorAll('.toggle-enter')).forEach(elt => {
            elt.classList.toggle('d-none')
          })
        }
      }
    },
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
