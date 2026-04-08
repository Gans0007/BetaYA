export function renderChallengePath(data){

    const container = document.createElement("div")
    container.className = "challenge-path"

    for(let i = 1; i <= data.days; i++){

        const state =
            i < data.currentDay ? "done" :
            i === data.currentDay ? "active" :
            "locked"

        const node = document.createElement("div")
        node.className = `challenge-node node-${state}`

        const offset = (i % 2 === 0) ? 40 : 0
        node.style.marginLeft = offset + "px"

        node.innerHTML = `
            <div class="node-circle">
                <img src="img/challenges/node.png" class="node-img" />
            </div>
        `

        container.appendChild(node)
    }

    return container
}


function getIcon(i){
    if(i === 1) return "⭐"
    if(i === 3) return "📖"
    if(i === 5) return "🎧"
    if(i === 7) return "🏁"
    return ""
}