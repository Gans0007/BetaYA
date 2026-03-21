let userProfileOverlay = null
let isOpening = false

export function initUserProfileModal(){

    if(userProfileOverlay) return

    userProfileOverlay = document.createElement("div")
    userProfileOverlay.className = "profile-overlay hidden"

    userProfileOverlay.innerHTML = `
    <div class="profile-modal">

        <div class="profile-modal-header">
            <div class="profile-header-left">

                <img id="external-avatar" class="profile-avatar">

                <div>
                    <div class="profile-name">...</div>
                    <div class="profile-sub">...</div>
                </div>

            </div>

            <div class="profile-close">✕</div>
        </div>

        <div class="profile-modal-content">

            <div class="profile-section">
                <div class="section-title">Информация</div>
                <div class="external-info"></div>
            </div>

        </div>

    </div>
    `

    document.body.appendChild(userProfileOverlay)

    const closeBtn = userProfileOverlay.querySelector(".profile-close")

    closeBtn.addEventListener("click", closeModal)

    userProfileOverlay.addEventListener("click", (e)=>{
        if(e.target === userProfileOverlay){
            closeModal()
        }
    })

    function closeModal(){
        userProfileOverlay.classList.remove("active")
        setTimeout(()=>{
            userProfileOverlay.classList.add("hidden")
        },200)

        document.body.style.overflow = ""
    }

}

export async function openUserProfile(userId){

    if(isOpening) return
    isOpening = true

    if(!userProfileOverlay){
        initUserProfileModal()
    }

    userProfileOverlay.classList.remove("hidden")
    const nameEl = userProfileOverlay.querySelector(".profile-name")
    const subEl = userProfileOverlay.querySelector(".profile-sub")
    const avatarEl = userProfileOverlay.querySelector("#external-avatar")

    nameEl.innerText = "Загрузка..."
    subEl.innerText = "..."
    avatarEl.src = "img/avatar/avatar_1.png"

    setTimeout(()=>{
        userProfileOverlay.classList.add("active")
    },10)

    document.body.style.overflow = "hidden"

    try{

        const res = await fetch("/api/profile/view",{
            method:"POST",
            headers:{ "Content-Type":"application/json" },
            body: JSON.stringify({ user_id: userId })
        })

        const data = await res.json()

        if(!data || !data.user) return

        renderUserProfile(data.user)
        isOpening = false

    }catch(err){
        console.error(err)
        isOpening = false
    }

}

function renderUserProfile(user){

    const nameEl = userProfileOverlay.querySelector(".profile-name")
    const subEl = userProfileOverlay.querySelector(".profile-sub")
    const avatarEl = userProfileOverlay.querySelector("#external-avatar")

    nameEl.innerText = user.nickname
    subEl.innerText = user.league.name
    avatarEl.src = `img/avatar/${user.avatar}`

}