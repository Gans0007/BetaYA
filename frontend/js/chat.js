export function renderChatUser(xp){

const tg = window.Telegram.WebApp
const user = tg.initDataUnsafe?.user

if(!user) return

const list = document.querySelector(".friends-list")
if(!list) return

/* чтобы не дублировалось */

if(document.querySelector(".friend-card.me")) return

const card = document.createElement("div")
card.className = "friend-card me"

card.innerHTML = `

<div class="friend-left">

<img src="${user.photo_url || 'img/default-avatar.png'}" class="friend-avatar">

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
🏆 ${Math.floor(xp ?? 0)}
</div>

</div>

`

list.prepend(card)

}