Vue.component('LineChart', {
  extends:  VueChartJs.Line,
  mixins: [ VueChartJs.mixins.reactiveProp ],
  props:  [ "options" ],
  mounted: function() {
    this.renderChart(this.chartData, this.merged_options);
  },
  computed: {
    merged_options: function() {
      return $.extend(true, this.default_options, this.options);
    }
  },
  data : function() {
    return {
      default_options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          display: false
        },
        animation: {
          duration: 500
        },
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: true
            }
          }]
        }        
      }
    }
  }
});
