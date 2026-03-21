export function renderChatUser(xp){

const tg = window.Telegram.WebApp
const user = tg.initDataUnsafe?.user || {}

const list = document.querySelector(".friends-list")
if(!list) return

const old = document.querySelector(".friend-card.me")
if(old) old.remove()

const card = document.createElement("div")
card.className = "friend-card me"

card.innerHTML = `

<div class="friend-left">

<img src="img/avatar/${window.currentUserAvatar || "avatar_1.png"}" class="friend-avatar">

<div>

<div class="friend-name">
${user.first_name || "You"} (Вы)
</div>

<div class="friend-status">
В сети
</div>

</div>

</div>

<div class="friend-right">

<div class="friend-cups">
🏆 ${Math.floor(xp || 0)}
</div>

</div>

`

list.prepend(card)

}




/* реферал */
export function renderReferrals(referrals){

const list = document.querySelector(".friends-list")

if(!list) return

/* очистка старых */

const old = document.querySelectorAll(".friend-card.ref")
old.forEach(el=>el.remove())

referrals.forEach(user=>{

const card=document.createElement("div")

card.className="friend-card ref"

card.innerHTML=`

<div class="friend-left">

<img src="img/avatar/${user.avatar || "avatar_1.png"}" class="friend-avatar">

<div>

<div class="friend-name">
${user.name}
</div>

<div class="friend-status">
Друг
</div>

</div>

</div>

<div class="friend-right">

<div class="friend-cups">
🏆 ${user.xp}
</div>

</div>

`

list.appendChild(card)

})

}