//только работа с API
const tg = window.Telegram.WebApp
tg.expand()

async function apiPost(url){

const response = await fetch(url,{
method:"POST",
headers:{ "Content-Type":"application/json" },
body:JSON.stringify({
initData: tg.initData
})
})

return response.json()

}

async function loadDashboard(){

const data = await apiPost("/api/dashboard")

document.getElementById("streak").innerText = data.streak ?? 0
document.getElementById("xp").innerText = Math.floor(data.xp ?? 0)
document.getElementById("league").innerText = data.league ?? "-"

}

async function loadHabits(){

const data = await apiPost("/api/habits")

return data.habits || []

}

async function loadHistory(){

const data = await apiPost("/api/habit_history")

return data.history || []

}