export function renderHeader(user) {
    const root = document.getElementById("header-root")

    if (!root) {
        console.error("Header root not found")
        return
    }

    const avatar =
        "/img/header_img/avatars_img/hunter.png"

    const background =
        "/img/header_img/background_header_img/forest.png"

    root.innerHTML = `
        <div
            class="profile-card"
            style="--header-background: url('${background}')"
        >
            <div class="header-shade"></div>

            <img
                id="player-avatar"
                class="header-avatar"
                src="${avatar}"
                alt="Аватар"
            >

            <div class="header-main">

                <div class="header-xp">

                    <div class="header-xp-text">
                        <strong>XP ${user.xp_current || 0}</strong>
                        <span>/ ${user.xp_next || 0}</span>
                    </div>

                    <div class="header-xp-track">
                        <div
                            id="xp-fill"
                            class="header-xp-fill"
                            style="width: ${user.xp_percent || 0}%"
                        ></div>
                    </div>

                </div>

                <div class="header-user-info">

                    <div
                        id="player-name"
                        class="profile-name"
                    >
                        ${user.nickname || "Player"}
                    </div>

                    <div class="profile-clan">
                        ${user.clan?.name || "Не в клане"}
                    </div>

                </div>

            </div>

            <div class="header-stars">

                <span class="header-star-icon">
                    ⭐
                </span>

                <span id="stars-text">
                    ${user.stars_current || 0} /
                    ${user.stars_next || 0}
                </span>

            </div>

            <div class="profile-league">

                <img
                    id="league-icon"
                    class="league-icon"
                    src="${user.league?.icon || ""}"
                    alt="Лига"
                >

                <div
                    id="league-text"
                    class="league-text"
                >
                    ${user.league?.name || "—"}
                </div>

            </div>

        </div>
    `

    const leagueIcon =
        root.querySelector("#league-icon")

    if (leagueIcon) {
        leagueIcon.addEventListener("click", () => {
            window.openLeagueInfo?.()
        })
    }
}