export function drawChart(id,series){

const ctx=document.getElementById(id)

new Chart(ctx,{

type:"line",

data:{
labels:["","","","",""],
datasets:[{
data:series,
borderColor:"#e8c66a",
borderWidth:3,
pointRadius:4,
pointBackgroundColor:"#e8c66a",
tension:0.45
}]
},

options:{
responsive:true,
maintainAspectRatio:false,
plugins:{
legend:false,
tooltip:{enabled:false}
},
scales:{
x:{display:false},
y:{display:false}
}
}

})

}