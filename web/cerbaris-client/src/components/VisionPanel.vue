<template>
  <b-card no-body>
    <b-card-header class="panel-heading">
      Vision Panel
    </b-card-header>
    <b-card-body class="panel-body d-flex">
      <bounding-box-diagram class="mr-3" :bboxData="bboxData" :timestamp="timestamp"></bounding-box-diagram>
      <b-table hover sticky-header small class="flex-fill" :items="dataTable"></b-table>
    </b-card-body>
  </b-card>
</template>

<script>
  /*
  DATA: bbox_x, bbox_y, bbox_width, bbox_height
  */
  // table: bbox_x, bbox_y, bbox_width, bbox_height, depth?
  // bubble chart: bbox_x, bbox_y, bbox_width, bbox_height
  import BoundingBoxDiagram from '@/components/BoundingBoxDiagram'

  const VisionPanel = {
    components: {BoundingBoxDiagram},
    data() {
      return {
        bboxData: {x: 0, y: 0, w: 0, h: 0},
        timestamp: 0,
        dataTable: [{name: null, value: null, date: null}],
      }
    },
    created() {
      const pusher = new Pusher(process.env.VUE_APP_PUSHER_KEY, {
        cluster: process.env.VUE_APP_PUSHER_CLUSTER,
      });

      const channel = pusher.subscribe('vision_data')
      channel.bind('new', this.update)
    },
    methods: {
      update(data) {
        this.timestamp = data.timestamp
        delete data.timestamp
        this.update_bbox_chart(data)
        this.update_data_table(data)
      },

      update_bbox_chart({bbox_x, bbox_y, bbox_w, bbox_h}) {
        this.bboxData = {
          x: bbox_x,
          y: bbox_y,
          w: bbox_w,
          h: bbox_h,
        }
      },

      update_data_table(data) {
        let currDataTable = []
        let date = new Date(this.timestamp * 1000).toLocaleString()
        for (const [name, value] of Object.entries(data)) {
          currDataTable.push({name, value, date})
        }
        this.dataTable = currDataTable
      }
    },
  }

  export default VisionPanel;
</script>