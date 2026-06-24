export function drawChart(id, series, color = "#22c55e") {
  const canvas = document.getElementById(id)
  const ctx = canvas.getContext("2d")

  new Chart(ctx, {
    type: "line",

    data: {
      labels: series.map(() => ""),

      datasets: [{
        data: series,

        borderColor: color,
        borderWidth: 2,

        pointRadius: 4,
        pointHoverRadius: 4,

        pointBackgroundColor: (ctx) => {
          return ctx.raw > 0 ? color : "#ffffff"
        },

        pointBorderColor: color,
        pointBorderWidth: 2,

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
      }
    }
  })
}