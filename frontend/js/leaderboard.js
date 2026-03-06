async function loadLeaderboard(){

    const response = await fetch("/api/leaderboard")
    const data = await response.json()

    const list = document.getElementById("leaderboard-list")

    list.innerHTML=""

    data.leaders.forEach(user=>{

        const item=document.createElement("div")

        item.className="leader-row"

        let rankClass="rank"

        if(user.rank===1) rankClass+=" gold"
        if(user.rank===2) rankClass+=" silver"
        if(user.rank===3) rankClass+=" bronze"

        item.innerHTML=`

        <div class="${rankClass}">
            ${user.rank}
        </div>

        <div class="leader-name">
            ${user.username || "Unknown"}
        </div>

        <div class="leader-xp">
            ${user.xp.toLocaleString()}
        </div>

        <div class="leader-cup">
            🏆
        </div>

        `

        list.appendChild(item)

    })

}

loadLeaderboard()