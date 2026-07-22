/**
 * Экран создания новой привычки.
 *
 * Этот файл отвечает только за разметку экрана.
 * Нажатия, выбор цвета и сохранение будут обрабатываться
 * отдельно в habitsEvents.js.
 */

export function renderAddHabitPage() {
    const root = document.getElementById("habits-v2-root")

    if (!root) {
        console.error("Add Habit V2: не найден контейнер #habits-v2-root")
        return
    }

    root.innerHTML = `
        <section class="add-habit-v2">

            <!-- Верхняя панель -->
            <header class="add-habit-v2__header">

                <button
                    class="add-habit-v2__back-button"
                    type="button"
                    data-action="close-add-habit"
                    aria-label="Вернуться к привычкам"
                >
                    <span class="add-habit-v2__back-icon" aria-hidden="true">
                        ‹
                    </span>
                </button>

                <h1 class="add-habit-v2__title">
                    Новая привычка
                </h1>

                <button
                    class="add-habit-v2__save-button"
                    type="button"
                    data-action="save-habit"
                    aria-label="Сохранить привычку"
                >
                    <span class="add-habit-v2__save-icon" aria-hidden="true">
                        ✓
                    </span>
                </button>

            </header>


            <!-- Основное содержимое -->
            <div class="add-habit-v2__content">

                <!-- Название привычки -->
                <section class="add-habit-v2__section">

                    <label
                        class="add-habit-v2__section-label"
                        for="add-habit-name"
                    >
                        Название
                    </label>

                    <div class="add-habit-v2__name-field">

                        <div
                            class="add-habit-v2__name-icon"
                            aria-hidden="true"
                        >
                            ✱
                        </div>

                        <input
                            id="add-habit-name"
                            class="add-habit-v2__name-input"
                            name="habitName"
                            type="text"
                            maxlength="60"
                            placeholder="Назовите привычку"
                            autocomplete="off"
                            autocapitalize="sentences"
                            enterkeyhint="done"
                        >

                    </div>


                    <!-- Быстрые варианты названия -->
                    <div class="add-habit-v2__suggestions">

                        <button
                            class="add-habit-v2__suggestion"
                            type="button"
                            data-habit-suggestion="Откладывать деньги"
                        >
                            <span
                                class="add-habit-v2__suggestion-icon"
                                aria-hidden="true"
                            >
                                ◫
                            </span>

                            <span class="add-habit-v2__suggestion-text">
                                Откладывать деньги
                            </span>
                        </button>

                        <div
                            class="add-habit-v2__suggestions-divider"
                            aria-hidden="true"
                        ></div>

                        <button
                            class="add-habit-v2__suggestion"
                            type="button"
                            data-habit-suggestion="Планировать бюджет"
                        >
                            <span
                                class="add-habit-v2__suggestion-icon"
                                aria-hidden="true"
                            >
                                ◇
                            </span>

                            <span class="add-habit-v2__suggestion-text">
                                Планировать бюджет
                            </span>
                        </button>

                    </div>

                </section>


                <!-- Выбор цвета -->
                <section class="add-habit-v2__section">

                    <div class="add-habit-v2__section-label">
                        Цвет
                    </div>

                    <div
                        class="add-habit-v2__colors"
                        role="radiogroup"
                        aria-label="Цвет карточки привычки"
                    >

                        <button
                            class="add-habit-v2__color is-selected"
                            type="button"
                            data-habit-color="blue"
                            role="radio"
                            aria-checked="true"
                            aria-label="Голубой цвет"
                        ></button>

                        <button
                            class="add-habit-v2__color"
                            type="button"
                            data-habit-color="green"
                            role="radio"
                            aria-checked="false"
                            aria-label="Зелёный цвет"
                        ></button>

                        <button
                            class="add-habit-v2__color"
                            type="button"
                            data-habit-color="purple"
                            role="radio"
                            aria-checked="false"
                            aria-label="Фиолетовый цвет"
                        ></button>

                        <button
                            class="add-habit-v2__color is-locked"
                            type="button"
                            data-habit-color="orange"
                            data-locked="true"
                            role="radio"
                            aria-checked="false"
                            aria-label="Оранжевый цвет, доступен с Premium"
                        >
                            <span
                                class="add-habit-v2__lock"
                                aria-hidden="true"
                            >
                                🔒
                            </span>
                        </button>

                        <button
                            class="add-habit-v2__color is-locked"
                            type="button"
                            data-habit-color="cyan"
                            data-locked="true"
                            role="radio"
                            aria-checked="false"
                            aria-label="Бирюзовый цвет, доступен с Premium"
                        >
                            <span
                                class="add-habit-v2__lock"
                                aria-hidden="true"
                            >
                                🔒
                            </span>
                        </button>

                        <button
                            class="add-habit-v2__color is-locked"
                            type="button"
                            data-habit-color="pink"
                            data-locked="true"
                            role="radio"
                            aria-checked="false"
                            aria-label="Розовый цвет, доступен с Premium"
                        >
                            <span
                                class="add-habit-v2__lock"
                                aria-hidden="true"
                            >
                                🔒
                            </span>
                        </button>

                        <button
                            class="add-habit-v2__color is-locked"
                            type="button"
                            data-habit-color="yellow"
                            data-locked="true"
                            role="radio"
                            aria-checked="false"
                            aria-label="Жёлтый цвет, доступен с Premium"
                        >
                            <span
                                class="add-habit-v2__lock"
                                aria-hidden="true"
                            >
                                🔒
                            </span>
                        </button>

                    </div>

                </section>


                <!-- Размер карточки -->
                <section class="add-habit-v2__section">

                    <div class="add-habit-v2__section-label">
                        Размер карточки
                    </div>

                    <button
                        class="add-habit-v2__size-card is-selected"
                        type="button"
                        data-habit-size="large"
                        aria-pressed="true"
                    >

                        <div
                            class="add-habit-v2__size-icon"
                            aria-hidden="true"
                        >
                            ⛶
                        </div>

                        <div class="add-habit-v2__size-copy">

                            <div class="add-habit-v2__size-title">
                                Большая
                            </div>

                            <div class="add-habit-v2__size-description">
                                Подходит для подробного описания<br>
                                и мотивации
                            </div>

                        </div>

                        <div
                            class="add-habit-v2__size-check"
                            aria-hidden="true"
                        >
                            ✓
                        </div>

                    </button>

                </section>

            </div>

        </section>
    `
}