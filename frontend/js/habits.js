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
МЕСЯЦ
========================= */

let monthCells=""
let completedMonth = 0

for(let day=1; day<=daysInMonth; day++){

const dateStr =
now.getFullYear()+"-"+String(now.getMonth()+1).padStart(2,"0")+"-"+String(day).padStart(2,"0")

const active = confirmedDays.has(dateStr)
? "cell active"
: "cell"

if(active==="cell active"){
completedMonth++
}

monthCells += `<div class="${active}"></div>`

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

const startOfYear = new Date(now.getFullYear(),0,1)

const totalWeeks = 53

for(let week=0; week<totalWeeks; week++){

for(let day=0; day<7; day++){

const date = new Date(
now.getFullYear(),
0,
week*7 + day + 1
)

let cellClass="cell"

if(date.getFullYear()===now.getFullYear()){

const dateStr =
date.getFullYear()+"-"+String(date.getMonth()+1).padStart(2,"0")+"-"+String(date.getDate()).padStart(2,"0")

if(confirmedDays.has(dateStr)){
cellClass="cell active"
completedYear++
}

}

yearCells+=`<div class="${cellClass}"></div>`

}

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
<div></div>
<div>Ср</div>
<div></div>
<div>Пт</div>
<div></div>
<div></div>

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

drawChart(chartId,habit.series)

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