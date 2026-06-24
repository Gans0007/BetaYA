export function drawChart(id, series, color = "#22c55e") {
  const canvas = document.getElementById(id)
  const ctx = canvas.getContext("2d")

  const gradient = ctx.createLinearGradient(0, 0, 0, 90)
  gradient.addColorStop(0, color)
  gradient.addColorStop(1, color)

  const glowPlugin = {
    id: "glow",

    beforeDatasetsDraw(chart) {
      const { ctx } = chart

      ctx.save()
      ctx.shadowColor = color
      ctx.shadowBlur = 12
      ctx.shadowOffsetX = 0
      ctx.shadowOffsetY = 0
    },

    afterDatasetsDraw(chart) {
      chart.ctx.restore()
    }
  }

  new Chart(ctx, {
    type: "line",

    data: {
      labels: series.map(() => ""),

      datasets: [{
        data: series,

        borderColor: gradient,
        borderWidth: 3,

        pointRadius: 5,
        pointHoverRadius: 5,

        pointBackgroundColor: (ctx) => {
          return ctx.raw > 0 ? color : "#ffffff"
        },

        pointBorderColor: color,
        pointBorderWidth: 3,

        tension: 0.45
      }]
    },

    options: {
      responsive: true,
      maintainAspectRatio: false,

      plugins: {
        legend: false,
        tooltip: { enabled: false }
      },

      scales: {
        x: { display: false },
        y: { display: false }
      },

      elements: {
        line: {
          borderJoinStyle: "round",
          capBezierPoints: true
        }
      }
    },

    plugins: [glowPlugin]
  })
}