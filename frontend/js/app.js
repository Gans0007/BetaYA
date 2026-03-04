// логика Mini App

let habits = []
let history = []
let currentPeriod = 7

async function init(){

    await loadDashboard()

    habits = await loadHabits()
    history = await loadHistory()

    setupButtons()

    render(currentPeriod)

}


/*
========================
КНОПКИ ПЕРЕКЛЮЧЕНИЯ
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
ГЕНЕРАЦИЯ ДАТ
========================
*/

function generateDates(period){

const today = new Date()
let dates = []

if(period === 7){

for(let i=6;i>=0;i--){
let d = new Date()
d.setDate(today.getDate()-i)
dates.push(d.toISOString().slice(0,10))
}

}

if(period === 30){

for(let i=29;i>=0;i--){
let d = new Date()
d.setDate(today.getDate()-i)
dates.push(d.toISOString().slice(0,10))
}

}

if(period === 12){

for(let i=11;i>=0;i--){
let d = new Date()
d.setMonth(today.getMonth()-i)
dates.push(d.toISOString().slice(0,7))
}

}

return dates

}


/*
========================
ПОСТРОЕНИЕ ГРАФИКА
========================
*/

function render(period){

const dates = generateDates(period)

const datasets = habits.map(h => {

const habitHistory = history.filter(r => r.habit_id === h.id)

const confirmSet = new Set(
habitHistory
.filter(r => r.confirm_day)
.map(r => r.confirm_day)
)

let value = 0
let series = []

dates.forEach(date => {

if(confirmSet.has(date)){
value += 1
}
else{
value = Math.max(0,value-1)
}

series.push(value)

})

return {
label: h.name,
data: series,
tension:0.35
}

})

buildChart(dates, datasets)

}

init()