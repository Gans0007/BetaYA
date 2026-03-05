// логика Mini App

let habits = []
let history = []
let monthStats = []

let currentPeriod = 7

const weekdays = ["Вс","Пн","Вт","Ср","Чт","Пт","Сб"]

async function init(){

await loadDashboard()

habits = await loadHabits()
history = await loadHistory()
monthStats = await loadMonthStats()

setupButtons()

render(currentPeriod)

}

/*
========================
КНОПКИ
========================
*/

function setupButtons(){

const buttons = document.querySelectorAll(".period-switch button")

buttons.forEach(btn => {

btn.addEventListener("click", () => {

buttons.forEach(b => b.classList.remove("active"))

btn.classList.add("active")

currentPeriod = parseInt(btn.dataset.period)

render(currentPeriod)

})

})

}


/*
========================
ГЕНЕРАЦИЯ ДАТ + LABELS
========================
*/

function generateTimeline(period){

const today = new Date()

let dates = []
let labels = []

if(period === 7){

for(let i=6;i>=0;i--){

let d = new Date()
d.setDate(today.getDate()-i)

dates.push(d.toISOString().slice(0,10))
labels.push(weekdays[d.getDay()])

}

}

if(period === 30){

for(let i=29;i>=0;i--){

let d = new Date()
d.setDate(today.getDate()-i)

dates.push(d.toISOString().slice(0,10))
labels.push(String(d.getDate()).padStart(2,"0"))

}

}

if(period === 12){

for(let i=11;i>=0;i--){

let d = new Date()
d.setMonth(today.getMonth()-i)

dates.push(d.toISOString().slice(0,7))
labels.push(d.toLocaleString("ru",{month:"short"}))

}

}

return {dates, labels}

}


/*
========================
ГРАФИК
========================
*/

function render(period){

const timeline = generateTimeline(period)

/*
========================
ГОДОВОЙ ГРАФИК
========================
*/

if(period === 12){

const totals = timeline.dates.map(month => {

const row = monthStats.find(r => r.month === month)

return row ? parseInt(row.total) : 0

})

const datasets = [

{
label:"Подтверждения",
data:totals,
tension:0.35,
borderWidth:3
}

]

buildChart(timeline.labels, datasets, timeline.dates)

return

}

/*
========================
7 и 30 дней
========================
*/

const datasets = habits.map(h => {

const habitHistory = history.filter(r => r.habit_id === h.id)

const confirmSet = new Set(
habitHistory
.filter(r => r.confirm_day)
.map(r => r.confirm_day)
)

let value = 0
let series = []

timeline.dates.forEach(date => {

if(confirmSet.has(date)){
value++
}else{
value = Math.max(0,value-1)
}

series.push(value)

})

return{
label:h.name,
data:series,
tension:0.35,
habit_id:h.id
}

})

buildChart(timeline.labels, datasets, timeline.dates)

}

document.addEventListener("DOMContentLoaded", init)