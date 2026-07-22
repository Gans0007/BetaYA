export function renderHabitsPage() {

    const root = document.querySelector("#dashboard-page .page-content")

    if (!root) {
        console.error("V2: не найден .page-content")
        return
    }

    root.innerHTML = `
        <section class="habits-v2-empty">
            <div class="habits-v2-empty__content">

                <div class="habits-v2-empty__date">
                    Вт, 21 июля
                </div>

                <h1 class="habits-v2-empty__title">
                    Начните свой путь.
                </h1>

                <div class="habits-v2-empty__subtitle">
                    Создайте привычку
                </div>

                <button
                    class="habits-v2-empty__add-button"
                    type="button"
                    aria-label="Создать привычку"
                >
                    +
                </button>

            </div>
        </section>
    `
}