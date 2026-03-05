const tg = window.Telegram.WebApp
tg.expand()

const initData = tg.initData

async function loadDashboard(){

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

    renderHabits(data.habits)

}

function randomSeries(){

    let v=0
    const arr=[]

    for(let i=0;i<5;i++){

        if(Math.random()>0.4){
            v++
        }else{
            v=Math.max(0,v-1)
        }

        arr.push(v)

    }

    return arr

}

function renderHabits(habits){

    const list=document.getElementById("habits-list")

    list.innerHTML=""

    habits.forEach((habit,i)=>{

        const id="chart-"+i

        const card=document.createElement("div")

        card.className="habit-card"

        card.innerHTML=`

        <div class="habit-info">

            <div class="habit-name">
                ${habit.name}
            </div>

            <div class="habit-streak">
                🔥 Стрик: ${Math.floor(Math.random()*12)+1} дней
            </div>

        </div>

        <div class="habit-chart">
            <canvas id="${id}"></canvas>
        </div>

        `

        list.appendChild(card)

        drawChart(id)

    })

}

function drawChart(id){

    const ctx=document.getElementById(id)

    const data=randomSeries()

    new Chart(ctx,{
        type:"line",
        data:{
            labels:["","","","",""],
            datasets:[
                {
                    data:data,
                    borderColor:"#f4d47c",
                    borderWidth:2,
                    pointRadius:3,
                    tension:0.4
                }
            ]
        },
        options:{
            plugins:{
                legend:false
            },
            scales:{
                x:{display:false},
                y:{display:false}
            }
        }
    })

}

loadDashboard()