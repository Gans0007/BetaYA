import { openReferral } from "./chat_components/referral.js"

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

<img 
    src="img/avatar/${user.avatar || "avatar_1.png"}" 
    class="friend-avatar"
    data-user-id="${user.user_id}"
>

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


// ==========================
// КНОПКА ДОБАВИТЬ ДРУЗЕЙ
// ==========================

document.addEventListener("click", (e)=>{

    const btn = e.target.closest(".add-friend-btn")

    if(btn){
        openReferral()
    }

})

// ==========================
// КНОПКА "ПОКАЗАТЬ" (КЛАНЫ)
// ==========================

document.addEventListener("click", (e) => {

    const btn = e.target.closest(".clan-btn")

    if(btn){
        showSoonModal()
    }

})


let soonModal = null

function showSoonModal(){

    if(soonModal){
        soonModal.style.display = "flex"
        return
    }

    soonModal = document.createElement("div")
    soonModal.className = "soon-modal"

    soonModal.innerHTML = `

    <div class="soon-overlay"></div>

    <div class="soon-content">

        <div class="soon-close">✕</div>

        <div class="soon-title">
            Скоро*
        </div>

        <div class="soon-text">
            Объединяйтесь вместе с друзьями,<br>
            соревнуйтесь за первенство с другими группами!<br>
            Отслеживайте прогресс друг друга!<br>
            Прокачивайтесь вместе!
        </div>

    </div>

    `

    document.body.appendChild(soonModal)

    // закрытие
    soonModal.querySelector(".soon-close").onclick = () => {
        soonModal.style.display = "none"
    }

    soonModal.querySelector(".soon-overlay").onclick = () => {
        soonModal.style.display = "none"
    }

}