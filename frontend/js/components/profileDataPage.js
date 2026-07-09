export function getProfileDataPage() {

    return `

    <div class="stats-grid">

        <div class="stat-card">
            <div class="stat-icon">🗓️</div>
            <div class="stat-info">
                <div class="stat-title">Зарегистрирован</div>
                <div class="stat-value">14 июля 2026</div>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-icon">💎</div>
            <div class="stat-info">
                <div class="stat-title">Premium</div>
                <div class="stat-value active">Активен</div>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-info">
                <div class="stat-title">Привычки</div>
                <div class="stat-value active">423</div>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-icon">🏆</div>
            <div class="stat-info">
                <div class="stat-title">Челленджи</div>
                <div class="stat-value active">27</div>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-icon">⭐</div>
            <div class="stat-info">
                <div class="stat-title">Звезды</div>
                <div class="stat-value active">1860</div>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-info">
                <div class="stat-title">Подтвержденные дни</div>
                <div class="stat-value active">542</div>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-icon">🔥</div>
            <div class="stat-info">
                <div class="stat-title">Текущий стрик</div>
                <div class="stat-value active">18 дней</div>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-icon">👑</div>
            <div class="stat-info">
                <div class="stat-title">Максимальный стрик</div>
                <div class="stat-value active">43 дня</div>
            </div>
        </div>

    </div>

    <div class="league-card">
        <div class="league-icon">🏅</div>
        <div class="league-info">
            <div class="league-title">Лига</div>
            <div class="league-name">Серебро I</div>
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
            <div class="achievement-name">500 звезд</div>
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

    `

}
