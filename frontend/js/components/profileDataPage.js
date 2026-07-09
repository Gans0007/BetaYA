export function getProfileDataPage() {
    setTimeout(loadProfileDataPageData, 0);

    return `
    <div class="stats-grid">

        ${statCard("img/data/1.png", "Зарегистрирован", "—", "profile-joined-at", "registration")}
        ${statCard("img/data/2.png", "Premium", "—", "profile-premium", "active")}
        ${statCard("img/data/3.png", "Привычки", "0", "profile-finished-habits", "active")}
        ${statCard("img/data/4.png", "Челленджи", "0", "profile-finished-challenges", "active")}
        ${statCard("img/data/5.png", "Опыт", "0", "profile-xp", "active")}
        ${statCard("img/data/6.png", "Подтвержденные дни", "0", "profile-confirmed-days", "active")}
        ${statCard("img/data/7.png", "Текущий стрик", "0 дней", "profile-current-streak", "active")}
        ${statCard("img/data/8.png", "Максимальный стрик", "0 дней", "profile-max-streak", "active")}

    </div>

    <div class="league-card">
        <div class="league-icon">
            <img src="img/data/9.png" alt="Лига" class="league-icon-img">
        </div>
        <div class="league-info">
            <div class="league-title">Лига</div>
            <div class="league-name" id="profile-league">—</div>
        </div>
    </div>

    <div class="section-header">
        <div class="section-title">Достижения</div>
        <div class="section-link">Все достижения ›</div>
    </div>

    <div class="achievements-scroll" id="achievements-scroll">
        ${achievementSkeleton()}
    </div>

    <div class="achievement-progress">
        <div class="progress-text">
            <span>Получено достижений</span>
            <span id="achievements-progress-text">0 / 0</span>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" id="achievements-progress-fill" style="width:0%"></div>
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
            <img src="${iconPath}" alt="${title}" class="stat-icon-img">
        </div>
        <div class="stat-info">
            <div class="stat-title">${title}</div>
            <div class="stat-value ${valueClass}" id="${id}">${value}</div>
        </div>
    </div>
    `;
}

async function loadProfileDataPageData() {
    try {
        const initData = window.Telegram?.WebApp?.initData;

        if (!initData) {
            console.warn("Telegram initData не найден");
            return;
        }

        const response = await fetch("/api/profile/data", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                initData: initData
            })
        });

        const result = await response.json();

        if (!result || result.status !== "ok" || !result.data) {
            console.warn("Ошибка загрузки данных профиля:", result);
            return;
        }

        const data = result.data;

        setText("profile-joined-at", data.joined_at || "—");
        setText("profile-premium", data.has_access ? "Активен" : "Нет");

        setText("profile-finished-habits", data.finished_habits ?? 0);
        setText("profile-finished-challenges", data.finished_challenges ?? 0);
        setText("profile-xp", data.xp ?? 0);
        setText("profile-confirmed-days", data.total_confirmed_days ?? 0);

        setText(
            "profile-current-streak",
            `${data.current_streak ?? 0} ${getDaysWord(data.current_streak ?? 0)}`
        );

        setText(
            "profile-max-streak",
            `${data.max_streak ?? 0} ${getDaysWord(data.max_streak ?? 0)}`
        );

        setText("profile-league", data.league || "Бронза I");

        renderAchievements(data.achievements || []);

        renderAchievementsProgress(
            data.achievements_received ?? 0,
            data.achievements_total ?? 0
        );

    } catch (error) {
        console.error("Ошибка profileDataPage:", error);
    }
}

function renderAchievements(achievements) {
    const container = document.getElementById("achievements-scroll");
    if (!container) return;

    if (!achievements.length) {
        container.innerHTML = `
        <div class="achievement-card locked">
            <div class="achievement-icon">🏆</div>
            <div class="achievement-name">Достижений пока нет</div>
            <div class="achievement-status locked">Закрыто</div>
        </div>
        `;
        return;
    }

    container.innerHTML = achievements.map(item => {
        const unlocked = Boolean(item.unlocked);

        return `
        <div class="achievement-card ${unlocked ? "" : "locked"}">
            <div class="achievement-icon">
                ${
                    item.image
                        ? `<img src="${item.image}" alt="${escapeHtml(item.title)}" class="achievement-img">`
                        : `<span>${item.icon || "🏆"}</span>`
                }
            </div>

            <div class="achievement-name">${escapeHtml(item.title)}</div>

            <div class="achievement-status ${unlocked ? "" : "locked"}">
                ${unlocked ? "Получено" : "Закрыто"}
            </div>
        </div>
        `;
    }).join("");
}

function renderAchievementsProgress(received, total) {
    const progressText = document.getElementById("achievements-progress-text");
    const progressFill = document.getElementById("achievements-progress-fill");

    const safeReceived = Number(received) || 0;
    const safeTotal = Number(total) || 0;

    const percent = safeTotal > 0
        ? Math.round((safeReceived / safeTotal) * 100)
        : 0;

    if (progressText) {
        progressText.textContent = `${safeReceived} / ${safeTotal}`;
    }

    if (progressFill) {
        progressFill.style.width = `${Math.max(0, Math.min(100, percent))}%`;
    }
}

function achievementSkeleton() {
    return `
    <div class="achievement-card locked">
        <div class="achievement-icon">🏆</div>
        <div class="achievement-name">Загрузка...</div>
        <div class="achievement-status locked">...</div>
    </div>
    `;
}

function setText(id, value) {
    const el = document.getElementById(id);

    if (el) {
        el.textContent = value;
    }
}

function getDaysWord(number) {
    number = Math.abs(Number(number) || 0) % 100;

    const lastDigit = number % 10;

    if (number > 10 && number < 20) {
        return "дней";
    }

    if (lastDigit === 1) {
        return "день";
    }

    if (lastDigit >= 2 && lastDigit <= 4) {
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