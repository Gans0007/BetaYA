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

export function renderUserProfileDataPage(data) {
    if (!data) return;

    setText("user-profile-joined-at", data.joined_at || "—");
    setText("user-profile-premium", data.has_access ? "Активен" : "Нет");
    setText("user-profile-finished-habits", data.finished_habits ?? 0);
    setText("user-profile-finished-challenges", data.finished_challenges ?? 0);
    setText("user-profile-xp", data.xp ?? 0);
    setText("user-profile-confirmed-days", data.total_confirmed_days ?? 0);

    setText(
        "user-profile-current-streak",
        `${data.current_streak ?? 0} ${getDaysWord(data.current_streak ?? 0)}`
    );

    setText(
        "user-profile-max-streak",
        `${data.max_streak ?? 0} ${getDaysWord(data.max_streak ?? 0)}`
    );

    setText("user-profile-league", data.league || "Бронза I");
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function getDaysWord(number) {
    number = Math.abs(number) % 100;
    const lastDigit = number % 10;

    if (number > 10 && number < 20) return "дней";
    if (lastDigit === 1) return "день";
    if (lastDigit >= 2 && lastDigit <= 4) return "дня";

    return "дней";
}