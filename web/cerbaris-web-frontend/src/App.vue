<template>
  <div id="app">
    <h1>CERBARIS Dashboard</h1>
    <b-table hover :items="data_table"></b-table>
    <sensor-panel></sensor-panel>
  </div>
</template>

<script>
  import Pusher from 'pusher-js';
  import SensorPanel from '@/components/SensorPanel'
  import VisionPanel from '@/components/VisionPanel'

  const App = {
    components: {SensorPanel, VisionPanel},
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
  margin-top: 60px;
}
</style>
