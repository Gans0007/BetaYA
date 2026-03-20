export function renderHeatmap(container, data){

    if(!container) return

    container.innerHTML = ""

    const wrapper = document.createElement("div")
    wrapper.className = "heatmap-wrapper"

    // =========================
    // ДНИ НЕДЕЛИ
    // =========================

    const days = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]

    const daysCol = document.createElement("div")
    daysCol.className = "heatmap-days"

    days.forEach(d => {
        const el = document.createElement("div")
        el.className = "heatmap-day-label"
        el.innerText = d
        daysCol.appendChild(el)
    })

    // =========================
    // ГРУППИРОВКА
    // =========================

    const grid = document.createElement("div")
    grid.className = "heatmap-grid"

    const weeks = []
    let currentWeek = []

    data.forEach((day, i) => {

        const date = new Date(day.date)
        const dayOfWeek = (date.getDay() + 6) % 7 + 1

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
    // РЕНДЕР КЛЕТОК
    // =========================

    weeks.forEach(week => {

        const col = document.createElement("div")
        col.className = "heatmap-col"

        week.forEach(day => {

            const cell = document.createElement("div")
            cell.className = "heatmap-cell"

            if(day){
                const val = day.value

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

        grid.appendChild(col)
    })

    // =========================
    // СБОРКА
    // =========================

    wrapper.appendChild(daysCol)
    wrapper.appendChild(grid)

    container.appendChild(wrapper)
}