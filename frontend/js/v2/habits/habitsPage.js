import { renderHabitsEmpty } from "./habitsEmpty.js"
import { renderHabitsList } from "./habitsList.js"


export function renderHabitsPage(habits = []) {
    const root = document.getElementById("habits-v2-root")

    if (!root) {
        console.error("V2: не найден #habits-v2-root")
        return
    }

    if (!Array.isArray(habits)) {
        console.error(
            "V2: renderHabitsPage ожидал массив привычек"
        )

        root.innerHTML = renderHabitsEmpty()
        return
    }

    root.innerHTML =
        habits.length === 0
            ? renderHabitsEmpty()
            : renderHabitsList(habits)
}