import {drawChart} from "./charts.js"

export function renderHabits(habits){

const list=document.getElementById("habits-list")
list.innerHTML=""

if(!habits || habits.length===0){
list.innerHTML="<p>Нет привычек</p>"
return
}

/* ===== ДАТА ===== */

const now = new Date()

const daysInMonth = new Date(
now.getFullYear(),
now.getMonth()+1,
0
).getDate()

const startOfYear = new Date(now.getFullYear(),0,1)
const endOfYear = new Date(now.getFullYear(),11,31)

const daysInYear =
Math.floor((endOfYear-startOfYear)/(1000*60*60*24))+1


habits.forEach((habit,i)=>{

const chartId="chart-"+i

/* ===== КВАДРАТЫ МЕСЯЦА ===== */

let monthCells=""

const confirmedDays = new Set(habit.days || [])

for(let day=1; day<=daysInMonth; day++){

const date = new Date(
now.getFullYear(),
now.getMonth(),
day
)

const dateStr = date.toISOString().slice(0,10)

const active = confirmedDays.has(dateStr)
? "cell active"
: "cell"

monthCells += `<div class="${active}"></div>`

}

/* ===== ГОД ===== */

let yearCells=""

const confirmedDaysYear = new Set(habit.days || [])

for(let i=0;i<daysInYear;i++){

const date = new Date(
now.getFullYear(),
0,
i + 1
)

const dateStr =
date.getFullYear() + "-" +
String(date.getMonth()+1).padStart(2,"0") + "-" +
String(date.getDate()).padStart(2,"0")

const active = confirmedDaysYear.has(dateStr)
? "cell active"
: "cell"

yearCells += `<div class="${active}"></div>`

}

/* ===== КАРТОЧКА ===== */

const wrap=document.createElement("div")
wrap.className="habit-wrap"

wrap.innerHTML=`

<div class="habit-card">

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

</div>

<div class="habit-overlay">

<div class="grid">

${monthCells}

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

/* toggle overlay */

const main = wrap.querySelector(".habit-main")

main.addEventListener("click",()=>{
wrap.classList.toggle("active")
})

/* переключатель */

const grid = wrap.querySelector(".grid")

const monthBtn = wrap.querySelector(".switch-btn:nth-child(1)")
const yearBtn = wrap.querySelector(".switch-btn:nth-child(2)")

monthBtn.onclick=()=>{

monthBtn.classList.add("active")
yearBtn.classList.remove("active")

grid.classList.remove("year")
grid.innerHTML=monthCells

}

yearBtn.onclick=()=>{

yearBtn.classList.add("active")
monthBtn.classList.remove("active")

grid.classList.add("year")
grid.innerHTML=yearCells

}

list.appendChild(wrap)

drawChart(chartId,habit.series)

})

}