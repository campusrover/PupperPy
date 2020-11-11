<script>
  import { Line, mixins } from 'vue-chartjs';
  const { reactiveProp } = mixins

  export default {
    extends: Line,
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
              ticks: {
                beginAtZero: true,
              },
            }],
            xAxes: [{
              type: 'linear',
              position: 'bottom',
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