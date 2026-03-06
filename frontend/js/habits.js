import {drawChart} from "./charts.js"



/* =========================================
ОТКРЫТИЕ ВЫЕЗЖАЮЩЕГО ОКНА ПРИВЫЧКИ
========================================= */

function openHabitSheet(){

const sheet=document.getElementById("habit-sheet")

sheet.classList.add("active")

}



/* =========================================
ОТРИСОВКА СПИСКА ПРИВЫЧЕК
========================================= */

export function renderHabits(habits){

const list=document.getElementById("habits-list")

/* очищаем контейнер */

list.innerHTML=""



/* если привычек нет */

if(!habits || habits.length===0){

list.innerHTML="<p>Нет активных привычек</p>"
return

}



/* создаём карточки привычек */

habits.forEach((habit,i)=>{

const chartId="chart-"+i

const card=document.createElement("div")

card.className="habit-card"



/* при клике открываем подробное окно */

card.onclick=openHabitSheet



/* =========================================
HTML карточки привычки
========================================= */

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



/* добавляем карточку в список */

list.appendChild(card)



/* =========================================
РИСУЕМ МИНИ ГРАФИК
========================================= */

drawChart(chartId,habit.series)

})

}