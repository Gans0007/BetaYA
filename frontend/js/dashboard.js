/* =========================================
   TELEGRAM MINI APP INIT
   ========================================= */

const tg = window.Telegram.WebApp

// расширяем мини апп на весь экран
tg.expand()

// telegram initData (нужно для проверки пользователя в API)
const initData = tg.initData



/* =========================================
   ЗАГРУЗКА ДАННЫХ С API
   ========================================= */

async function loadDashboard(){

    try{

        // отправляем Telegram initData на API
        const response = await fetch("/api/dashboard",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body: JSON.stringify({
                initData:initData
            })

        })

        // получаем ответ
        const data = await response.json()

        console.log("API DATA:",data)

        // передаем привычки на отрисовку
        renderHabits(data.habits)

    }

    catch(e){

        console.log("API ERROR",e)

    }

}



/* =========================================
   ОТРИСОВКА КАРТОЧЕК ПРИВЫЧЕК
   ========================================= */

function renderHabits(habits){

    const list=document.getElementById("habits-list")

    // очищаем контейнер
    list.innerHTML=""

    // если привычек нет
    if(!habits || habits.length===0){

        list.innerHTML="<p>Нет активных привычек</p>"
        return

    }

    habits.forEach((habit,i)=>{

        const chartId="chart-"+i

        const card=document.createElement("div")

        card.className="habit-card"

        /* -------------------------------
           HTML карточки привычки
           ------------------------------- */

        card.innerHTML=`

        <div class="habit-info">

            <div class="habit-name">
                ${habit.name}
            </div>

        </div>

        <div class="habit-chart">
            <canvas id="${chartId}"></canvas>
        </div>

        `

        list.appendChild(card)

        /* -------------------------------
           строим график привычки
           ------------------------------- */

        drawChart(chartId,habit.series)

    })

}



/* =========================================
   ФУНКЦИЯ ОТРИСОВКИ МИНИ ГРАФИКА
   ========================================= */

function drawChart(id,series){

    const ctx=document.getElementById(id)

    new Chart(ctx,{

        type:"line",

        data:{

            // 5 последних дней
            labels:["","","","",""],

            datasets:[{

                // данные приходят из API
                data:series,

                borderColor:"#f4d47c",

                borderWidth:2,

                pointRadius:3,

                tension:0.4

            }]

        },

        options:{

            responsive:true,

            maintainAspectRatio:false,

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



/* =========================================
   ЗАПУСК DASHBOARD
   ========================================= */

loadDashboard()