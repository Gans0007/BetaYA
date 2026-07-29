/* =========================================================
   HABITS STORE

   Хранит состояние раздела привычек.
   Пока данные находятся в памяти браузера.
   Позже Store будет заполняться данными из API.
   ========================================================= */


/* =========================================================
   СОСТОЯНИЕ
   ========================================================= */

const habitsState = {
    habits: [],
    selectedHabitId: null,
    statistics: {
        currentStreak: 0,
        totalXp: 0
    },
    isLoading: false,
    error: null
}


/* =========================================================
   ПОЛУЧИТЬ ВСЕ ПРИВЫЧКИ
   Возвращаем копию массива, чтобы внешний код
   не мог случайно изменить Store напрямую.
   ========================================================= */

export function getHabits() {
    return [...habitsState.habits]
}


/* =========================================================
   ПОЛУЧИТЬ ПРИВЫЧКУ ПО ID
   ========================================================= */

export function getHabitById(habitId) {
    return (
        habitsState.habits.find(
            (habit) => habit.id === habitId
        ) || null
    )
}


/* =========================================================
   ЗАПИСАТЬ ПОЛНЫЙ СПИСОК ПРИВЫЧЕК
   Позже будет использоваться после получения данных API.
   ========================================================= */

export function setHabits(habits = []) {
    if (!Array.isArray(habits)) {
        console.warn(
            "Habits Store: setHabits ожидал массив"
        )

        return
    }

    habitsState.habits = [...habits]
}


/* =========================================================
   ДОБАВИТЬ ПРИВЫЧКУ
   ========================================================= */

export function addHabit(habit) {
    if (!habit || !habit.id) {
        console.warn(
            "Habits Store: невозможно добавить привычку без ID"
        )

        return null
    }

    const alreadyExists = habitsState.habits.some(
        (storedHabit) => storedHabit.id === habit.id
    )

    if (alreadyExists) {
        console.warn(
            `Habits Store: привычка "${habit.id}" уже существует`
        )

        return null
    }

    habitsState.habits.push(habit)

    return habit
}


/* =========================================================
   ОБНОВИТЬ ПРИВЫЧКУ
   ========================================================= */

export function updateHabit(habitId, changes = {}) {
    const habitIndex = habitsState.habits.findIndex(
        (habit) => habit.id === habitId
    )

    if (habitIndex === -1) {
        return null
    }

    const updatedHabit = {
        ...habitsState.habits[habitIndex],
        ...changes,
        id: habitId
    }

    habitsState.habits[habitIndex] = updatedHabit

    return updatedHabit
}


/* =========================================================
   УДАЛИТЬ ПРИВЫЧКУ
   ========================================================= */

export function removeHabit(habitId) {
    const habitIndex = habitsState.habits.findIndex(
        (habit) => habit.id === habitId
    )

    if (habitIndex === -1) {
        return null
    }

    const [removedHabit] = habitsState.habits.splice(
        habitIndex,
        1
    )

    if (habitsState.selectedHabitId === habitId) {
        habitsState.selectedHabitId = null
    }

    return removedHabit
}


/* =========================================================
   ВЫБРАТЬ ПРИВЫЧКУ
   ========================================================= */

export function selectHabit(habitId) {
    const habit = getHabitById(habitId)

    habitsState.selectedHabitId = habit
        ? habitId
        : null

    return habit
}


/* =========================================================
   ПОЛУЧИТЬ ВЫБРАННУЮ ПРИВЫЧКУ
   ========================================================= */

export function getSelectedHabit() {
    if (!habitsState.selectedHabitId) {
        return null
    }

    return getHabitById(
        habitsState.selectedHabitId
    )
}


/* =========================================================
   ОЧИСТИТЬ ВЫБОР
   ========================================================= */

export function clearSelectedHabit() {
    habitsState.selectedHabitId = null
}


/* =========================================================
   СТАТИСТИКА
   ========================================================= */

export function getHabitsStatistics() {
    return {
        ...habitsState.statistics
    }
}


export function setHabitsStatistics(statistics = {}) {
    habitsState.statistics = {
        ...habitsState.statistics,
        ...statistics
    }
}


/* =========================================================
   ЗАГРУЗКА
   ========================================================= */

export function getHabitsLoading() {
    return habitsState.isLoading
}


export function setHabitsLoading(isLoading) {
    habitsState.isLoading = Boolean(isLoading)
}


/* =========================================================
   ОШИБКА
   ========================================================= */

export function getHabitsError() {
    return habitsState.error
}


export function setHabitsError(error) {
    habitsState.error = error || null
}


/* =========================================================
   ПОЛНЫЙ СБРОС STORE
   Удобно для выхода из аккаунта и тестирования.
   ========================================================= */

export function resetHabitsStore() {
    habitsState.habits = []
    habitsState.selectedHabitId = null

    habitsState.statistics = {
        currentStreak: 0,
        totalXp: 0
    }

    habitsState.isLoading = false
    habitsState.error = null
}