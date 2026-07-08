export function getProfileDataPage() {
    return `
<div class="profile-data-page">

    <!-- ===================== -->
    <!-- ОБЩАЯ СТАТИСТИКА -->
    <!-- ===================== -->

    <div class="data-section">

        <div class="data-grid">

            <div class="data-card">
                <div class="data-card-icon">📅</div>

                <div class="data-card-content">
                    <div class="data-card-title">
                        Регистрация
                    </div>

                    <div class="data-card-value registration-date">
                        14 июля 2026
                    </div>
                </div>
            </div>


            <div class="data-card">
                <div class="data-card-icon">💎</div>

                <div class="data-card-content">
                    <div class="data-card-title">
                        Premium
                    </div>

                    <div class="data-card-value premium-status active">
                        Активен
                    </div>
                </div>
            </div>


            <div class="data-card">
                <div class="data-card-icon">✅</div>

                <div class="data-card-content">
                    <div class="data-card-title">
                        Выполнено привычек
                    </div>

                    <div class="data-card-value habits-count">
                        423
                    </div>
                </div>
            </div>


            <div class="data-card">
                <div class="data-card-icon">🏆</div>

                <div class="data-card-content">
                    <div class="data-card-title">
                        Челленджей
                    </div>

                    <div class="data-card-value challenges-count">
                        27
                    </div>
                </div>
            </div>


            <div class="data-card">
                <div class="data-card-icon">⭐</div>

                <div class="data-card-content">
                    <div class="data-card-title">
                        Получено звёзд
                    </div>

                    <div class="data-card-value stars-count">
                        1860
                    </div>
                </div>
            </div>


            <div class="data-card">
                <div class="data-card-icon">✔</div>

                <div class="data-card-content">
                    <div class="data-card-title">
                        Подтверждений
                    </div>

                    <div class="data-card-value confirmations-count">
                        542
                    </div>
                </div>
            </div>


            <div class="data-card">
                <div class="data-card-icon">🔥</div>

                <div class="data-card-content">
                    <div class="data-card-title">
                        Текущий стрик
                    </div>

                    <div class="data-card-value current-streak">
                        18 дней
                    </div>
                </div>
            </div>


            <div class="data-card">
                <div class="data-card-icon">👑</div>

                <div class="data-card-content">
                    <div class="data-card-title">
                        Лучший стрик
                    </div>

                    <div class="data-card-value best-streak">
                        43 дня
                    </div>
                </div>
            </div>

        </div>

    </div>



    <!-- ===================== -->
    <!-- ЛИГА -->
    <!-- ===================== -->

    <div class="data-section">

        <div class="data-section-title">

            🏅 Лига

        </div>

        <div class="league-card">

            <div class="league-header">

                <div class="league-name">

                    Серебро I

                </div>

                <div class="league-level">

                    520 XP

                </div>

            </div>

            <div class="league-progress">

                <div class="league-progress-fill"></div>

            </div>

            <div class="league-description">

                До следующей лиги осталось совсем немного.
                Продолжай выполнять привычки каждый день.

            </div>

        </div>

    </div>



    <!-- ===================== -->
    <!-- ДОСТИЖЕНИЯ -->
    <!-- ===================== -->

    <div class="data-section">

        <div class="data-section-header">

            <div class="data-section-title">

                🏆 Достижения

            </div>

            <button class="view-all-button">

                Все →

            </button>

        </div>


        <div class="achievement-scroll">

            <div class="achievement-item">

                <div class="achievement-icon">

                    🥇

                </div>

                <div class="achievement-title">

                    Первая победа

                </div>

            </div>

            <div class="achievement-item">

                <div class="achievement-icon">

                    🔥

                </div>

                <div class="achievement-title">

                    100 дней

                </div>

            </div>

            <div class="achievement-item">

                <div class="achievement-icon">

                    ⭐

                </div>

                <div class="achievement-title">

                    500 звёзд

                </div>

            </div>

            <div class="achievement-item">

                <div class="achievement-icon">

                    💎

                </div>

                <div class="achievement-title">

                    Мастер

                </div>

            </div>

            <div class="achievement-item">

                <div class="achievement-icon">

                    ⚡

                </div>

                <div class="achievement-title">

                    Скорость

                </div>

            </div>

        </div>

    </div>



    <!-- ===================== -->
    <!-- ПРОГРЕСС -->
    <!-- ===================== -->

    <div class="data-section">

        <div class="data-section-title">

            📈 Получено достижений

        </div>

        <div class="achievement-progress">

            <div class="achievement-progress-bar">

                <div class="achievement-progress-fill"></div>

            </div>

            <div class="achievement-progress-text">

                23 из 114

            </div>

        </div>

    </div>



    <!-- ===================== -->
    <!-- FOOTER -->
    <!-- ===================== -->

    <div class="profile-data-footer">

        Lite Version • TrackerYA

    </div>

</div>
`;
}