let currentLeaderboardType = "global";
let leaderboardLoading = false;


// ==========================================
// ПЕРЕКЛЮЧАТЕЛЬ РЕЙТИНГА
// ==========================================

function createLeaderboardSwitcher() {
    const list = document.getElementById("leaderboard-list");

    if (!list) {
        return;
    }

    let controls = document.getElementById("leaderboard-controls");

    if (controls) {
        return;
    }

    controls = document.createElement("div");
    controls.id = "leaderboard-controls";
    controls.className = "leaderboard-controls";

    controls.innerHTML = `
        <div class="leaderboard-switcher">
            <button
                type="button"
                class="leaderboard-switch active"
                data-rating-type="global"
            >
                <span class="leaderboard-switch-icon">🌍</span>
                <span>Глобальный</span>
            </button>

            <button
                type="button"
                class="leaderboard-switch"
                data-rating-type="season"
            >
                <span class="leaderboard-switch-icon">🏆</span>
                <span>Сезон</span>
            </button>
        </div>

        <div
            id="leaderboard-season-info"
            class="leaderboard-season-info"
        ></div>
    `;

    list.parentNode.insertBefore(controls, list);

    controls
        .querySelectorAll(".leaderboard-switch")
        .forEach(button => {
            button.addEventListener("click", async () => {
                const ratingType = button.dataset.ratingType;

                if (
                    leaderboardLoading ||
                    ratingType === currentLeaderboardType
                ) {
                    return;
                }

                currentLeaderboardType = ratingType;

                controls
                    .querySelectorAll(".leaderboard-switch")
                    .forEach(item => {
                        item.classList.toggle(
                            "active",
                            item.dataset.ratingType === ratingType
                        );
                    });

                await loadLeaderboard();
            });
        });
}


// ==========================================
// ИНФОРМАЦИЯ О СЕЗОНЕ
// ==========================================

function renderSeasonInfo(data) {
    const seasonInfo = document.getElementById(
        "leaderboard-season-info"
    );

    if (!seasonInfo) {
        return;
    }

    if (
        currentLeaderboardType !== "season" ||
        !data.season
    ) {
        seasonInfo.innerHTML = "";
        seasonInfo.classList.remove("visible");
        return;
    }

    const season = data.season;

    seasonInfo.innerHTML = `
        <span>
            ${season.name || "Текущий сезон"}
        </span>

        <span class="season-info-divider">•</span>

        <span>
            осталось ${Number(season.days_left || 0)} дн.
        </span>
    `;

    seasonInfo.classList.add("visible");
}


// ==========================================
// ЗАГРУЗКА ЛИДЕРБОРДА
// ==========================================

async function loadLeaderboard() {
    if (leaderboardLoading) {
        return;
    }

    const tg = window.Telegram?.WebApp;
    const list = document.getElementById("leaderboard-list");

    if (!list || !tg) {
        return;
    }

    leaderboardLoading = true;
    list.classList.add("leaderboard-loading");

    try {
        const response = await fetch("/api/leaderboard", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                initData: tg.initData,
                ratingType: currentLeaderboardType
            })
        });

        if (!response.ok) {
            throw new Error(
                `Leaderboard API error: ${response.status}`
            );
        }

        const data = await response.json();

        renderSeasonInfo(data);
        renderLeaderboard(data);

    } catch (error) {
        console.error("[LEADERBOARD ERROR]", error);

        list.innerHTML = `
            <div class="leaderboard-empty">
                Не удалось загрузить рейтинг
            </div>
        `;

    } finally {
        leaderboardLoading = false;
        list.classList.remove("leaderboard-loading");
    }
}


// ==========================================
// ОТРИСОВКА ЛИДЕРБОРДА
// ==========================================

function renderLeaderboard(data) {
    const list = document.getElementById("leaderboard-list");

    if (!list) {
        return;
    }

    list.innerHTML = "";

    const leaders = Array.isArray(data.leaders)
        ? data.leaders
        : [];

    if (leaders.length === 0) {
        list.innerHTML = `
            <div class="leaderboard-empty">
                Пока в рейтинге нет участников
            </div>
        `;

        return;
    }

    const topThree = leaders.slice(0, 3);
    const otherLeaders = leaders.slice(3);

    renderTopThree(list, topThree, data.me);
    renderOtherLeaders(list, otherLeaders, data.me);
}


