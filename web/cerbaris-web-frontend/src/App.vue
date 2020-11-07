<template>
<div id="app">
  Pinged: {{ pinged }}
</div>
</template>

<script>
  import Pusher from 'pusher-js';

  const App = {
    data() {
      return {
        pinged: false
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

      update() {
        this.pinged = true;
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
