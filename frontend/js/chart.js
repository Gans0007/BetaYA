// =====================================
// CHART.JS
// Отрисовка графика привычек
// =====================================

let chart


// =====================================
// confirmationsUntil
// =====================================

function confirmationsUntil(habitId, date){

const count = history.filter(r =>
r.habit_id === habitId &&
r.confirm_day &&
r.confirm_day <= date
).length

return count

}


// =====================================
// streakUntil
// =====================================

function streakUntil(habitId, date){

const days = history
.filter(r =>
r.habit_id === habitId &&
r.confirm_day &&
r.confirm_day <= date
)
.map(r => r.confirm_day)
.sort()

let streak = 0
let prev = null

for(let i = days.length-1; i >= 0; i--){

const current = new Date(days[i])

if(!prev){
streak++
prev = current
continue
}

const diff = (prev-current)/(1000*60*60*24)

if(diff === 1){
streak++
prev = current
}else{
break
}

}

return streak

}


// =====================================
// buildChart
// =====================================

function buildChart(labels, datasets, dates){

if(chart) chart.destroy()

let maxValue = 0

datasets.forEach(d=>{
d.data.forEach(v=>{
if(v > maxValue) maxValue = v
})
})

maxValue = Math.ceil(maxValue * 1.4) + 1


chart = new Chart(document.getElementById("habitsChart"),{

type:"line",

data:{
labels:labels,
datasets:datasets,
dates:dates
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
},

tooltip:{
callbacks:{

label:function(context){

const dataset = context.dataset
const habitId = dataset.habit_id

const index = context.dataIndex

// ВАЖНО: теперь используем реальные даты
const date = context.chart.data.dates[index]

const confirmations = confirmationsUntil(habitId, date)
const streak = streakUntil(habitId, date)

let lines = []

lines.push("Подтверждений: " + confirmations)

if(streak >= 1){
lines.push("🔥 Серия: " + streak + " дня")
}

return lines

}

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