// ==========================================
// ТОП-3
// ==========================================

function renderTopThree(list, topThree, me) {
    const topBlock = document.createElement("div");
    topBlock.className = "leaderboard-top";

    const getUserByRank = rank => {
        return topThree.find(
            user => Number(user.rank) === rank
        );
    };

    [2, 1, 3].forEach(rank => {
        const user = getUserByRank(rank);

        if (!user) {
            return;
        }

        const card = document.createElement("div");
        card.className = `top-card top-${rank}`;

        if (
            me?.rank &&
            Number(user.rank) === Number(me.rank)
        ) {
            card.classList.add("my-top-card");
        }

        card.innerHTML = `
            <div class="top-rank">
                ${user.rank}
            </div>

            ${
                rank === 1
                    ? `<div class="top-crown">🏆</div>`
                    : ""
            }

            <img
                src="img/avatar/${user.avatar || "avatar_1.png"}"
                class="top-avatar"
                data-user-id="${user.user_id}"
                alt="${escapeHtml(user.username || "Unknown")}"
            >

            <div class="top-name">
                ${escapeHtml(user.username || "Unknown")}
            </div>

            <div class="top-league">
                ${escapeHtml(user.league || "Бронза I")}
            </div>

            <div class="top-score">
                <span>🏆</span>

                <b>
                    ${formatXp(user.xp)}
                </b>
            </div>
        `;

        topBlock.appendChild(card);
    });

    list.appendChild(topBlock);
}


// ==========================================
// ОСТАЛЬНЫЕ УЧАСТНИКИ
// ==========================================

function renderOtherLeaders(list, leaders, me) {
    const rowsBlock = document.createElement("div");
    rowsBlock.className = "leaderboard-rows";

    leaders.forEach(user => {
        const item = createLeaderboardRow(
            user,
            Number(user.rank) === Number(me?.rank)
        );

        rowsBlock.appendChild(item);
    });

    if (me?.rank && Number(me.rank) > 100) {
        const divider = document.createElement("div");
        divider.className = "leader-divider";
        divider.textContent = "...";

        rowsBlock.appendChild(divider);

        const myRow = createLeaderboardRow(
            {
                rank: me.rank,
                avatar: me.avatar,
                username: me.username,
                league: me.league,
                xp: me.xp
            },
            true
        );

        rowsBlock.appendChild(myRow);
    }

    list.appendChild(rowsBlock);
}


// ==========================================
// СТРОКА УЧАСТНИКА
// ==========================================

function createLeaderboardRow(user, isMe = false) {
    const item = document.createElement("div");
    item.className = "leader-row";

    if (isMe) {
        item.classList.add("my-row");
    }

    item.innerHTML = `
        <div class="leader-rank">
            ${user.rank || "—"}
        </div>

        <img
            src="img/avatar/${user.avatar || "avatar_1.png"}"
            class="leader-avatar"
            ${
                user.user_id
                    ? `data-user-id="${user.user_id}"`
                    : ""
            }
            alt="${escapeHtml(user.username || "Unknown")}"
        >

        <div class="leader-info">
            <div class="leader-name">
                ${escapeHtml(user.username || "Unknown")}
            </div>

            <div class="leader-league">
                ${escapeHtml(user.league || "Бронза I")}
            </div>
        </div>

        <div class="leader-score">
            <span class="leader-cup">🏆</span>

            <span>
                ${formatXp(user.xp)}
            </span>
        </div>
    `;

    return item;
}


// ==========================================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// ==========================================

function formatXp(value) {
    return Number(value || 0).toLocaleString("ru-RU", {
        maximumFractionDigits: 2
    });
}


function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// ==========================================
// ЗАПУСК
// ==========================================

createLeaderboardSwitcher();
loadLeaderboard();