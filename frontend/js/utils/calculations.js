export function calculateBehavior(habits, range = "month"){

if(!habits || habits.length === 0){
return { completed: 0, missed: 0, index: 0 }
}

const now = new Date()

let startDate

if(range === "month"){
startDate = new Date(now.getFullYear(), now.getMonth(), 1)
}else{
startDate = new Date(now.getFullYear(), 0, 1)
}

const today = new Date(
now.getFullYear(),
now.getMonth(),
now.getDate()
)

let completed = 0
let missed = 0

for(let d = new Date(startDate); d <= today; d.setDate(d.getDate()+1)){

const dateStr =
d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0")

let doneCount = 0

habits.forEach(h => {
if(h.days && h.days.includes(dateStr)){
doneCount++
}
})

completed += doneCount
missed += (habits.length - doneCount)

}

let index = 0

if(completed + missed > 0){
index = Math.round((completed / (completed + missed)) * 100)
}

return {
completed,
missed,
index
}

}