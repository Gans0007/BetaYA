export function renderHeader(user) {
    const root = document.getElementById("header-root")

    if (!root) {
        console.error("Header root not found")
        return
    }

    const avatar = user.avatar || "avatar_1.png"
    const headerTheme = user.header_theme || "header_default"

    root.innerHTML = `
        <div
            class="profile-card"
            data-header-theme="${headerTheme}"
        >
            <div class="resources-bar">

                <div class="resource resource-xp">
                    <div
                        class="resource-xp-fill"
                        id="xp-fill"
                        style="width: ${user.xp_percent || 0}%"
                    ></div>

                    <div class="xp-top">
                        XP
                        <span id="xp-text">
                            ${user.xp_current || 0} / ${user.xp_next || 0}
                        </span>
                    </div>
                </div>

                <div class="resource resource-stars">
                    <div
                        class="resource-stars-fill"
                        id="stars-fill"
                        style="width: ${user.stars_percent || 0}%"
                    ></div>

                    <div class="xp-top">
                        ⭐
                        <span id="stars-text">
                            ${user.stars_current || 0} / ${user.stars_next || 0}
                        </span>
                    </div>
                </div>

            </div>

            <div class="profile-row">

                <div class="profile-left">

                    <img
                        id="player-avatar"
                        class="profile-flag"
                        src="img/avatar/${avatar}"
                        alt="Аватар"
                    >

                    <div class="profile-info">
                        <div
                            class="profile-name"
                            id="player-name"
                        >
                            ${user.nickname || "Player"}
                        </div>

                        <div class="profile-clan">
                            ${user.clan?.name || "Не в клане"}
                        </div>
                    </div>

                </div>

                <div class="profile-league">

                    <div
                        id="league-text"
                        class="league-text"
                    >
                        ${user.league?.name || "—"}
                    </div>

                    <img
                        id="league-icon"
                        class="league-icon"
                        src="${user.league?.icon || ""}"
                        alt="Лига"
                    >

                </div>

            </div>
        </div>
    `

    const leagueIcon = root.querySelector("#league-icon")

    if (leagueIcon) {
        leagueIcon.addEventListener("click", () => {
            window.openLeagueInfo?.()
        })
    }
}