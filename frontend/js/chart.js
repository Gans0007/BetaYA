// только график

let chart

function buildChart(labels, datasets){

if(chart) chart.destroy()

// ищем максимальное значение графика
let maxValue = 0

datasets.forEach(d=>{
d.data.forEach(v=>{
if(v > maxValue) maxValue = v
})
})

/*
добавляем запас сверху
пример:
3 → 5
5 → 7
10 → 13
*/

maxValue = Math.ceil(maxValue * 1.4) + 1

chart = new Chart(document.getElementById("habitsChart"),{

type:"line",

data:{
labels:labels,
datasets:datasets
},

options:{
responsive:true,
maintainAspectRatio:false,

plugins:{

legend:{
position:"top",
labels:{
boxWidth:12
}
},

tooltip:{
callbacks:{

label:function(context){

const dataset = context.dataset
const habitId = dataset.habit_id

const habit = habits.find(h => h.id === habitId)

const confirmations = habit?.done_days ?? 0

const streak = calculateStreak(habitId)

let lines = []

lines.push("Подтверждений: " + confirmations)

if(streak > 1){
lines.push("🔥 Серия: " + streak + " дня")
}

return lines

}

}

}

},


scales:{
y:{
beginAtZero:true,
suggestedMax:maxValue,
ticks:{
stepSize:1
}
}
}

}

})

}