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



/* =========================================
ДАТА
========================================= */

const now = new Date()



/* =========================================
ДНИ В МЕСЯЦЕ
========================================= */

const daysInMonth = new Date(
now.getFullYear(),
now.getMonth()+1,
0
).getDate()



/* =========================================
ДНИ В ГОДУ
========================================= */

const startOfYear = new Date(now.getFullYear(),0,1)
const endOfYear = new Date(now.getFullYear(),11,31)

const daysInYear =
Math.floor((endOfYear-startOfYear)/(1000*60*60*24))+1



/* =========================================
ГЕНЕРАЦИЯ КВАДРАТОВ МЕСЯЦА
========================================= */

let monthCellsHTML=""

for(let d=1; d<=daysInMonth; d++){

monthCellsHTML+=`<div class="cell"></div>`

}



/* =========================================
ГЕНЕРАЦИЯ КВАДРАТОВ ГОДА
========================================= */

let yearCellsHTML=""

for(let d=1; d<=daysInYear; d++){

yearCellsHTML+=`<div class="cell"></div>`

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

${monthCellsHTML}

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



/* =========================================
TOGGLE РАСКРЫТИЯ КАРТОЧКИ
========================================= */

const main = card.querySelector(".habit-main")

main.addEventListener("click",()=>{
toggleHabit(card)
})



/* =========================================
ПЕРЕКЛЮЧАТЕЛЬ МЕСЯЦ / ГОД
========================================= */

const grid = card.querySelector(".grid")

const monthBtn = card.querySelector(".switch-btn:nth-child(1)")
const yearBtn = card.querySelector(".switch-btn:nth-child(2)")



monthBtn.addEventListener("click",()=>{

monthBtn.classList.add("active")
yearBtn.classList.remove("active")

grid.classList.remove("year")

grid.innerHTML = monthCellsHTML

})



yearBtn.addEventListener("click",()=>{

yearBtn.classList.add("active")
monthBtn.classList.remove("active")

grid.classList.add("year")

grid.innerHTML = yearCellsHTML

})



list.appendChild(card)

drawChart(chartId,habit.series)

})

}