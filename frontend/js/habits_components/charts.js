export function drawChart(id,series){

const canvas = document.getElementById(id)
const ctx = canvas.getContext("2d")

/* ===== ЗОЛОТОЙ ГРАДИЕНТ ===== */

const gradient = ctx.createLinearGradient(0,0,0,70)

gradient.addColorStop(0,"#ffd86b")
gradient.addColorStop(1,"#e8c66a")

/* ===== ПЛАГИН ВЕРТИКАЛЬНЫХ ЛИНИЙ ===== */

const verticalLinesPlugin = {

id:"verticalLines",

afterDatasetsDraw(chart,args,pluginOptions){

const {ctx, chartArea:{bottom}} = chart
const meta = chart.getDatasetMeta(0)

ctx.save()

ctx.setLineDash([3,3])
ctx.strokeStyle="rgba(232,198,106,0.35)"
ctx.lineWidth=1

meta.data.forEach(point=>{

ctx.beginPath()
ctx.moveTo(point.x,point.y)
ctx.lineTo(point.x,bottom)
ctx.stroke()

})

ctx.restore()

}

}

/* ===== ГЛОУ ===== */

const glowPlugin = {

id:"glow",

beforeDatasetsDraw(chart,args,pluginOptions){

const {ctx} = chart

ctx.save()

ctx.shadowColor = "rgba(255,215,120,0.9)"
ctx.shadowBlur = 14
ctx.shadowOffsetX = 0
ctx.shadowOffsetY = 0

}

}

/* ===== ЧАРТ ===== */

new Chart(ctx,{

type:"line",

data:{

labels:series.map(()=>""), 

datasets:[{

data:series,

borderColor:gradient,
borderWidth:3,

pointRadius:5,
pointHoverRadius:5,

pointBackgroundColor:"#ffd86b",
pointBorderWidth:0,

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

},

elements:{
line:{
borderJoinStyle:"round",
capBezierPoints:true
}
}

},

plugins:[verticalLinesPlugin,glowPlugin]

})

}