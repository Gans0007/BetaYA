export function drawChart(id, series, color = "#22c55e") {
  const canvas = document.getElementById(id)
  if (!canvas) return

  const ctx = canvas.getContext("2d")

  const values = series.map(item => item.value)
  const statuses = series.map(item => item.done)

  new Chart(ctx, {
    type: "line",

    data: {
      labels: values.map(() => ""),

      datasets: [{
        data: values,

        borderColor: color,
        borderWidth: 1.6,

        pointRadius: 3.5,
        pointHoverRadius: 3.5,

        pointBackgroundColor: (ctx) => {
          return statuses[ctx.dataIndex] ? color : "#ffffff"
        },

        pointBorderColor: color,
        pointBorderWidth: 1.8,

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
        y: {
          display: false,
          min: 0,
          max: 8
        }
      }
    }
  })
}