let modal = null

export function openReferral(){

    const link = window.refLink || ""

    if(!link){
        alert("Ссылка ещё не загрузилась")
        return
    }

    // если уже создана — просто показываем
    if(modal){
        modal.style.display = "flex"
        generateQR(link)
        return
    }

    // =========================
    // СОЗДАЕМ МОДАЛКУ
    // =========================

    modal = document.createElement("div")
    modal.className = "referral-modal"

modal.innerHTML = `

<div class="referral-overlay"></div>

<div class="referral-content">

    <div class="referral-close">✕</div>

    <div class="referral-title">
        Пригласи друга
    </div>

    <div class="referral-qr-wrapper">
        <div id="referral-qr"></div>
    </div>

    <div class="referral-text">
        Любой, кто отсканирует этот код,<br>
        будет мгновенно добавлен в друзья.
    </div>

    <button class="referral-copy">
        Скопировать ссылку
    </button>

</div>
`

    document.body.appendChild(modal)


    // =========================
    // ЗАКРЫТИЕ ПО ХРЕСТИКУ
    // =========================

    modal.querySelector(".referral-close").onclick = () => {
        modal.style.display = "none"
    }

    // =========================
    // ЗАКРЫТИЕ ПО ФОНУ
    // =========================

    modal.querySelector(".referral-overlay").onclick = () => {
        modal.style.display = "none"
    }

    // =========================
    // КОПИРОВАНИЕ
    // =========================

    modal.querySelector(".referral-copy").onclick = async () => {

        try{
            await navigator.clipboard.writeText(link)
            showToast("Скопировано")
        }catch{
            fallbackCopy(link)
        }

    }

    // =========================
    // ГЕНЕРАЦИЯ QR
    // =========================

    generateQR(link)

}

function generateQR(link){

    const qr = document.getElementById("referral-qr")
    if(!qr) return

    qr.innerHTML = ""

    new QRCode(qr, {
        text: link,
        width: 220,
        height: 220
    })

}

// =========================
// TOAST
// =========================

function showToast(text){

    let toast = document.createElement("div")
    toast.className = "referral-toast"
    toast.innerText = text

    document.body.appendChild(toast)

    setTimeout(()=>{
        toast.classList.add("show")
    },10)

    setTimeout(()=>{
        toast.remove()
    },2000)

}

// =========================
// FALLBACK COPY
// =========================

function fallbackCopy(text){

    const textarea = document.createElement("textarea")
    textarea.value = text
    document.body.appendChild(textarea)

    textarea.select()
    document.execCommand("copy")

    textarea.remove()

    showToast("Скопировано")

}