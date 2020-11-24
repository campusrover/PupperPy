<template>
  <div id="app">
    <b-table hover :items="data_table"></b-table>
    <sensor-panel></sensor-panel>
    <div class="d-flex">
      <vision-panel class="flex-fill"></vision-panel>
      <state-panel class="flex-fill"></state-panel>
    </div>
  </div>
</template>

<script>
  import Pusher from 'pusher-js';
  import SensorPanel from '@/components/SensorPanel'
  import VisionPanel from '@/components/VisionPanel'
  import StatePanel from '@/components/StatePanel'

  const App = {
    components: {SensorPanel, VisionPanel, StatePanel},
    data() {
      return {
        data_obj: {},
        data_table: [],
      }
    },
    created() {
      this.subscribe();
    },
    methods: {
      subscribe() {
        const pusher = new Pusher(process.env.VUE_APP_PUSHER_KEY, {
          cluster: process.env.VUE_APP_PUSHER_CLUSTER,
        });

        const channel = pusher.subscribe('data');
        channel.bind('new', this.update);
      },

      update(message) {
        // message = {metadata: {timestamp, ...}, data: {state, x_acc, ...}}
        let timestamp = new Date(message.metadata.timestamp * 1000).toLocaleString();

        for (const [name, value] of Object.entries(message.data)) {
          this.data_obj[name] = {value: value, timestamp: timestamp};
        }

        this.update_data_table();
      },

      update_data_table() {
        let curr_table = []
        for (const [name, info] of Object.entries(this.data_obj)) {
          curr_table.push({
            name: name,
            value: info.value,
            timestamp: info.timestamp,
          });
        }
        this.data_table = curr_table;
      },
    },
  }

  export default App;
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

canvas {
  border: .5px solid gray;
}

.card {
  margin: 10px;
}
</style>
