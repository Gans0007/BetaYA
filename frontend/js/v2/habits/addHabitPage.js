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

                        <button
                            class="add-habit-v2__name-icon"
                            type="button"
                            data-action="open-icon-picker"
                            aria-label="Выбрать значок привычки"
                        >
                            <span
                                class="add-habit-v2__selected-icon"
                                aria-hidden="true"
                            >
                                ✱
                            </span>
                        </button>

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

    <button class="add-habit-v2__suggestion" data-habit-suggestion="Не тратить на фигню">
        Не тратить на фигню
    </button>

    <span class="add-habit-v2__divider">|</span>

    <button class="add-habit-v2__suggestion" data-habit-suggestion="Откладывать деньги">
        Откладывать деньги
    </button>

    <span class="add-habit-v2__divider">|</span>

    <button class="add-habit-v2__suggestion" data-habit-suggestion="Планировать бюджет">
        Планировать бюджет
    </button>

    <span class="add-habit-v2__divider">|</span>

    <button class="add-habit-v2__suggestion" data-habit-suggestion="Читать книгу">
        Читать книгу
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

    <!-- 1. Доступен -->
    <button
        class="add-habit-v2__color is-selected"
        type="button"
        data-habit-color="blue"
        role="radio"
        aria-checked="true"
        aria-label="Голубой цвет"
    ></button>

    <!-- 2. Доступен -->
    <button
        class="add-habit-v2__color"
        type="button"
        data-habit-color="green"
        role="radio"
        aria-checked="false"
        aria-label="Зелёный цвет"
    ></button>

    <!-- 3. Доступен -->
    <button
        class="add-habit-v2__color"
        type="button"
        data-habit-color="purple"
        role="radio"
        aria-checked="false"
        aria-label="Фиолетовый цвет"
    ></button>

    <!-- 4. Закрыт -->
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

    <!-- 5. Доступен -->
    <button
        class="add-habit-v2__color"
        type="button"
        data-habit-color="red"
        role="radio"
        aria-checked="false"
        aria-label="Красный цвет"
    ></button>

    <!-- 6. Доступен -->
    <button
        class="add-habit-v2__color"
        type="button"
        data-habit-color="graphite"
        role="radio"
        aria-checked="false"
        aria-label="Графитовый цвет"
    ></button>

    <!-- 7. Закрыт -->
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

    <!-- 8. Доступен -->
    <button
        class="add-habit-v2__color"
        type="button"
        data-habit-color="brown"
        role="radio"
        aria-checked="false"
        aria-label="Кофейный цвет"
    ></button>

    <!-- 9. Закрыт -->
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

    <!-- 10. Доступен -->
    <button
        class="add-habit-v2__color"
        type="button"
        data-habit-color="silver"
        role="radio"
        aria-checked="false"
        aria-label="Серебристый цвет"
    ></button>

    <!-- 11. Закрыт -->
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

                    </button>

                </section>

            </div>

        </section>
    `
}