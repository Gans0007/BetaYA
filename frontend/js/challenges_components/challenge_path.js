export function renderChallengePath(data){

    const container = document.createElement("div")
    container.className = "challenge-path"

    // 🔥 красивая змейка (как в игре)
    const offsets = [0, 80, 20, 100, 40, 120, 60]

    for(let i = 1; i <= data.days; i++){

        const state =
            i < data.currentDay ? "done" :
            i === data.currentDay ? "active" :
            "locked"

        const node = document.createElement("div")
        node.className = `challenge-node node-${state}`

        const offset = offsets[i % offsets.length]
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