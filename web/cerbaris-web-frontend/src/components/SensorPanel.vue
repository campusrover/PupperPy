<template>
  <div>
    <b-table hover :items="dataTable"></b-table>
    <acc-line-chart :xAccData="xAccData" :yAccData="yAccData" :zAccData="zAccData"></acc-line-chart>
  </div>
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

  const SensorPanel = {
    components: {AccLineChart},
    data() {
      return {
        xAccData: [],
        yAccData: [],
        zAccData: [],
        dataObj: {},
        dataTable: [],
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
      update({timestamp, x_acc, y_acc, z_acc, imu_calibration, gyro_calibration, accel_calibration, left_obj, center_obj, right_obj}) {
        this.update_acc_line_chart(timestamp, x_acc, y_acc, z_acc)
        this.update_data_table(timestamp, {gyro_calibration, left_obj, center_obj, right_obj})
      },

      update_acc_line_chart(timestamp, xAcc, yAcc, zAcc) {
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

      update_data_table(timestamp, data) {
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