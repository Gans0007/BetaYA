/* =========================================================
   HABIT DRAFT

   Хранит временные данные привычки.

   Используется:
   - при создании новой привычки;
   - при редактировании существующей привычки;
   - при переходе к выбору эмодзи;
   - при возвращении со страницы выбора эмодзи.
   ========================================================= */


/* =========================================================
   ЗНАЧЕНИЯ ПО УМОЛЧАНИЮ
   ========================================================= */

const DEFAULT_HABIT_DRAFT = {
    name: "",
    icon: "✱",
    color: "blue",
    size: "large"
}


/* =========================================================
   ТЕКУЩИЙ ЧЕРНОВИК
   ========================================================= */

const habitDraft = {
    ...DEFAULT_HABIT_DRAFT
}


/* =========================================================
   ID РЕДАКТИРУЕМОЙ ПРИВЫЧКИ

   null:
   создаётся новая привычка.

   string:
   редактируется существующая привычка.
   ========================================================= */

let editingHabitId = null


/* =========================================================
   НОРМАЛИЗОВАТЬ ID ПРИВЫЧКИ
   ========================================================= */

function normalizeHabitId(habitId) {
    const normalizedId = String(
        habitId ?? ""
    ).trim()

    return normalizedId || null
}


/* =========================================================
   ПОЛУЧИТЬ ЧЕРНОВИК

   Возвращаем копию, чтобы внешний код
   не изменял черновик напрямую.
   ========================================================= */

export function getHabitDraft() {
    return {
        ...habitDraft
    }
}


/* =========================================================
   ПОЛУЧИТЬ ОТДЕЛЬНОЕ ЗНАЧЕНИЕ
   ========================================================= */

export function getHabitDraftValue(key) {
    return habitDraft[key]
}


/* =========================================================
   ИЗМЕНИТЬ ОДНО ПОЛЕ
   ========================================================= */

export function setHabitDraftValue(
    key,
    value
) {
    if (!(key in DEFAULT_HABIT_DRAFT)) {
        console.warn(
            `Habit Draft: неизвестное поле "${key}"`
        )

        return
    }

    habitDraft[key] = value
}


/* =========================================================
   ОБНОВИТЬ НЕСКОЛЬКО ПОЛЕЙ

   Обновляются только разрешённые поля:
   - name;
   - icon;
   - color;
   - size.

   Прогресс привычки здесь не хранится.
   ========================================================= */

export function updateHabitDraft(
    values = {}
) {
    Object.keys(
        DEFAULT_HABIT_DRAFT
    ).forEach((key) => {
        if (key in values) {
            habitDraft[key] =
                values[key]
        }
    })
}


/* =========================================================
   ПОЛУЧИТЬ ID РЕДАКТИРУЕМОЙ ПРИВЫЧКИ
   ========================================================= */

export function getEditingHabitId() {
    return editingHabitId
}


/* =========================================================
   ПРОВЕРИТЬ РЕЖИМ РЕДАКТИРОВАНИЯ
   ========================================================= */

export function isHabitDraftEditing() {
    return Boolean(
        editingHabitId
    )
}


/* =========================================================
   НАЧАТЬ СОЗДАНИЕ НОВОЙ ПРИВЫЧКИ

   Полностью очищает предыдущий черновик
   и выключает режим редактирования.
   ========================================================= */

export function startNewHabitDraft() {
    Object.assign(
        habitDraft,
        DEFAULT_HABIT_DRAFT
    )

    editingHabitId = null

    return getHabitDraft()
}


/* =========================================================
   НАЧАТЬ РЕДАКТИРОВАНИЕ ПРИВЫЧКИ

   В черновик переносятся только поля,
   которые пользователь может изменить.

   Не переносятся и не изменяются:
   - completedToday;
   - streak;
   - xpReward;
   - weekProgress;
   - completedDates;
   - createdAt;
   - completedAt.
   ========================================================= */

export function startHabitEditDraft(
    habit
) {
    if (!habit || !habit.id) {
        console.warn(
            "Habit Draft: невозможно начать редактирование привычки без ID"
        )

        return null
    }

    const normalizedId =
        normalizeHabitId(
            habit.id
        )

    if (!normalizedId) {
        console.warn(
            "Habit Draft: получен некорректный ID привычки"
        )

        return null
    }

    editingHabitId =
        normalizedId

    Object.assign(
        habitDraft,
        {
            name:
                String(
                    habit.name ?? ""
                ),

            icon:
                String(
                    habit.icon || "✱"
                ),

            color:
                String(
                    habit.color || "blue"
                ),

            size:
                String(
                    habit.size || "large"
                )
        }
    )

    return getHabitDraft()
}


/* =========================================================
   СБРОСИТЬ ЧЕРНОВИК

   Очищает данные формы и выключает
   режим редактирования.
   ========================================================= */

export function resetHabitDraft() {
    Object.assign(
        habitDraft,
        DEFAULT_HABIT_DRAFT
    )

    editingHabitId = null
}