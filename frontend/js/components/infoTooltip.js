export function initInfoTooltip(config){

    if(document.querySelector(".info-tooltip")) return

    const tooltip = document.createElement("div")
    tooltip.className = "info-tooltip hidden"

    document.body.appendChild(tooltip)

    document.addEventListener("click", (e) => {

        if(!document.querySelector(".profile-overlay.active")){
            tooltip.classList.add("hidden")
            return
        }

        const btn = e.target.closest(".info-btn")

        if(btn){

            if(!tooltip.classList.contains("hidden")){
                tooltip.classList.add("hidden")
                return
            }

            const key = btn.dataset.info
            const text = config[key]

            if(!text) return

            tooltip.innerHTML = text
            tooltip.classList.remove("hidden")

            tooltip.style.maxWidth = "220px"

            const rect = btn.getBoundingClientRect()
            const tooltipWidth = tooltip.offsetWidth || 220

            const padding = 10
            let left = rect.left + rect.width / 2
            const top = rect.bottom + 8

            // ограничение слева
            if(left - tooltipWidth / 2 < padding){
                left = padding + tooltipWidth / 2
            }

            // ограничение справа
            if(left + tooltipWidth / 2 > window.innerWidth - padding){
                left = window.innerWidth - padding - tooltipWidth / 2
            }

            tooltip.style.top = top + "px"
            tooltip.style.left = left + "px"

            tooltip.style.transform = "translateX(-50%) scale(0.95)"

            setTimeout(() => {
                if(!tooltip.classList.contains("hidden")){
                    tooltip.style.transform = "translateX(-50%) scale(1)"
                }
            }, 10)

            return
        }

        tooltip.classList.add("hidden")
    })

    window.addEventListener("scroll", () => {
        tooltip.classList.add("hidden")
    })
}