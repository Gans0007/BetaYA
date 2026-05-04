export function renderChallengePath({ days, currentDay }) {

    const container = document.createElement("div")
    container.className = "challenge-path"

    for(let i = 1; i <= days; i++){

        let state = "locked"

        if(i <= currentDay){
            state = "done"
        } else if(i === currentDay + 1){
            state = "active"
        }

        const node = document.createElement("div")
        node.className = `challenge-node node-${state}`

        node.innerHTML = `
            <div class="node-circle"></div>
            ${i < days ? `<div class="node-line"></div>` : ""}
        `

        container.appendChild(node)
    }

    return container
}