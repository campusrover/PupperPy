<template>
  <canvas id="sensorCanvas" :width="width+'px'" :height="height+'px'"></canvas>
</template>

<script>
  import paper, { Path, Point, Tool, Group } from 'paper'

  const SensorDiagram = {
    components: {},
    props: ['sensorData', 'yaw', 'timestamp'],
    data() {
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
    mounted() {
      this.scope = new paper.PaperScope()
      this.scope.setup('sensorCanvas')
      this.reset()
    },
    watch: {
      sensorData() {
        this.updateRangeSensors()
        this.updateYaw()
      }
    },
    methods: {
      reset() {
        this.scope.project.activeLayer.removeChildren()
        this.scope.activate()
        // radial axes
        let num_axes = 8
        for (let i = 0; i < num_axes; i++) {
          let axis = new Path.Line({
            from: [this.width/2, this.height/2],
            to: [this.width/2, -this.height],
            strokeColor: 'black',
            opacity: .2
          })
          axis.rotate(i * 360 / num_axes, new Point(this.width/2, this.height/2))
        }
        // forward arrow
        let arrow_w = 10
        let arrow_h = 10
        let forward_arrow = new Path.Line({
          from: [this.width/2, this.height/2],
          to: [this.width/2, 0],
          strokeColor: 'black',
        })
        forward_arrow.add({point: [this.width/2 - arrow_w/2, arrow_h]})
        forward_arrow.add({point: [this.width/2, 0]})
        forward_arrow.add({point: [this.width/2 + arrow_w/2, arrow_h]})
        // robot body
        let robot_w = 60
        let robot_h = 1.5 * robot_w
        let robot = new Path.Rectangle({
          point: [(this.width - robot_w) / 2, (this.height - robot_h) / 2],
          size: [robot_w, robot_h],
          fillColor: 'black',
          opacity: .5,
        })
        // robot group
        this.robotGroup = new Group([forward_arrow, robot])
        this.robotGroup.applyMatrix = false
        // proximity sensors
        let sensor_w = 10
        let sensor_h = 2 * sensor_w
        this.leftSensor = new Path.Rectangle({
          point: [10, 10],
          size: [sensor_w, sensor_h],
          fillColor: 'rgba(15, 234, 0)',
          opacity: 1,
        })
        this.centerSensor = new Path.Rectangle({
          point: [sensor_w * 2 + 10, 10],
          size: [sensor_w, sensor_h],
          fillColor: 'rgba(15, 234, 0)',
          opacity: 1,
        })
        this.rightSensor = new Path.Rectangle({
          point: [sensor_w * 4 + 10, 10],
          size: [sensor_w, sensor_h],
          fillColor: 'rgba(15, 234, 0)',
          opacity: 1,
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
      updateYaw() {
        this.robotGroup.rotate(-this.robotGroup.rotation, new Point(this.width/2, this.height/2))
        this.robotGroup.rotate(this.yaw, new Point(this.width/2, this.height/2))
      },
      updateRangeSensor(sensor, value) {
        if (value) {
          sensor.fillColor = 'red'
        } else {
          sensor.fillColor = 'rgba(15, 234, 0)'
        }
      },
      createTool(scope) {
        scope.activate();
        return new Tool();
      },
    }
  }

  export default SensorDiagram;
</script>