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

let rankClass="rank"

if(user.rank===1) rankClass+=" gold"
if(user.rank===2) rankClass+=" silver"
if(user.rank===3) rankClass+=" bronze"

item.innerHTML=`

<div class="${rankClass}">
${user.rank}
</div>

<div class="leader-left">

<img 
    src="img/avatar/${user.avatar || "avatar_1.png"}" 
    class="leader-avatar"
    data-user-id="${user.user_id}"
>

<div class="leader-name">
${user.username || "Unknown"}
</div>

</div>

<div class="leader-xp">
${user.xp.toLocaleString()}
</div>

<div class="leader-cup">
🏆
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

myRow.innerHTML=`

<div class="rank">
${data.me.rank}
</div>

<div class="leader-left">

<img src="img/avatar/${data.me.avatar || "avatar_1.png"}" class="leader-avatar">

<div class="leader-name">
${data.me.username || "You"}
</div>

</div>

<div class="leader-xp">
${(data.me.xp || 0).toLocaleString()}
</div>

<div class="leader-cup">
🏆
</div>

`

list.appendChild(myRow)

}

}

loadLeaderboard()