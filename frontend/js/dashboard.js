const tg = window.Telegram.WebApp
tg.expand()

const initData = tg.initData

async function loadDashboard(){

    try{

        const response = await fetch("/api/dashboard",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body: JSON.stringify({
                initData:initData
            })
        })

        const data = await response.json()

        console.log("API DATA:",data)

        renderHabits(data.habits)

    }catch(e){

        console.log("API ERROR",e)

    }

}

function renderHabits(habits){

    const list=document.getElementById("habits-list")

    list.innerHTML=""

    if(!habits || habits.length===0){

        list.innerHTML="<p class='empty'>Нет активных привычек</p>"
        return

    }

    habits.forEach(habit=>{

        const item=document.createElement("div")

        item.className="habit-card"

        item.innerHTML=`

            <div class="habit-left">
                <div class="habit-name">${habit.name}</div>
            </div>

            <div class="habit-right">
                ✔
            </div>

        `

        list.appendChild(item)

    })

}

loadDashboard()