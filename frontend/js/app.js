// логика Mini App

let habits = []
let history = []

async function init(){

    await loadDashboard()

    // загружаем привычки
    habits = await loadHabits()

    // загружаем подтверждения из confirmations
    history = await loadHistory()

    render(7)

}

function render(period){

    // пока используем недельный график
    const labels=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    const datasets = habits.map(h=>{

        // берём подтверждения только этой привычки
        const habitHistory = history.filter(r => r.habit_id === h.id)

        // список подтвержденных дней
        const confirmedDays = habitHistory
            .filter(r => r.confirm_day)
            .map(r => r.confirm_day)

        let value = 0
        let series = []

        for(let i=0;i<labels.length;i++){

            /*
            логика графика:

            подтверждение → +1
            пропуск → -1
            ниже 0 нельзя
            */

            if(confirmedDays.length > i){
                value += 1
            }
            else{
                value = Math.max(0,value-1)
            }

            series.push(value)

        }

        return{
            label: h.name,
            data: series,
            tension:0.35
        }

    })

    buildChart(labels,datasets)

}

init()