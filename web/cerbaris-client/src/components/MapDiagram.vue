<template>
  <canvas
    id="mapCanvas"
    :width="width+'px'"
    :height="height+'px'"
  />
</template>

<script>
import paper, { Path, PointText } from 'paper'

const BoundingBoxDiagram = {
  components: {},
  props: ['posData', 'timestamp'],
  data () {
    return {
      scope: null,
      pathData: [{ x: 0, y: 0 }],
      pos: null,
      path: null,
      scale: 5,
      mapBounds: { xMin: 0, xMax: 0, yMin: 0, yMax: 0 },
      width: 250,
      height: 250,
    }
  },
  mounted () {
    this.minScale = this.scale
    this.origin = { x: this.width / 2, y: this.height / 2 }
    this.margin = 10
    this.scope = new paper.PaperScope()
    this.scope.setup('mapCanvas')
    this.reset()
    this.drawPath()
  },
  watch: {
    mapBounds () {
      this.scale = Math.min(this.minScale,
        (this.origin.y - this.margin) / (this.mapBounds.yMax || 1),
        (this.margin - this.origin.y) / (this.mapBounds.yMin || -1),
        (this.origin.x - this.margin) / (this.mapBounds.xMax || 1),
        (this.margin - this.origin.x) / (this.mapBounds.xMin || -1))
    },
    scale () {
      this.reset()
      this.drawPath()
      this.drawPos()
    },
    posData () {
      if (this.posData.x == null || this.posData.y == null) return
      this.calcMapBounds()
      this.pathData.push(this.posData)
      this.addToPath(this.posData)
      this.drawPos()
    },
  },
  methods: {
    // clear canvas, draw axes and guidelines
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
      const tickW = 10 * this.scale
      const tickH = 10 * this.scale
      const xTicks = Math.trunc(this.width / tickW) + 1
      const yTicks = Math.trunc(this.height / tickH) + 1
      // vertical lines
      for (let x = 0; x < xTicks; x++) {
        const xCoord = this.width / 2 + tickW * (-Math.trunc(xTicks / 2) + x)
        new Path.Line({
          from: [xCoord, 0],
          to: [xCoord, this.height],
          strokeColor: 'black',
          strokeWidth: 0.5,
          opacity: 0.2,
        })
        new PointText({
          point: [xCoord + 2, this.height / 2 - 2],
          content: 10 * Math.round(x - xTicks / 2),
          fillColor: 'black',
          fontFamily: 'Helvetica',
          fontSize: 10,
        })
      }
      // horiz lines
      for (let y = 0; y < yTicks; y++) {
        const yCoord = this.height / 2 + tickH * (-Math.trunc(yTicks / 2) + y)
        new Path.Line({
          from: [0, yCoord],
          to: [this.width, yCoord],
          strokeColor: 'black',
          strokeWidth: 0.5,
          opacity: 0.2,
        })
        new PointText({
          point: [this.width / 2 + 2, yCoord - 2],
          content: 10 * Math.round(y - yTicks / 2),
          fillColro: 'black',
          fontFamily: 'Helvetica',
          fontSize: 10,
        })
      }
    },
    drawPath () {
      this.scope.activate()
      this.path = new Path.Line({
        from: [this.origin.x, this.origin.y],
        to: [this.origin.x, this.origin.y],
        strokeColor: 'red',
        strokeWidth: 0.5,
      })
      this.pathData.forEach(this.addToPath)
      console.table('map delay: ' + Math.trunc(Date.now() - this.timestamp * 1000) + 'ms')
    },
    addToPath ({ x, y }) {
      this.scope.activate()
      this.path.add({ point: [x * this.scale + this.origin.x, this.origin.y - y * this.scale] })
    },
    drawPos () {
      this.scope.activate()
      if (this.pos) {
        this.pos.remove()
      }
      const { x, y } = this.posData
      this.pos = new Path.Circle({
        center: [x * this.scale + this.origin.x, this.origin.y - y * this.scale],
        radius: 2,
        strokeColor: 'blue',
        strokeWidth: 0.5,
      })
    },
    calcMapBounds () {
      // recalculate mapBounds
      if (this.posData.x < this.mapBounds.xMin ||
          this.posData.x > this.mapBounds.xMax ||
          this.posData.y < this.mapBounds.yMin ||
          this.posData.y > this.mapBounds.yMax) {
        this.mapBounds = {
          xMin: Math.min(this.posData.x, this.mapBounds.xMin),
          xMax: Math.max(this.posData.x, this.mapBounds.xMax),
          yMin: Math.min(this.posData.y, this.mapBounds.yMin),
          yMax: Math.max(this.posData.y, this.mapBounds.yMax),
        }
      }
    },
  },
}

export default BoundingBoxDiagram
</script>
