async function loadLeaderboard(){

const tg = window.Telegram.WebApp

const response = await fetch("/api/leaderboard",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
initData:tg.initData
})
})

const data = await response.json()

const list = document.getElementById("leaderboard-list")

list.innerHTML=""

/* ===== ТОП 100 ===== */

data.leaders.forEach(user=>{

const item=document.createElement("div")

item.className="leader-row"

if(user.rank === data.me?.rank){
    item.classList.add("my-row")
}

let rankClass = ""

if(user.rank === 1) rankClass = "gold"
if(user.rank === 2) rankClass = "silver"
if(user.rank === 3) rankClass = "bronze"

item.innerHTML = `

<div class="leader-rank ${rankClass}">
    ${user.rank}
</div>

<img 
    src="img/avatar/${user.avatar || "avatar_1.png"}" 
    class="leader-avatar"
    data-user-id="${user.user_id}"
>

<div class="leader-info">
    <div class="leader-name">
        ${user.username || "Unknown"}
    </div>

    <div class="leader-league">
            ${user.league || "Бронза I"}
    </div>
</div>

<div class="leader-score">
    <span class="leader-cup">🏆</span>
    <span>${user.xp.toLocaleString()}</span>
</div>

`

list.appendChild(item)

})

/* ===== ЕСЛИ Я НЕ В ТОП 100 ===== */

if(data.me?.rank && data.me.rank > 100){

const divider=document.createElement("div")

divider.className="leader-divider"
divider.innerHTML="..."

list.appendChild(divider)

const myRow=document.createElement("div")

myRow.className="leader-row my-row"

myRow.innerHTML = `

<div class="leader-rank">
    ${data.me.rank}
</div>

<img 
    src="img/avatar/${data.me.avatar || "avatar_1.png"}" 
    class="leader-avatar"
>

<div class="leader-info">
    <div class="leader-name">
        ${data.me.username || "You"}
    </div>

    <div class="leader-league">
        ${data.me.league || "Бронза I"}
    </div>
</div>

<div class="leader-score">
    <span class="leader-cup">🏆</span>
    <span>${(data.me.xp || 0).toLocaleString()}</span>
</div>

`

list.appendChild(myRow)

}

}

loadLeaderboard()