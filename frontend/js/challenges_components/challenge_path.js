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

        let imgSrc = ""

        if(state === "done"){
            imgSrc = "/img/nodes/node_done.png"
        }else if(state === "active"){
            imgSrc = "/img/nodes/node_wait.png"
        }else{
            imgSrc = "/img/nodes/node_lock.png"
        }

        const node = document.createElement("div")
        node.className = "challenge-node"

        node.innerHTML = `
            <div class="node-circle">
                <img src="${imgSrc}" class="node-img"/>
            </div>
            ${i < days ? `<div class="node-line"></div>` : ""}
        `

        container.appendChild(node)
    }

    return container
}