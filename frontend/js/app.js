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

function generateLabels(period){

if(period === 7){
return ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
}

if(period === 30){
return Array.from({length:30},(_,i)=>i+1)
}

if(period === 12){
return ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
}

}


/*
========================
ПОСТРОЕНИЕ ГРАФИКА
========================
*/

function render(period){

const labels = generateLabels(period)

const datasets = habits.map(h => {

const habitHistory = history.filter(r => r.habit_id === h.id)

const confirmedDays = habitHistory
.filter(r => r.confirm_day)
.map(r => r.confirm_day)

let value = 0
let series = []

for(let i=0;i<labels.length;i++){

if(confirmedDays.length > i){
value += 1
}
else{
value = Math.max(0,value-1)
}

series.push(value)

}

return {
label: h.name,
data: series,
tension:0.35
}

})

buildChart(labels, datasets)

}

init()