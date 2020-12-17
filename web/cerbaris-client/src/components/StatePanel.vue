<template>
  <b-card no-body>
    <b-card-header class="panel-heading">
      State Panel
    </b-card-header>
    <b-card-body class="panel-body d-flex p-2">
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

const StatePanel = {
  components: {},
  props: [],
  data () {
    return {
      dataObj: {},
      dataTable: [{ name: null, value: null, date: null }],
    }
  },
  created () {
    const pusher = new Pusher(process.env.VUE_APP_PUSHER_KEY, {
      cluster: process.env.VUE_APP_PUSHER_CLUSTER,
    })

    const channel = pusher.subscribe('state_data')
    channel.bind('new', this.update)
  },
  methods: {
    update (message) {
      const timestamp = message.timestamp
      delete message.timestamp
      this.updateDataTable(timestamp, message)
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

export default StatePanel
</script>
