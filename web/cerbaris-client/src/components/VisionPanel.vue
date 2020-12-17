<template>
  <b-card no-body>
    <b-card-header class="panel-heading">
      Vision Panel
    </b-card-header>
    <b-card-body class="panel-body d-flex justify-content-center flex-wrap flex-lg-nowrap p-2">
      <bounding-box-diagram
        class="m-1"
        :bbox-data="bboxData"
        :timestamp="timestamp"
      />
      <b-table
        hover
        sticky-header
        small
        class="m-1 flex-fill"
        :items="dataTable"
      />
    </b-card-body>
  </b-card>
</template>

<script>
import Pusher from 'pusher-js'
import BoundingBoxDiagram from '@/components/BoundingBoxDiagram'

const VisionPanel = {
  components: { BoundingBoxDiagram },
  data () {
    return {
      bboxData: { x: 0, y: 0, w: 0, h: 0 },
      timestamp: 0,
      dataTable: [{ name: null, value: null, date: null }],
    }
  },
  created () {
    const pusher = new Pusher(process.env.VUE_APP_PUSHER_KEY, {
      cluster: process.env.VUE_APP_PUSHER_CLUSTER,
    })

    const channel = pusher.subscribe('vision_data')
    channel.bind('new', this.update)
  },
  methods: {
    update (data) {
      this.timestamp = data.timestamp
      delete data.timestamp
      this.updateBBoxChart(data)
      this.updateDataTable(data)
    },

    updateBBoxChart ({ bboxX, bboxY, bboxW, bboxH }) {
      this.bboxData = {
        x: bboxX,
        y: bboxY,
        w: bboxW,
        h: bboxH,
      }
    },

    updateDataTable (data) {
      const currDataTable = []
      const date = new Date(this.timestamp * 1000).toLocaleString()
      for (const [name, value] of Object.entries(data)) {
        currDataTable.push({ name, value, date })
      }
      this.dataTable = currDataTable
    },
  },
}

export default VisionPanel
</script>
