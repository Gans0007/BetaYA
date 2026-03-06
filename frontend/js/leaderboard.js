async function loadLeaderboard(){

const response = await fetch("/api/leaderboard")
const data = await response.json()

const list = document.getElementById("leaderboard-list")

list.innerHTML=""

data.leaders.forEach(user=>{

const item=document.createElement("div")

item.className="leader-row"

item.innerHTML=`

<div class="rank">${user.rank}</div>

<div class="leader-name">
${user.username}
</div>

<div class="leader-xp">
${user.xp}
</div>

<div class="leader-cup">
🏆
</div>

`

list.appendChild(item)

})

}

loadLeaderboard()