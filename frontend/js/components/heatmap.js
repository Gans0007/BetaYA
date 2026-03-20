export function renderHeatmap(container, data){

    if(!container) return

    container.innerHTML = ""

    const map = document.createElement("div")
    map.className = "heatmap-grid"

    // =========================
    // ГРУППИРУЕМ ПО НЕДЕЛЯМ
    // =========================

    const weeks = []

    let currentWeek = []

    data.forEach((day, i) => {

        const date = new Date(day.date)
        const dayOfWeek = (date.getDay() + 6) % 7 + 1 // Пн = 1

        if(i === 0){
            for(let j = 1; j < dayOfWeek; j++){
                currentWeek.push(null)
            }
        }

        currentWeek.push(day)

        if(dayOfWeek === 7){
            weeks.push(currentWeek)
            currentWeek = []
        }

    })

    if(currentWeek.length){
        while(currentWeek.length < 7){
            currentWeek.push(null)
        }
        weeks.push(currentWeek)
    }

    // =========================
    // РЕНДЕР
    // =========================

    weeks.forEach(week => {

        const col = document.createElement("div")
        col.className = "heatmap-col"

        week.forEach(day => {

            const cell = document.createElement("div")
            cell.className = "heatmap-cell"

            if(day){
                const val = day.value

                cell.dataset.value = val

                if(val === 0) cell.classList.add("lvl-0")
                else if(val < 2) cell.classList.add("lvl-1")
                else if(val < 4) cell.classList.add("lvl-2")
                else cell.classList.add("lvl-3")

                cell.title = `${day.date} — ${val}`
            }else{
                cell.classList.add("empty")
            }

            col.appendChild(cell)

        })

        map.appendChild(col)

    })

    container.appendChild(map)
}