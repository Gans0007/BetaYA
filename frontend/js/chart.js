// только график

let chart

function buildChart(labels, datasets){

if(chart) chart.destroy()

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
ticks:{
stepSize:1
}
}
}

}

})

}