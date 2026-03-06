import {drawChart} from "./charts.js"

export function renderHabits(habits){

const list=document.getElementById("habits-list")

list.innerHTML=""

if(!habits || habits.length===0){

list.innerHTML="<p>Нет активных привычек</p>"
return

}

habits.forEach((habit,i)=>{

const chartId="chart-"+i

const card=document.createElement("div")

card.className="habit-card"

card.innerHTML=`

<div class="habit-info">

<div class="habit-name">${habit.name}</div>

<div class="habit-streak">
🔥 Стрик: ${habit.streak} дней
</div>

</div>

<div class="habit-chart">
<canvas id="${chartId}"></canvas>
</div>

`

list.appendChild(card)

drawChart(chartId,habit.series)

})

}