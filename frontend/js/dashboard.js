const tg = window.Telegram.WebApp
const initData = tg.initData

async function loadHabits(){

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

        const list = document.getElementById("habits-list")

        list.innerHTML=""

        if(!data.habits){
            list.innerHTML="<p>Нет привычек</p>"
            return
        }

        data.habits.forEach(habit =>{

            const item=document.createElement("div")

            item.className="habit-card"

            item.innerHTML=`<div class="habit-name">${habit.name}</div>`

            list.appendChild(item)

        })

    }catch(e){

        console.log("Ошибка API",e)

    }

}

loadHabits()