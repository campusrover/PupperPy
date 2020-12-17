<template>
  <b-card no-body>
    <b-card-header class="panel-heading">
      Sensor Panel
    </b-card-header>
    <b-card-body class="panel-body d-flex justify-content-center flex-wrap flex-lg-nowrap p-2">
      <sensor-diagram
        class="m-1"
        :sensor-data="sensorData"
        :yaw="yaw"
        :timestamp="timestamp"
      />
      <map-diagram
        class="m-1"
        :pos-data="posData"
        :timestamp="timestamp"
      />
      <b-table
        hover
        sticky-header
        small
        class="m-1 flex-fill"
        style="max-height: 250px"
        :items="dataTable"
      />
    </b-card-body>
  </b-card>
</template>

<script>
import Pusher from 'pusher-js'
import SensorDiagram from '@/components/SensorDiagram'
import MapDiagram from '@/components/MapDiagram'

const SensorPanel = {
  components: { SensorDiagram, MapDiagram },
  data () {
    return {
      xAccData: [],
      yAccData: [],
      timestamp: 0,
      sensorData: {},
      posData: {},
      yaw: 0,
      dataObj: {},
      dataTable: [{ name: null, value: null, date: null }],
    }
  },
  created () {
    const pusher = new Pusher(process.env.VUE_APP_PUSHER_KEY, {
      cluster: process.env.VUE_APP_PUSHER_CLUSTER,
    })

    const channel = pusher.subscribe('sensor_data')
    channel.bind('new', this.update)
  },
  methods: {
    update (data) {
      const { timestamp, xPos, yPos, leftObj, centerObj, rightObj, yaw } = data
      this.timestamp = timestamp
      delete data.timestamp
      this.yaw = yaw
      this.updateSensorDiagram(timestamp, { leftObj, centerObj, rightObj })
      this.updateMapDiagram(timestamp, { x: xPos, y: yPos })
      this.updateDataTable(timestamp, data)
    },

    updateSensorDiagram (timestamp, sensorData) {
      this.sensorData = sensorData
    },

    updateMapDiagram (timestamp, posData) {
      this.posData = posData
    },

    updateDataTable (timestamp, data) {
      const date = new Date(timestamp * 1000).toLocaleString()

      for (const [name, value] of Object.entries(data)) {
        if (value !== undefined) {
          this.dataObj[name] = { value, date }
        }
      }

      const currTable = []
      for (const [name, { value, date }] of Object.entries(this.dataObj)) {
        currTable.push({
          name,
          value,
          date,
        })
      }
      this.dataTable = currTable
    },
  },
}

export default SensorPanel
</script>
