<template>
  <bounding-box-chart :bbox-data="bboxData"></bounding-box-chart>
</template>

<script>
  /*
  DATA: bbox_x, bbox_y, bbox_width, bbox_height
  */
  // table: bbox_x, bbox_y, bbox_width, bbox_height, depth?
  // bubble chart: bbox_x, bbox_y, bbox_width, bbox_height
  import BoundingBoxChart from '@/components/BoundingBoxChart'

  const SensorPanel = {
    components: {BoundingBoxChart},
    data() {
      return {
        bboxData: [{x: 0, y: 0, r: 30}],
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
      update({timestamp, bbox_x, bbox_y, bbox_width, bbox_height}) {
        this.update_bbox_chart(timestamp, bbox_x, bbox_y, bbox_width, bbox_height)
      },

      update_bbox_chart(timestamp, bboxX, bboxY, bboxWidth, bboxHeight) {
        bboxData.push({x: bboxX, y: bboxY, width: bboxWidth, height: bboxHeight})
      },
    },
  }

  export default SensorPanel;
</script>