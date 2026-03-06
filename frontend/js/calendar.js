export function renderWeek(){

const weekContainer = document.getElementById("week-days")
const monthName = document.getElementById("month-name")

const today = new Date()

const months=[
"Январь","Февраль","Март","Апрель",
"Май","Июнь","Июль","Август",
"Сентябрь","Октябрь","Ноябрь","Декабрь"
]

const days=["Вс","Пн","Вт","Ср","Чт","Пт","Сб"]

monthName.innerText=months[today.getMonth()]
weekContainer.innerHTML=""

for(let i=6;i>=0;i--){

const d=new Date(today)
d.setDate(today.getDate()-i)

const el=document.createElement("div")
el.className="day"

if(d.toDateString()===today.toDateString()){
el.classList.add("today")
}

el.innerHTML=`
<div class="day-number">${d.getDate()}</div>
<div class="day-name">${days[d.getDay()]}</div>
`

weekContainer.appendChild(el)

}

}