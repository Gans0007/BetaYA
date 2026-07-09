export function getProfileDataPage() {
    setTimeout(loadProfileDataPageData, 0);

    return `
    <div class="stats-grid">

        ${statCard("🗓️", "Зарегистрирован", "—", "profile-joined-at", "registration")}
        ${statCard("💎", "Premium", "—", "profile-premium", "active")}
        ${statCard("✅", "Привычки", "0", "profile-finished-habits", "active")}
        ${statCard("🏆", "Челленджи", "0", "profile-finished-challenges", "active")}
        ${statCard("ХР", "Опыт", "0", "profile-xp", "active")}
        ${statCard("✅", "Подтвержденные дни", "0", "profile-confirmed-days", "active")}
        ${statCard("🔥", "Текущий стрик", "0 дней", "profile-current-streak", "active")}
        ${statCard("👑", "Максимальный стрик", "0 дней", "profile-max-streak", "active")}

    </div>

    <div class="league-card">
        <div class="league-icon">🏅</div>
        <div class="league-info">
            <div class="league-title">Лига</div>
            <div class="league-name" id="profile-league">—</div>
        </div>
    </div>

    <div class="section-header">
        <div class="section-title">Достижения</div>
        <div class="section-link">Все достижения ›</div>
    </div>

    <div class="achievements-scroll">

        <div class="achievement-card">
            <div class="achievement-icon">🏆</div>
            <div class="achievement-name">Первая победа</div>
            <div class="achievement-status">Получено</div>
        </div>

        <div class="achievement-card">
            <div class="achievement-icon">🔥</div>
            <div class="achievement-name">100 дней</div>
            <div class="achievement-status">Получено</div>
        </div>

        <div class="achievement-card">
            <div class="achievement-icon">⭐</div>
            <div class="achievement-name">500 XP</div>
            <div class="achievement-status">Получено</div>
        </div>

        <div class="achievement-card">
            <div class="achievement-icon">💎</div>
            <div class="achievement-name">Мастер привычек</div>
            <div class="achievement-status">Получено</div>
        </div>

        <div class="achievement-card">
            <div class="achievement-icon">🔒</div>
            <div class="achievement-name">Гуру дисциплины</div>
            <div class="achievement-status locked">Заблокировано</div>
        </div>

    </div>

    <div class="achievement-progress">
        <div class="progress-text">
            <span>Получено достижений</span>
            <span>23 / 114</span>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" style="width:20%"></div>
        </div>
    </div>

    <div class="profile-footer">
        @LiteVAmbitionBot
    </div>
    `;
}

function statCard(icon, title, value, id, valueClass = "") {
    return `
    <div class="stat-card">
        <div class="stat-icon">${icon}</div>
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

        setText(
            "profile-premium",
            data.has_access ? "Активен" : "Нет"
        );

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

    } catch (error) {
        console.error("Ошибка profileDataPage:", error);
    }
}

function setText(id, value) {
    const el = document.getElementById(id);

    if (el) {
        el.textContent = value;
    }
}

function getDaysWord(number) {
    number = Math.abs(number) % 100;

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