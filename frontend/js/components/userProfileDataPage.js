export function getUserProfileDataPage() {
    return `
    <div class="stats-grid">
        ${statCard("img/data/1.png", "Зарегистрирован", "—", "user-profile-joined-at", "registration")}
        ${statCard("img/data/2.png", "Premium", "—", "user-profile-premium", "active")}
        ${statCard("img/data/3.png", "Привычки", "0", "user-profile-finished-habits", "active")}
        ${statCard("img/data/4.png", "Челленджи", "0", "user-profile-finished-challenges", "active")}
        ${statCard("img/data/5.png", "Опыт", "0", "user-profile-xp", "active")}
        ${statCard("img/data/6.png", "Подтвержденные дни", "0", "user-profile-confirmed-days", "active")}
        ${statCard("img/data/7.png", "Текущий стрик", "0 дней", "user-profile-current-streak", "active")}
        ${statCard("img/data/8.png", "Максимальный стрик", "0 дней", "user-profile-max-streak", "active")}
    </div>

    <div class="league-card">
        <div class="league-icon">
            <img src="img/data/9.png" alt="Лига" class="league-icon-img">
        </div>

        <div class="league-info">
            <div class="league-title">Лига</div>
            <div class="league-name" id="user-profile-league">—</div>
        </div>
    </div>

    <div class="section-header">
        <div class="section-title">Достижения</div>
        <div class="section-link">Все достижения ›</div>
    </div>

    <div class="achievements-scroll" id="user-achievements-scroll">
        ${achievementSkeleton()}
    </div>

    <div class="achievement-progress">
        <div class="progress-text">
            <span>Получено достижений</span>
            <span id="user-achievements-progress-text">0 / 0</span>
        </div>

        <div class="progress-bar">
            <div
                class="progress-fill"
                id="user-achievements-progress-fill"
                style="width: 0%"
            ></div>
        </div>
    </div>

    <div class="profile-footer">
        @LiteVAmbitionBot
    </div>
    `;
}

function statCard(iconPath, title, value, id, valueClass = "") {
    return `
    <div class="stat-card">
        <div class="stat-icon">
            <img
                src="${iconPath}"
                alt="${title}"
                class="stat-icon-img"
            >
        </div>

        <div class="stat-info">
            <div class="stat-title">${title}</div>
            <div class="stat-value ${valueClass}" id="${id}">
                ${value}
            </div>
        </div>
    </div>
    `;
}

export function renderUserProfileDataPage(data) {
    if (!data) {
        console.warn("Данные чужого профиля не переданы");
        return;
    }

    setText(
        "user-profile-joined-at",
        data.joined_at || "—"
    );

    setText(
        "user-profile-premium",
        data.has_access ? "Активен" : "Нет"
    );

    setText(
        "user-profile-finished-habits",
        data.finished_habits ?? 0
    );

    setText(
        "user-profile-finished-challenges",
        data.finished_challenges ?? 0
    );

    setText(
        "user-profile-xp",
        data.xp ?? 0
    );

    setText(
        "user-profile-confirmed-days",
        data.total_confirmed_days ?? 0
    );

    const currentStreak = Number(data.current_streak) || 0;
    const maxStreak = Number(data.max_streak) || 0;

    setText(
        "user-profile-current-streak",
        `${currentStreak} ${getDaysWord(currentStreak)}`
    );

    setText(
        "user-profile-max-streak",
        `${maxStreak} ${getDaysWord(maxStreak)}`
    );

    const leagueName =
        typeof data.league === "object"
            ? data.league?.name
            : data.league;

    setText(
        "user-profile-league",
        leagueName || "Бронза I"
    );

    renderAchievements(
        Array.isArray(data.achievements)
            ? data.achievements
            : []
    );

    renderAchievementsProgress(
        data.achievements_received ?? 0,
        data.achievements_total ?? 0
    );
}

function renderAchievements(achievements) {
    const container = document.getElementById(
        "user-achievements-scroll"
    );

    if (!container) return;

    if (
        !Array.isArray(achievements) ||
        achievements.length === 0
    ) {
        container.innerHTML = `
        <div class="achievement-card locked">
            <div class="achievement-icon">
                🏆
            </div>

            <div class="achievement-name">
                Достижений пока нет
            </div>

            <div class="achievement-status locked">
                Закрыто
            </div>
        </div>
        `;

        return;
    }

    container.innerHTML = achievements
        .map((item) => {
            const unlocked = Boolean(item.unlocked);

            const title = escapeHtml(
                item.title || "Достижение"
            );

            const iconContent = item.image
                ? `
                <img
                    src="${escapeHtml(item.image)}"
                    alt="${title}"
                    class="achievement-img"
                >
                `
                : `
                <span>
                    ${escapeHtml(item.icon || "🏆")}
                </span>
                `;

            return `
            <div class="achievement-card ${unlocked ? "" : "locked"}">
                <div class="achievement-icon">
                    ${iconContent}
                </div>

                <div class="achievement-name">
                    ${title}
                </div>

                <div class="achievement-status ${unlocked ? "" : "locked"}">
                    ${unlocked ? "Получено" : "Закрыто"}
                </div>
            </div>
            `;
        })
        .join("");
}

function renderAchievementsProgress(received, total) {
    const progressText = document.getElementById(
        "user-achievements-progress-text"
    );

    const progressFill = document.getElementById(
        "user-achievements-progress-fill"
    );

    const safeReceived = Number(received) || 0;
    const safeTotal = Number(total) || 0;

    const percent =
        safeTotal > 0
            ? Math.round(
                (safeReceived / safeTotal) * 100
            )
            : 0;

    const safePercent = Math.max(
        0,
        Math.min(100, percent)
    );

    if (progressText) {
        progressText.textContent =
            `${safeReceived} / ${safeTotal}`;
    }

    if (progressFill) {
        progressFill.style.width =
            `${safePercent}%`;
    }
}

function achievementSkeleton() {
    return `
    <div class="achievement-card locked">
        <div class="achievement-icon">
            🏆
        </div>

        <div class="achievement-name">
            Загрузка...
        </div>

        <div class="achievement-status locked">
            ...
        </div>
    </div>
    `;
}

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}

function getDaysWord(number) {
    const safeNumber =
        Math.abs(Number(number) || 0) % 100;

    const lastDigit = safeNumber % 10;

    if (
        safeNumber > 10 &&
        safeNumber < 20
    ) {
        return "дней";
    }

    if (lastDigit === 1) {
        return "день";
    }

    if (
        lastDigit >= 2 &&
        lastDigit <= 4
    ) {
        return "дня";
    }

    return "дней";
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}