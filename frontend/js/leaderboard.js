async function loadLeaderboard() {
    const tg = window.Telegram.WebApp;

    const response = await fetch("/api/leaderboard", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            initData: tg.initData
        })
    });

    const data = await response.json();

    const list = document.getElementById("leaderboard-list");
    list.innerHTML = "";

    const leaders = data.leaders || [];
    const topThree = leaders.slice(0, 3);
    const otherLeaders = leaders.slice(3);

    const topBlock = document.createElement("div");
    topBlock.className = "leaderboard-top";

    const getUserByRank = (rank) => topThree.find(user => user.rank === rank);

    [2, 1, 3].forEach(rank => {
        const user = getUserByRank(rank);
        if (!user) return;

        const card = document.createElement("div");
        card.className = `top-card top-${rank}`;

        if (user.rank === data.me?.rank) {
            card.classList.add("my-top-card");
        }

        card.innerHTML = `
            <div class="top-rank">${user.rank}</div>

            ${rank === 1 ? `<div class="top-crown">🏆</div>` : ""}

            <img 
                src="img/avatar/${user.avatar || "avatar_1.png"}" 
                class="top-avatar"
                data-user-id="${user.user_id}"
            >

            <div class="top-name">${user.username || "Unknown"}</div>
            <div class="top-league">${user.league || "Бронза I"}</div>

            <div class="top-score">
                <span>🏆</span>
                <b>${Number(user.xp || 0).toLocaleString()}</b>
            </div>
        `;

        topBlock.appendChild(card);
    });

    list.appendChild(topBlock);

    const rowsBlock = document.createElement("div");
    rowsBlock.className = "leaderboard-rows";

    otherLeaders.forEach(user => {
        const item = document.createElement("div");
        item.className = "leader-row";

        if (user.rank === data.me?.rank) {
            item.classList.add("my-row");
        }

        item.innerHTML = `
            <div class="leader-rank">${user.rank}</div>

            <img 
                src="img/avatar/${user.avatar || "avatar_1.png"}" 
                class="leader-avatar"
                data-user-id="${user.user_id}"
            >

            <div class="leader-info">
                <div class="leader-name">${user.username || "Unknown"}</div>
                <div class="leader-league">${user.league || "Бронза I"}</div>
            </div>

            <div class="leader-score">
                <span class="leader-cup">🏆</span>
                <span>${Number(user.xp || 0).toLocaleString()}</span>
            </div>
        `;

        rowsBlock.appendChild(item);
    });

    if (data.me?.rank && data.me.rank > 100) {
        const divider = document.createElement("div");
        divider.className = "leader-divider";
        divider.innerHTML = "...";
        rowsBlock.appendChild(divider);

        const myRow = document.createElement("div");
        myRow.className = "leader-row my-row";

        myRow.innerHTML = `
            <div class="leader-rank">${data.me.rank}</div>

            <img 
                src="img/avatar/${data.me.avatar || "avatar_1.png"}" 
                class="leader-avatar"
            >

            <div class="leader-info">
                <div class="leader-name">${data.me.username || "You"}</div>
                <div class="leader-league">${data.me.league || "Бронза I"}</div>
            </div>

            <div class="leader-score">
                <span class="leader-cup">🏆</span>
                <span>${Number(data.me.xp || 0).toLocaleString()}</span>
            </div>
        `;

        rowsBlock.appendChild(myRow);
    }

    list.appendChild(rowsBlock);
}

loadLeaderboard();