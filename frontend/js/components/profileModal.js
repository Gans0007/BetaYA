export function initProfileModal(){

const avatar = document.getElementById("player-avatar")

if(!avatar) return

// ==========================
// СОЗДАЕМ MODAL HTML
// ==========================

const overlay = document.createElement("div")
overlay.className = "profile-overlay hidden"

overlay.innerHTML = `
<div class="profile-modal">

    <div class="profile-modal-header">
        <div>Профиль</div>
        <div class="profile-close">✕</div>
    </div>

    <div class="profile-modal-content">
        <div style="opacity:0.6; text-align:center; margin-top:40px;">
            Здесь будет профиль
        </div>
    </div>

</div>
`

document.body.appendChild(overlay)

const modal = overlay.querySelector(".profile-modal")
const closeBtn = overlay.querySelector(".profile-close")

// ==========================
// ОТКРЫТИЕ
// ==========================

avatar.addEventListener("click", ()=>{

overlay.classList.remove("hidden")

setTimeout(()=>{
overlay.classList.add("active")
},10)

document.body.style.overflow = "hidden"

})

// ==========================
// ЗАКРЫТИЕ
// ==========================

function closeModal(){

overlay.classList.remove("active")

setTimeout(()=>{
overlay.classList.add("hidden")
},250)

document.body.style.overflow = ""

}

// крестик
closeBtn.addEventListener("click", closeModal)

// клик вне модалки
overlay.addEventListener("click",(e)=>{
if(e.target === overlay){
closeModal()
}
})

// ESC
document.addEventListener("keydown",(e)=>{
if(e.key === "Escape"){
closeModal()
}
})

}