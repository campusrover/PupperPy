<template>
  <canvas
    id="sensorCanvas"
    :width="width+'px'"
    :height="height+'px'"
  />
</template>

<script>
import paper, { Path, Point, Tool, Group } from 'paper'

const SensorDiagram = {
  components: {},
  props: ['sensorData', 'yaw', 'timestamp'],
  data () {
    return {
      scope: null,
      leftSensor: null,
      centerSensor: null,
      rightSensor: null,
      robotGroup: null,
      width: 250,
      height: 250,
    }
  },
  mounted () {
    this.scope = new paper.PaperScope()
    this.scope.setup('sensorCanvas')
    this.reset()
  },
  watch: {
    sensorData () {
      this.updateRangeSensors()
      this.updateYaw()
    },
  },
  methods: {
    reset () {
      this.scope.project.activeLayer.removeChildren()
      this.scope.activate()
      // radial axes
      const numAxes = 8
      for (let i = 0; i < numAxes; i++) {
        const axis = new Path.Line({
          from: [this.width / 2, this.height / 2],
          to: [this.width / 2, -this.height],
          strokeColor: 'black',
          opacity: 0.2,
        })
        axis.rotate(i * 360 / numAxes, new Point(this.width / 2, this.height / 2))
      }
      // forward arrow
      const arrowW = 10
      const arrowH = 10
      const forwardArrow = new Path.Line({
        from: [this.width / 2, this.height / 2],
        to: [this.width / 2, 0],
        strokeColor: 'black',
      })
      forwardArrow.add({ point: [this.width / 2 - arrowW / 2, arrowH] })
      forwardArrow.add({ point: [this.width / 2, 0] })
      forwardArrow.add({ point: [this.width / 2 + arrowW / 2, arrowH] })
      // robot body
      const robotW = 60
      const robotH = 1.5 * robotW
      const robot = new Path.Rectangle({
        point: [(this.width - robotW) / 2, (this.height - robotH) / 2],
        size: [robotW, robotH],
        fillColor: 'black',
        opacity: 0.5,
      })
      // robot group
      this.robotGroup = new Group([forwardArrow, robot])
      this.robotGroup.applyMatrix = false
      // proximity sensors
      const sensorW = 10
      const sensorH = 2 * sensorW
      this.leftSensor = new Path.Rectangle({
        point: [10, 10],
        size: [sensorW, sensorH],
        fillColor: 'rgba(15, 234, 0)',
        opacity: 1,
      })
      this.centerSensor = new Path.Rectangle({
        point: [sensorW * 2 + 10, 10],
        size: [sensorW, sensorH],
        fillColor: 'rgba(15, 234, 0)',
        opacity: 1,
      })
      this.rightSensor = new Path.Rectangle({
        point: [sensorW * 4 + 10, 10],
        size: [sensorW, sensorH],
        fillColor: 'rgba(15, 234, 0)',
        opacity: 1,
      })
    },
    updateRangeSensors () {
      this.scope.activate()
      const { leftObj, centerObj, rightObj } = this.sensorData
      this.updateRangeSensor(this.leftSensor, leftObj === 'True')
      this.updateRangeSensor(this.centerSensor, centerObj === 'True')
      this.updateRangeSensor(this.rightSensor, rightObj === 'True')
      console.table('range sensor delay: ' + Math.trunc(Date.now() - this.timestamp * 1000) + 'ms')
    },
    updateYaw () {
      if (this.yaw == null) return
      this.robotGroup.rotate(-this.robotGroup.rotation, new Point(this.width / 2, this.height / 2))
      this.robotGroup.rotate(this.yaw, new Point(this.width / 2, this.height / 2))
    },
    updateRangeSensor (sensor, value) {
      if (value) {
        sensor.fillColor = 'red'
      } else {
        sensor.fillColor = 'rgba(15, 234, 0)'
      }
    },
    createTool (scope) {
      scope.activate()
      return new Tool()
    },
  },
}

export default SensorDiagram
</script>
