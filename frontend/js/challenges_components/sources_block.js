export function renderSourcesBlock(data){
    const div = document.createElement("div")
    div.className = "sources-section"

    div.innerHTML = `
        <div class="sources-title">
            <img src="/img/sources/resources.png">
            <span>Ресурсы для роста</span>
        </div>

        <div class="sources-grid">
            <div class="source-card blue">
                <img src="/img/sources/books.png">
                <div>Книги</div>
                <b>${data.books}</b>
            </div>

            <div class="source-card green">
                <img src="/img/sources/audios.png">
                <div>Аудио</div>
                <b>${data.audios}</b>
            </div>

            <div class="source-card yellow">
                <img src="/img/sources/videos.png">
                <div>Видео</div>
                <b>${data.videos}</b>
            </div>

            <div class="source-card purple">
                <img src="/img/sources/documents.png">
                <div>Статьи</div>
                <b>${data.documents}</b>
            </div>

            <div class="source-card orange">
                <img src="/img/sources/links.png">
                <div>Ссылки</div>
                <b>${data.links}</b>
            </div>
        </div>
    `

    return div
}