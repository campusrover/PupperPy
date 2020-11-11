<template>
  <line-chart :styles="styles" :chart-data="datacollection" titletext="Acceleration vs. Time"></line-chart>
</template>

<script>
  import LineChart from '@/components/LineChart'

  export default {
    name: 'accLineChart',
    components: {LineChart},
    props: ['xAccData', 'yAccData', 'zAccData'],
    data() {
      return {
        styles: {
          width: '400px',
        },
      }
    },
    computed: {
      datacollection() {
        return {
          datasets: [
            {
              label: 'x_acc',
              lineTension: 0,
              borderColor: "rgba(233, 62, 62, .8)",
              fill: false,
              data: this.xAccData,
            }, {
              label: 'y_acc',
              lineTension: 0,
              borderColor: "rgba(58, 151, 231, .8)",
              fill: false,
              data: this.yAccData,
            }, {
              label: 'z_acc',
              lineTension: 0,
              borderColor: "rgba(15, 203, 40, .8)",
              fill: false,
              data: this.zAccData,
            }
          ]
        }
      }
    },
  }
</script>
