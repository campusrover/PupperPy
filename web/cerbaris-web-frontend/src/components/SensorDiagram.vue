<template>
  <canvas id="sensorCanvas" :width="width+'px'" :height="height+'px'"></canvas>
</template>

<script>
  import paper, { Path, Point, Tool } from 'paper'

  const BoundingBoxCanvas = {
    components: {},
    props: ['sensorData', 'timestamp'],
    data() {
      return {
        scope: null,
        leftSensor: null,
        centerSensor: null,
        rightSensor: null,
        width: 300,
        height: 300,
      }
    },
    mounted() {
      this.scope = new paper.PaperScope()
      this.scope.setup('sensorCanvas')
      this.reset()
    },
    watch: {
      sensorData() {
        this.updateRangeSensors()
      }
    },
    methods: {
      reset() {
        this.scope.project.activeLayer.removeChildren()
        this.scope.activate()
        this.leftSensor = new Path.Rectangle({
          point: [this.width / 3, this.height / 2],
          size: [20, 20],
          fillColor: 'green',
          strokeColor: 'black',
          opacity: .4,
        })
        this.centerSensor = new Path.Rectangle({
          point: [this.width / 2, this.height / 2],
          size: [20, 20],
          fillColor: 'green',
          strokeColor: 'black',
          opacity: .4,
        })
        this.rightSensor = new Path.Rectangle({
          point: [2 * this.width / 3, this.height / 2],
          size: [20, 20],
          fillColor: 'green',
          strokeColor: 'black',
          opacity: .4,
        })
      },
      updateRangeSensors() {
        this.scope.activate()
        let {left_obj, center_obj, right_obj} = this.sensorData
        this.updateRangeSensor(this.leftSensor, left_obj === 'True')
        this.updateRangeSensor(this.centerSensor, center_obj === 'True')
        this.updateRangeSensor(this.rightSensor, right_obj === 'True')
        console.table('range sensor delay: ' + Math.trunc(Date.now() - this.timestamp * 1000) + 'ms')
      },
      updateRangeSensor(sensor, value) {
        if (value) {
          sensor.fillColor = 'red'
        } else {
          sensor.fillColor = 'green'
        }
      },
      createTool(scope) {
          scope.activate();
          return new Tool();
      },
    }
  }

  export default BoundingBoxCanvas;
</script>