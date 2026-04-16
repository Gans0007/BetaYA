export function renderChallengePath({ days, currentDay }) {

    const container = document.createElement("div")
    container.className = "challenge-path"

    // 🔥 змейка
    const offsets = [20, 60, 30, 70, 40, 60, 30]

    for(let i = 1; i <= days; i++){

        let state = "locked"

        // ✅ DONE
        if(i <= currentDay){
            state = "done"
        }

        // ⚡ ACTIVE (следующий после done)
        else if(i === currentDay + 1){
            state = "active"
        }

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