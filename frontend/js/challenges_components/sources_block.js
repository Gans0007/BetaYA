const TRIBUTE_URL = "https://t.me/tribute/app?startapp=ssdz"

export function renderSourcesBlock(data){

    const section = document.createElement("section")
    section.className = "sources-section"

    section.innerHTML = `
        <h2 class="sources-title">
            Полный доступ<br>
            ко всем ресурсам
        </h2>

        <div class="sources-grid">

            <div class="source-card blue">
                <img src="/img/sources/books.png">
                <span>Книги</span>
                <b>${data.books}</b>
            </div>

            <div class="source-card green">
                <img src="/img/sources/audios.png">
                <span>Аудио</span>
                <b>${data.audios}</b>
            </div>

            <div class="source-card yellow">
                <img src="/img/sources/videos.png">
                <span>Видео</span>
                <b>${data.videos}</b>
            </div>

            <div class="source-card purple">
                <img src="/img/sources/trainings.png">
                <span>Тренировки</span>
                <b>${data.trainings}</b>
            </div>

            <div class="source-card orange">
                <img src="/img/sources/mylife.png">
                <span>Жизнь</span>
                <b>${data.mylife}</b>
            </div>

        </div>

        <p class="sources-description">
            Книги, аудио, видео, тренировки и жизнь<br>
            в одном месте.
        </p>

        <div class="sources-divider">
            <span></span>
            <b>✦</b>
            <span></span>
        </div>

        <div class="sources-access-title">
            Внутри закрытого канала ты получишь:
        </div>

        <div class="sources-benefits">

            <div class="source-benefit">
                <span class="source-benefit-mark">-</span>
                <div>
                    <b>Активное сообщество</b>
                    <p>Единомышленники, мотивация и поддержка каждый день.</p>
                </div>
            </div>

            <div class="source-benefit">
                <span class="source-benefit-mark">-</span>
                <div>
                    <b>Знания и практика</b>
                    <p>Только проверенная информация и личный опыт.</p>
                </div>
            </div>

            <div class="source-benefit">
                <span class="source-benefit-mark">-</span>
                <div>
                    <b>Спорт и дисциплина</b>
                    <p>Тренировки, челленджи и путь к сильной версии себя.</p>
                </div>
            </div>

            <div class="source-benefit">
                <span class="source-benefit-mark">-</span>
                <div>
                    <b>Общение и поддержка</b>
                    <p>Обсуждения, ответы на вопросы и помощь от участников.</p>
                </div>
            </div>

            <div class="source-benefit">
                <span class="source-benefit-mark">-</span>
                <div>
                    <b>Опыт и жизнь</b>
                    <p>Мой путь, ошибки, выводы и то, что работает на деле.</p>
                </div>
            </div>

        </div>

        <button class="sources-join-button">
            🔒 Вступить в закрытый канал
        </button>
    `

    section
        .querySelector(".sources-join-button")
        .addEventListener("click", () => {

            if(window.Telegram?.WebApp?.openTelegramLink){
                window.Telegram.WebApp.openTelegramLink(TRIBUTE_URL)
                return
            }

            window.location.href = TRIBUTE_URL

        })

    return section

}