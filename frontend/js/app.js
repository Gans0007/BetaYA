// логика Mini App

let habits = []
let history = []
let currentPeriod = 7

const weekdays = ["Вс","Пн","Вт","Ср","Чт","Пт","Сб"]

async function init(){

await loadDashboard()

habits = await loadHabits()
history = await loadHistory()

setupButtons()

render(currentPeriod)

}

function calculateStreak(habitId){

const habitHistory = history
  .filter(r => r.habit_id === habitId && r.confirm_day)
  .map(r => r.confirm_day)
  .sort()

let streak = 0
let prevDate = null

for(let i = habitHistory.length - 1; i >= 0; i--){

const current = new Date(habitHistory[i])

if(!prevDate){
streak++
prevDate = current
continue
}

const diff = (prevDate - current) / (1000*60*60*24)

if(diff === 1){
streak++
prevDate = current
}else{
break
}

}

return streak

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

if(period === 12){

// дата вида 2026-03
const monthChecks = habitHistory.filter(r => 
    r.confirm_day && r.confirm_day.startsWith(date)
)

if(monthChecks.length > 0){
value++
}else{
value = Math.max(0, value-1)
}

}else{

// обычная логика для дней
if(confirmSet.has(date)){
value++
}else{
value = Math.max(0,value-1)
}

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

buildChart(timeline.labels, datasets)

}

init()