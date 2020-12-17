<template>
  <div id="app">
    <p class="m-3">
      Press enter to toggle between panels and tree diagram
    </p>
    <sensor-panel class="toggle-enter" />
    <div class="d-flex flex-wrap flex-lg-nowrap">
      <vision-panel class="toggle-enter flex-fill" />
      <state-panel class="toggle-enter flex-fill" />
    </div>
    <tree class="d-none-on-mount toggle-enter" />
  </div>
</template>

<script>
import SensorPanel from '@/components/SensorPanel'
import VisionPanel from '@/components/VisionPanel'
import StatePanel from '@/components/StatePanel'
import Tree from '@/components/Tree'

const App = {
  components: { SensorPanel, VisionPanel, StatePanel, Tree },
  mounted () {
    Array.from(document.querySelectorAll('.d-none-on-mount')).forEach(elt => {
      elt.classList.add('d-none')
    })
    document.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        Array.from(document.querySelectorAll('.toggle-enter')).forEach(elt => {
          elt.classList.toggle('d-none')
        })
      }
    })
  },
}

export default App
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
