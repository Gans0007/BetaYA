// =====================================
// CHART.JS
// Отрисовка графика привычек
// =====================================

let chart


// =====================================
// ФУНКЦИЯ: confirmationsUntil
// Считает количество подтверждений
// привычки ДО выбранной даты
// =====================================

function confirmationsUntil(habitId, date){

console.log("📊 confirmationsUntil()", habitId, date)

const count = history.filter(r =>
r.habit_id === habitId &&
r.confirm_day &&
r.confirm_day <= date
).length

return count

}


// =====================================
// ФУНКЦИЯ: streakUntil
// Считает серию привычки
// на выбранную дату
// =====================================

function streakUntil(habitId, date){

console.log("🔥 streakUntil()", habitId, date)

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
// ФУНКЦИЯ: buildChart
// Создает график Chart.js
// =====================================

function buildChart(labels, datasets){

if(chart) chart.destroy()


// =====================================
// Находим максимальное значение графика
// чтобы корректно построить ось Y
// =====================================

let maxValue = 0

datasets.forEach(d=>{
d.data.forEach(v=>{
if(v > maxValue) maxValue = v
})
})

maxValue = Math.ceil(maxValue * 1.4) + 1


// =====================================
// Создаем график
// =====================================

chart = new Chart(document.getElementById("habitsChart"),{

type:"line",

data:{
labels:labels,
datasets:datasets
},

options:{

responsive:true,
maintainAspectRatio:false,


// =====================================
// ПЛАГИНЫ
// =====================================

plugins:{


// ----------------------------
// Легенда привычек
// ----------------------------

legend:{
position:"top",
labels:{
boxWidth:12
}
},


// ----------------------------
// TOOLTIP
// Показывает статистику
// на выбранную точку графика
// ----------------------------

tooltip:{
callbacks:{


label:function(context){

const dataset = context.dataset
const habitId = dataset.habit_id

// индекс точки графика
const index = context.dataIndex

// дата выбранной точки
const date = context.chart.data.labels[index]


// считаем подтверждения на тот момент
const confirmations = confirmationsUntil(habitId, date)

// считаем серию на тот момент
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


// =====================================
// ОСЬ Y
// =====================================

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