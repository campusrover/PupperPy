<template>
  <b-card no-body>
    <b-card-header class="panel-heading">
      State Panel
    </b-card-header>
    <b-card-body class="panel-body d-flex">
      {{ state }}
    </b-card-body>
  </b-card>
</template>

<script>
  /* 
  DATA: state
  */
  // state diagram: state

  const StatePanel = {
    components: {},
    props: [],
    data() {
      return {
        state: '',
      }
    },
    created() {
      const pusher = new Pusher(process.env.VUE_APP_PUSHER_KEY, {
        cluster: process.env.VUE_APP_PUSHER_CLUSTER,
      });

      const channel = pusher.subscribe('state_data');
      channel.bind('new', this.update);
    },
    methods: {
      update(message) {
        this.state = message.state
      }
    }
  }

  export default StatePanel;
</script>