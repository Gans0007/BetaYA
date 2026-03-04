// только график

let chart

function buildChart(labels, datasets){

if(chart) chart.destroy()

// ищем максимальное значение графика
let maxValue = 0

datasets.forEach(d=>{
d.data.forEach(v=>{
if(v > maxValue) maxValue = v
})
})

// добавляем запас
maxValue = maxValue + 2

chart = new Chart(document.getElementById("habitsChart"),{

type:"line",

data:{
labels:labels,
datasets:datasets
},

options:{
responsive:true,
maintainAspectRatio:false,

plugins:{
legend:{
position:"top",
labels:{
boxWidth:12
}
}
},

scales:{
y:{
beginAtZero:true,
suggestedMax:maxValue,
ticks:{
stepSize:1
}
}
}

}

})

}