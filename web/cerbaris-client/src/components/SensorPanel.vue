<template>
  <b-card no-body style="max-height: 40vh">
    <b-card-header class="panel-heading">
      Sensor Panel
    </b-card-header>
    <b-card-body class="panel-body d-flex">
      <sensor-diagram class="mr-3" :sensor-data="sensorData" :yaw="yaw" :timestamp="timestamp"></sensor-diagram>
      <map-diagram class="mr-3" :pos-data="posData" :timestamp="timestamp"></map-diagram>
      <!-- <acc-line-chart :xAccData="xAccData" :yAccData="yAccData" :zAccData="zAccData"></acc-line-chart> -->
      <b-table hover sticky-header small class="flex-fill" :items="dataTable"></b-table>
    </b-card-body>
  </b-card>
</template>

<script>
  /* 
  DATA: timestamp, x_acc, y_acc, z_acc, robo_x_vel, robo_y_vel, roll, pitch, yaw, robo_yaw_rate,
  imu_calibration, gyro_calibration, accel_calibration, left_obj, right_obj, center_obj
  */
  // timeseries: x_acc, y_acc, z_acc
  // timeseries: robo_x_vel, robo_y_vel
  // timeseries: roll, pitch, yaw
  // timeseries: robo_yaw_rate
  // table: imu_calibration, gyro_calibration, accel_calibration
  // diagram: yaw, x_acc, y_acc, robo_x_vel, robo_y_vel, robo_yaw_rate, left_obj, right_obj, center_obj

  import AccLineChart from '@/components/AccLineChart'
  import SensorDiagram from '@/components/SensorDiagram'
  import MapDiagram from '@/components/MapDiagram'

  const SensorPanel = {
    components: {AccLineChart, SensorDiagram, MapDiagram},
    data() {
      return {
        xAccData: [],
        yAccData: [],
        zAccData: [],
        timestamp: 0,
        sensorData: {},
        posData: {},
        yaw: 0,
        dataObj: {},
        dataTable: [{name: null, value: null, date: null}],
      }
    },
    created() {
      const pusher = new Pusher(process.env.VUE_APP_PUSHER_KEY, {
        cluster: process.env.VUE_APP_PUSHER_CLUSTER,
      });

      const channel = pusher.subscribe('sensor_data');
      channel.bind('new', this.update);
    },
    methods: {
      update(data) {
        let {timestamp, x_acc, y_acc, z_acc, x_pos, y_pos, left_obj, center_obj, right_obj, yaw} = data
        this.timestamp = timestamp
        delete data.timestamp
        this.yaw = yaw
        this.updateAccLineChart(timestamp, x_acc, y_acc, z_acc)
        this.updateSensorDiagram(timestamp, {left_obj, center_obj, right_obj})
        this.updateMapDiagram(timestamp, {x: x_pos, y: y_pos})
        this.updateDataTable(timestamp, data)
      },

      updateAccLineChart(timestamp, xAcc, yAcc, zAcc) {
        if (xAcc !== undefined) {
          this.xAccData.push({x: timestamp, y: xAcc})
        }
        if (yAcc !== undefined) {
          this.yAccData.push({x: timestamp, y: yAcc})
        }
        if (zAcc !== undefined) {
          this.zAccData.push({x: timestamp, y: zAcc})
        }
      },

      updateSensorDiagram(timestamp, sensorData) {
        this.sensorData = sensorData
      },

      updateMapDiagram(timestamp, posData) {
        this.posData = posData
      },

      updateDataTable(timestamp, data) {
        let date = new Date(timestamp * 1000).toLocaleString();

        for (const [name, value] of Object.entries(data)) {
          if (value !== undefined) {
            this.dataObj[name] = {value, date};
          }
        }

        let currTable = []
        for (const [name, {value, date}] of Object.entries(this.dataObj)) {
          currTable.push({
            name,
            value,
            date,
          });
        }
        this.dataTable = currTable;
      }
    },
  }

  export default SensorPanel;
</script>