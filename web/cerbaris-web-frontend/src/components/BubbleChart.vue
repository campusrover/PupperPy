<script>
  import { Bubble, mixins } from 'vue-chartjs';
  const { reactiveProp } = mixins

  export default {
    extends: Bubble,
    mixins: [reactiveProp],
    props: ['titletext'],
    data() {
      return {
        options: {
          title: {
            display: true,
            text: this.titletext,
          },
          scales: {
            yAxes: [{
              type: 'linear',
              ticks: {
                min: -500,
                max: 500,
              }
            }],
            xAxes: [{
              type: 'linear',
              ticks: {
                min: -500,
                max: 500,
              }
            }]
          },
        },
      }
    },
    mounted () {
      this.renderChart(this.chartData, this.options)
    },
  };
</script>