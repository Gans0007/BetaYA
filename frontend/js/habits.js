import {drawChart} from "./charts.js"



/* =========================================
ПЕРЕКЛЮЧЕНИЕ БЛОКА ПРИВЫЧКИ
========================================= */

function toggleHabit(card){

const details = card.querySelector(".habit-details")

details.classList.toggle("active")

}



/* =========================================
ОТРИСОВКА СПИСКА ПРИВЫЧЕК
========================================= */

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

<div class="habit-main">

<div class="habit-info">

<div class="habit-name">${habit.name}</div>

<div class="habit-streak">
🔥 Стрик: ${habit.streak} дней
</div>

</div>

<div class="habit-chart">
<canvas id="${chartId}"></canvas>
</div>

</div>



<div class="habit-details">

<div class="grid">

<div class="cell active"></div>
<div class="cell"></div>
<div class="cell"></div>
<div class="cell"></div>
<div class="cell"></div>
<div class="cell"></div>
<div class="cell"></div>
<div class="cell"></div>
<div class="cell"></div>
<div class="cell"></div>
<div class="cell"></div>
<div class="cell"></div>

</div>


<div class="habit-footer">

<div class="switch">

<button class="switch-btn active">Месяц</button>
<button class="switch-btn">Год</button>

</div>

<div class="progress">
3% выполнено
</div>

</div>

</div>

`



const main = card.querySelector(".habit-main")

main.addEventListener("click",()=>{
toggleHabit(card)
})

list.appendChild(card)

drawChart(chartId,habit.series)

})   // закрывает habits.forEach

}    // закрывает renderHabits