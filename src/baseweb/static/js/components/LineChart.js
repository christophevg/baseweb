/**
 * LineChart - Chart.js wrapper component for Vue 3
 *
 * Uses Chart.js directly instead of vue-chartjs (v4 has no UMD build).
 * Provides reactive data updates and proper cleanup.
 *
 * Props:
 * - chartData: Object with labels and datasets arrays
 * - options: Chart.js options object (merged with defaults)
 *
 * Usage:
 * <line-chart :chart-data="data" :options="opts"></line-chart>
 */

app.component('LineChart', {
  template: '<canvas ref="canvas"></canvas>',
  props: {
    chartData: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: function() {
        return {};
      }
    }
  },
  data: function() {
    return {
      chart: null,
      default_options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        animation: {
          duration: 500
        },
        scales: {
          xAxes: [{
            id: 'x-axis-0',
            display: true
          }],
          yAxes: [{
            id: 'y-axis-0',
            display: true,
            ticks: {
              beginAtZero: true
            }
          }]
        }
      }
    };
  },
  computed: {
    merged_options: function() {
      // Deep merge options (Vue 3 compatible, no jQuery needed)
      return this.deepMerge(this.default_options, this.options);
    }
  },
  mounted: function() {
    this.createChart();
  },
  beforeUnmount: function() {
    // Clean up chart instance to prevent memory leaks
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  },
  watch: {
    chartData: {
      deep: true,
      handler: function(newData) {
        this.updateChartData();
      }
    },
    options: {
      deep: true,
      handler: function(newOptions) {
        this.recreateChart();
      }
    }
  },
  methods: {
    createChart: function() {
      var ctx = this.$refs.canvas.getContext('2d');
      this.chart = new Chart(ctx, {
        type: 'line',
        data: this.chartData,
        options: this.merged_options
      });
    },
    updateChartData: function() {
      // Only update data, not options (Chart.js 2.x limitation)
      if (this.chart) {
        this.chart.data = this.chartData;
        this.chart.update();
      }
    },
    recreateChart: function() {
      // Destroy and recreate for options changes (Chart.js 2.x limitation)
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
      this.createChart();
    },
    deepMerge: function(target, source) {
      // Simple deep merge utility (replaces $.extend(true, ...))
      var result = Object.assign({}, target);
      for (var key in source) {
        if (source.hasOwnProperty(key)) {
          if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
            result[key] = this.deepMerge(result[key] || {}, source[key]);
          } else {
            result[key] = source[key];
          }
        }
      }
      return result;
    }
  }
});
