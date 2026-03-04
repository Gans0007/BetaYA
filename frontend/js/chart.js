//только график

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
maintainAspectRatio:false
}

})

}