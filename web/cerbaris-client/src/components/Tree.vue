<template>
  <div>
    <p>Shift-click + drag to create. Alt-click to delete. Double-click to edit text.</p>
    <tree-diagram :curr-node-id="currNodeId" />
  </div>
</template>

<script>
import Pusher from 'pusher-js'
import TreeDiagram from '@/components/TreeDiagram'

// todo: get string from GET request to API
// switch between normal dashboard and this using keyboard shortcut
// make fully interactive

const Tree = {
  components: { TreeDiagram },
  data () {
    return {
      currNodeId: null,
    }
  },
  created () {
    const pusher = new Pusher(process.env.VUE_APP_PUSHER_KEY, {
      cluster: process.env.VUE_APP_PUSHER_CLUSTER,
    })

    const channel = pusher.subscribe('tree_data')
    channel.bind('new', this.update)
  },
  methods: {
    update (data) {
      this.currNodeId = data.node_id
    },
  },
}

export default Tree
</script>
