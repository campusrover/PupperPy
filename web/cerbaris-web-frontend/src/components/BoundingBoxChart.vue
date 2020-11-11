<template>
  <bubble-chart :styles="styles" :chart-data="datacollection" titletext="Bounding Box"></bubble-chart>
</template>

<script>
  import BubbleChart from '@/components/BubbleChart'

  export default {
    name: 'bboxChart',
    components: {BubbleChart},
    props: ['bboxData'],
    data() {
      return {
        styles: {
          width: '400px',
        },
        datacollection: {},
      }
    },
    created() {
      console.log(this.bboxData)
      this.datacollection = {datasets: [{
        pointStyle: 'rect',
        data: this.bboxData,
      }]}
    },
  }
</script>
