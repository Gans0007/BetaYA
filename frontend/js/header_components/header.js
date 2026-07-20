export function renderHeader(user) {
    const root = document.getElementById("header-root")

    if (!root) {
        console.error("Header root not found")
        return
    }

    const avatarFile =
        user?.avatar || "avatar_bronze_1.png"

    const avatar =
        `/img/header_img/avatars_img/${avatarFile}`

    const background =
        "/img/header_img/background_header_img/background_silver_1.png"

    const xpCurrent = user?.xp_current ?? 0
    const xpNext = user?.xp_next ?? 0
    const xpPercent = Math.min(
        100,
        Math.max(0, Number(user?.xp_percent) || 0)
    )

    const nickname =
        user?.nickname || "Player"

    const clanName =
        user?.clan?.name || "Не в клане"

    const starsCurrent =
        user?.stars_current ?? 0

    const starsNext =
        user?.stars_next ?? 0

    const leagueIcon =
        user?.league?.icon || ""

    const leagueName =
        user?.league?.name || "—"

    root.innerHTML = `
        <div
            class="profile-card"
            style="--header-background: url('${background}')"
        >
            <div class="header-shade"></div>

            <div class="header-content">

                <div class="header-avatar-column">
                    <img
                        id="player-avatar"
                        class="header-avatar"
                        src="${avatar}"
                        alt="Аватар"
                    >
                </div>

                <div class="header-main">

                    <div class="header-xp">

                        <div class="header-xp-text">
                            <strong>
                                XP ${xpCurrent}
                            </strong>

                            <span>
                                / ${xpNext}
                            </span>
                        </div>

                        <div class="header-xp-track">
                            <div
                                id="xp-fill"
                                class="header-xp-fill"
                                style="width: ${xpPercent}%"
                            ></div>
                        </div>

                    </div>

                    <div class="header-user-info">

                        <div
                            id="player-name"
                            class="profile-name"
                        >
                            ${nickname}
                        </div>

                        <div class="profile-clan">
                            ${clanName}
                        </div>

                    </div>

                </div>

                <div class="header-right">

                    <div class="header-stars">

                        <span class="header-star-icon">
                            ⭐
                        </span>

                        <span id="stars-text">
                            ${starsCurrent} / ${starsNext}
                        </span>

                    </div>

                    <div class="profile-league">

                        <img
                            id="league-icon"
                            class="league-icon"
                            src="${leagueIcon}"
                            alt="Лига"
                        >

                        <div
                            id="league-text"
                            class="league-text"
                        >
                            ${leagueName}
                        </div>

                    </div>

                </div>

            </div>

        </div>
    `

}