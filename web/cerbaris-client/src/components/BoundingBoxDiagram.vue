<template>
  <canvas
    id="boundingBoxCanvas"
    :width="width+'px'"
    :height="height+'px'"
  />
</template>

<script>
import paper, { Path } from 'paper'

const BoundingBoxDiagram = {
  components: {},
  props: ['bboxData', 'timestamp'],
  data () {
    return {
      scope: null,
      bbox: null,
      width: 320,
      height: 302,
    }
  },
  mounted () {
    this.scope = new paper.PaperScope()
    this.scope.setup('boundingBoxCanvas')
    this.reset()
    this.drawBoundingBox()
  },
  watch: {
    bboxData () {
      this.drawBoundingBox()
    },
  },
  methods: {
    reset () {
      this.scope.project.activeLayer.removeChildren()
      this.scope.activate()
      // x-axis
      new Path.Line({
        from: [0, this.height / 2],
        to: [this.width, this.height / 2],
        strokeColor: 'black',
        strokeWidth: 0.5,
      })
      // y-axis
      new Path.Line({
        from: [this.width / 2, 0],
        to: [this.width / 2, this.height],
        strokeColor: 'black',
        strokeWidth: 0.5,
      })
      const tickW = 50
      const tickH = 50
      const xTicks = Math.trunc(this.width / tickW) + 1
      const yTicks = Math.trunc(this.height / tickH) + 1
      // vertical lines
      for (let x = 0; x < xTicks; x++) {
        new Path.Line({
          from: [this.width / 2 + tickW * (-Math.trunc(xTicks / 2) + x), 0],
          to: [this.width / 2 + tickW * (-Math.trunc(xTicks / 2) + x), this.height],
          strokeColor: 'black',
          strokeWidth: 0.5,
          opacity: 0.2,
        })
      }
      // horiz lines
      for (let y = 0; y < yTicks; y++) {
        new Path.Line({
          from: [0, this.height / 2 + tickH * (-Math.trunc(yTicks / 2) + y)],
          to: [this.width, this.height / 2 + tickH * (-Math.trunc(yTicks / 2) + y)],
          strokeColor: 'black',
          strokeWidth: 0.5,
          opacity: 0.2,
        })
      }
    },
    drawBoundingBox () {
      this.scope.activate()
      if (this.bbox) {
        this.bbox.remove()
      }
      this.bbox = new Path.Rectangle({
        point: [this.bboxData.x, this.bboxData.y],
        size: [this.bboxData.w, this.bboxData.h],
        fillColor: 'red',
        opacity: 0.4,
        strokeColor: 'black',
      })
      console.table('bounding box delay: ' + Math.trunc(Date.now() - this.timestamp * 1000) + 'ms')
    },
  },
}

export default BoundingBoxDiagram
</script>
