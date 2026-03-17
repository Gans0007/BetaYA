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

    <!-- =========================
    HEADER
    ========================== -->
    <div class="profile-modal-header">
        <div class="profile-header-left">
            <img src="img/avatar/avatar_1.png" class="profile-avatar">
            <div>
                <div class="profile-name">Player</div>
                <div class="profile-sub">Бронза I</div>
            </div>
        </div>

        <div class="profile-close">✕</div>
    </div>

    <!-- =========================
    CONTENT
    ========================== -->
    <div class="profile-modal-content">

        <!-- =========================
        BEHAVIOR BLOCK
        ========================== -->
        <div class="behavior-block">

            <!-- donut -->
            <div class="behavior-left">
                <div class="donut-placeholder">
                    45 / 20
                </div>
                <div class="behavior-label">
                    Выполнено / Пропущено
                </div>
            </div>

            <!-- index -->
            <div class="behavior-right">
                <div class="gauge-placeholder">
                    69%
                </div>
                <div class="behavior-label">
                    Настойчивость
                </div>
            </div>

        </div>

        <!-- =========================
        HEATMAP BLOCK (заглушка)
        ========================== -->
        <div class="profile-section">
            <div class="section-title">Активность</div>
            <div class="heatmap-placeholder">
                Heatmap
            </div>
        </div>

        <!-- =========================
        GRAPH BLOCK (заглушка)
        ========================== -->
        <div class="profile-section">
            <div class="section-title">Прогресс</div>
            <div class="graph-placeholder">
                Graph
            </div>
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