<template>
  <div class="trial-scores-plot">
    <h3 class="trial-scores-title">Movement scores</h3>
    <div class="trial-scores-chart-wrapper">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrialScoresPlot',
  props: {
    scores: {
      type: Array,
      default: () => []
    },
    labels: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      chart: null
    };
  },
  computed: {
    chartLabels() {
      if (this.labels && this.labels.length >= this.normalizedScores.length) {
        return this.labels.slice(0, this.normalizedScores.length);
      }
      return this.normalizedScores.map((_, i) => `Score ${i + 1}`);
    },
    normalizedScores() {
      if (!Array.isArray(this.scores) || this.scores.length === 0) return [];
      const padded = this.scores.slice(0, 5);
      while (padded.length < 5) padded.push(0);
      return padded.map(v => Math.min(100, Math.max(0, Number(v) || 0)));
    }
  },
  watch: {
    scores: {
      handler() {
        this.updateChart();
      },
      deep: true
    },
    labels: {
      handler() {
        this.updateChart();
      },
      deep: true
    }
  },
  mounted() {
    this.initChart();
  },
  beforeDestroy() {
    this.destroyChart();
  },
  methods: {
    async initChart() {
      if (!this.$refs.chartCanvas || this.chart) return;
      const Chart = (await import('chart.js/auto')).default;
      const ctx = this.$refs.chartCanvas.getContext('2d');
      this.chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: this.chartLabels,
          datasets: [{
            label: 'Score (%)',
            data: this.normalizedScores,
            backgroundColor: 'rgba(76, 175, 80, 0.7)',
            borderColor: 'rgba(76, 175, 80, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: { duration: 0 },
          plugins: {
            legend: { display: false },
            title: { display: false }
          },
          scales: {
            x: {
              display: true,
              grid: { display: false },
              ticks: {
                color: '#ffffff',
                font: { size: 20 },
                maxRotation: 45
              }
            },
            y: {
              display: true,
              min: 0,
              max: 100,
              title: {
                display: true,
                text: 'Score (%)',
                color: '#ffffff',
                font: { size: 22 }
              },
              grid: { color: 'rgba(255, 255, 255, 0.1)' },
              ticks: {
                color: '#ffffff',
                font: { size: 20 },
                stepSize: 25
              }
            }
          }
        }
      });
    },
    updateChart() {
      if (!this.chart) return;
      this.chart.data.labels = this.chartLabels;
      this.chart.data.datasets[0].data = this.normalizedScores;
      this.chart.update('none');
    },
    destroyChart() {
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
    }
  }
};
</script>

<style scoped>
.trial-scores-plot {
  background: rgba(24, 24, 24, 0.98);
  border-radius: 16px;
  padding: 32px 48px;
  color: #ffffff;
  min-width: 640px;
  max-width: 90vw;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
}
.trial-scores-title {
  margin: 0 0 24px 0;
  font-size: 28px;
  font-weight: 600;
  text-align: center;
}
.trial-scores-chart-wrapper {
  height: 420px;
  width: 100%;
  position: relative;
}
</style>
