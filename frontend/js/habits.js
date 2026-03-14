import {drawChart} from "./charts.js"
import {getDashboard} from "./api.js"
import {renderChatUser} from "./chat.js"
import {renderReferrals} from "./chat.js"

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

const confirmedDays = new Set(habit.days || [])

/* =========================
СТРИК (ПОКАЗЫВАЕМ >=2)
========================= */

let streakHTML = ""

if(habit.streak >= 1){

const word =
habit.streak === 1 ? "день" :
habit.streak <= 4 ? "дня" :
"дней"

streakHTML =
`<div class="habit-streak">🔥 Стрик: ${habit.streak} ${word}</div>`

}

/* =========================
МЕСЯЦ (GitHub style)
========================= */

let monthCells=""
let completedMonth = 0

const year = now.getFullYear()
const month = now.getMonth()

const monthStart = new Date(year, month, 1)
const monthEnd = new Date(year, month + 1, 0)

// понедельник недели начала
const start = new Date(monthStart)
start.setDate(monthStart.getDate() - ((monthStart.getDay()+6)%7))

// воскресенье недели конца
const end = new Date(monthEnd)
end.setDate(monthEnd.getDate() + (6 - ((monthEnd.getDay()+6)%7)))

for(let d = new Date(start); d <= end; d.setDate(d.getDate()+1)){

let cellClass="cell"

const dateStr =
d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0")

if(
d.getMonth()===month &&
confirmedDays.has(dateStr)
){
cellClass="cell active"
completedMonth++
}

monthCells+=`<div class="${cellClass}"></div>`

}

let percentMonth = Math.floor(
(completedMonth / daysInMonth) * 100
)

percentMonth = Math.max(0,Math.min(100,percentMonth))

/* =========================
ГОД (GitHub style)
========================= */

let yearCells = ""
let completedYear = 0

const yearStart = new Date(now.getFullYear(),0,1)
const yearEnd = new Date(now.getFullYear(),11,31)

// понедельник первой недели
const startYear = new Date(yearStart)
startYear.setDate(yearStart.getDate() - ((yearStart.getDay()+6)%7))

// воскресенье последней недели
const endYear = new Date(yearEnd)
endYear.setDate(yearEnd.getDate() + (6 - ((yearEnd.getDay()+6)%7)))

for(let d = new Date(startYear); d <= endYear; d.setDate(d.getDate()+1)){

let cellClass="cell"

if(d.getFullYear()===now.getFullYear()){

const dateStr =
d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0")

if(confirmedDays.has(dateStr)){
cellClass="cell active"
completedYear++
}

}

yearCells+=`<div class="${cellClass}"></div>`

}

const percentYear = Math.floor(
(completedYear / 365) * 100
)

/* =========================
КАРТОЧКА
========================= */

const wrap=document.createElement("div")
wrap.className="habit-wrap"

wrap.innerHTML=`

<div class="habit-card">

<div class="habit-main">

<div class="habit-info">

<div class="habit-name">${habit.name}</div>

${streakHTML}

</div>

<div class="habit-chart">
<canvas id="${chartId}"></canvas>
</div>

</div>

</div>

<div class="habit-overlay">

<div class="year-wrapper">

<div class="weekdays">

<div>Пн</div>
<div>Вт</div>
<div>Ср</div>
<div>Чт</div>
<div>Пт</div>
<div>Сб</div>
<div>Вс</div>

</div>

<div class="grid">

${monthCells}

</div>

</div>

<div class="habit-footer">

<div class="switch">

<button class="switch-btn active">Месяц</button>
<button class="switch-btn">Год</button>

</div>

<div class="progress">
${percentMonth}% выполнено
</div>

</div>

</div>

`

/* =========================
ОТКРЫТИЕ КАРТОЧКИ
========================= */

const main = wrap.querySelector(".habit-main")

main.addEventListener("click",()=>{
wrap.classList.toggle("active")
})

/* =========================
ПЕРЕКЛЮЧАТЕЛЬ
========================= */

const grid = wrap.querySelector(".grid")
const progress = wrap.querySelector(".progress")

const monthBtn = wrap.querySelector(".switch-btn:nth-child(1)")
const yearBtn = wrap.querySelector(".switch-btn:nth-child(2)")

monthBtn.onclick=()=>{

monthBtn.classList.add("active")
yearBtn.classList.remove("active")

grid.classList.remove("year")
grid.innerHTML=monthCells

progress.innerHTML = percentMonth + "% выполнено"

}

yearBtn.onclick=()=>{

yearBtn.classList.add("active")
monthBtn.classList.remove("active")

grid.classList.add("year")
grid.innerHTML=yearCells

progress.innerHTML = percentYear + "% выполнено"

}

list.appendChild(wrap)

const series = (habit.series || []).slice(-7)

while(series.length < 7){
series.unshift(0)
}

drawChart(chartId,series)

})

}


/* =========================
LOAD DASHBOARD
========================= */

export async function loadHabitsDashboard(initData){

const data = await getDashboard(initData)

console.log("API DATA:", data)

renderChatUser(data.xp_current)

if(data.referrals){
renderReferrals(data.referrals)
}

/* ======================
XP BAR
====================== */

const xpText = document.getElementById("xp-text")
const xpFill = document.getElementById("xp-fill")

if(xpText && xpFill){

xpText.innerText = data.xp_current + " / " + data.xp_next

xpFill.style.width = data.xp_percent + "%"

}

/* ======================
PLAYER NAME
====================== */

const playerName = document.getElementById("player-name")

if(playerName){
playerName.innerText = data.nickname
}

/* ======================
PLAYER AVATAR
====================== */

const avatar = document.getElementById("player-avatar")

if(avatar){
avatar.src = "img/avatar/avatar_1.png"
}

/* ======================
LEAGUE
====================== */

const leagueText = document.getElementById("league-text")

if(leagueText){
leagueText.innerText = data.league
}

/* ======================
HABITS
====================== */

renderHabits(data.habits)

}