<template>
  <canvas id="boundingBoxCanvas" :width="width+'px'" :height="height+'px'"></canvas>
</template>

<script>
  import paper, { Path, Point, Tool, PointText } from 'paper'

  const BoundingBoxDiagram = {
    components: {},
    props: ['bboxData', 'timestamp'],
    data() {
      return {
        scope: null,
        bbox: null,
        width: 320,
        height: 302,
      }
    },
    mounted() {
      this.scope = new paper.PaperScope()
      this.scope.setup('boundingBoxCanvas')
      this.reset()
      this.drawBoundingBox()
    },
    watch: {
      bboxData() {
        this.drawBoundingBox()
      }
    },
    methods: {
      reset() {
          this.scope.project.activeLayer.removeChildren()
          this.scope.activate()
          // x-axis
          new Path.Line({
            from: [0, this.height / 2],
            to: [this.width, this.height / 2],
            strokeColor: 'black',
            strokeWidth: .5,
          })
          // y-axis
          new Path.Line({
            from: [this.width / 2, 0],
            to: [this.width / 2, this.height],
            strokeColor: 'black',
            strokeWidth: .5,
          })
          let tick_width = 50
          let tick_height = 50
          let x_ticks = Math.trunc(this.width / tick_width) + 1
          let y_ticks = Math.trunc(this.height / tick_height) + 1
          // vertical lines
          for (let x = 0; x < x_ticks; x++) {
            new Path.Line({
              from: [this.width/2 + tick_width*(-Math.trunc(x_ticks/2)+x), 0],
              to: [this.width/2 + tick_width*(-Math.trunc(x_ticks/2)+x), this.height],
              strokeColor: 'black',
              strokeWidth: .5,
              opacity: .2,
            })
          }
          // horiz lines
          for (let y = 0; y < y_ticks; y++) {
            new Path.Line({
              from: [0, this.height/2 + tick_height*(-Math.trunc(y_ticks/2)+y)],
              to: [this.width, this.height/2 + tick_height*(-Math.trunc(y_ticks/2)+y)],
              strokeColor: 'black',
              strokeWidth: .5,
              opacity: .2,
            })
          }
      },
      drawBoundingBox() {
        this.scope.activate()
        if (this.bbox) {
          this.bbox.remove()
        }
        this.bbox = new Path.Rectangle({
          point: [this.bboxData.x, this.bboxData.y],
          size: [this.bboxData.w, this.bboxData.h],
          fillColor: 'red',
          opacity: .4,
          strokeColor: 'black',
        })
        console.table('bounding box delay: ' + Math.trunc(Date.now() - this.timestamp * 1000) + 'ms')
      },
      createTool(scope) {
          scope.activate();
          return new Tool();
      },
    }
  }

  export default BoundingBoxDiagram;
</script>