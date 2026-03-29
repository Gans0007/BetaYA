export function openSettingsModal() {
    const existing = document.querySelector(".settings-overlay");

    if (existing) {
        existing.classList.remove("hidden");
        setTimeout(() => existing.classList.add("active"), 10);
        return;
    }

    const tg = window.Telegram?.WebApp;
    const initData = tg?.initData || "";

    const overlay = document.createElement("div");
    overlay.className = "settings-overlay hidden";

    overlay.innerHTML = `
        <div class="settings-modal">
            <div class="settings-header">
                <div class="settings-title">⚙️ Настройки</div>
                <div class="settings-close">✕</div>
            </div>

            <div class="settings-content">

                <div class="settings-block">
                    <div class="settings-label">Тон уведомлений</div>
                    <div class="settings-buttons">
                        <button data-tone="friend">🤝</button>
                        <button data-tone="gamer">🎮</button>
                        <button data-tone="spartan">⚔️</button>
                    </div>
                </div>

                <div class="settings-block">
                    <div class="settings-label">Регион</div>
                    <div class="settings-buttons">
                        <button data-tz="Europe/Kyiv">🇺🇦</button>
                        <button data-tz="Europe/Berlin">🇩🇪</button>
                        <button data-tz="Europe/Warsaw">🇵🇱</button>
                        <button data-tz="America/Vancouver">🇺🇸</button>
                        <button data-tz="Europe/Moscow">🇷🇺</button>
                    </div>
                </div>

                <div class="settings-block">
                    <div class="settings-label">Публикация медиа</div>
                    <button id="toggle-media">Загрузка...</button>
                </div>

            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    setTimeout(() => overlay.classList.add("active"), 10);

    const closeBtn = overlay.querySelector(".settings-close");
    const toneButtons = overlay.querySelectorAll("[data-tone]");
    const tzButtons = overlay.querySelectorAll("[data-tz]");
    const toggleBtn = overlay.querySelector("#toggle-media");

    closeBtn.addEventListener("click", closeModal);

    overlay.addEventListener("click", (e) => {
        if (e.target === overlay) {
            closeModal();
        }
    });

    function closeModal() {
        overlay.classList.remove("active");
        setTimeout(() => overlay.remove(), 250);
    }

    function requireInitData() {
        if (!initData) {
            showToast("Ошибка Telegram авторизации");
            throw new Error("Telegram initData is empty");
        }
    }

    async function postJSON(url, payload = {}) {
        requireInitData();

        const res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                initData,
                ...payload
            })
        });

        let data = {};
        try {
            data = await res.json();
        } catch (e) {
            data = {};
        }

        if (!res.ok || data.ok === false) {
            const errorText = data.error || `Request failed: ${res.status}`;
            throw new Error(errorText);
        }

        return data;
    }

    toneButtons.forEach((btn) => {
        btn.addEventListener("click", async () => {
            const tone = btn.dataset.tone;

            try {
                await postJSON("/api/settings/tone", { tone });

                toneButtons.forEach((b) => b.classList.remove("active"));
                btn.classList.add("active");

                showToast("Тон обновлён");
            } catch (e) {
                console.error("SET TONE ERROR", e);
                showToast("Не удалось обновить тон");
            }
        });
    });

    tzButtons.forEach((btn) => {
        btn.addEventListener("click", async () => {
            const timezone = btn.dataset.tz;

            try {
                await postJSON("/api/settings/timezone", { timezone });

                tzButtons.forEach((b) => b.classList.remove("active"));
                btn.classList.add("active");

                showToast("Регион обновлён");
            } catch (e) {
                console.error("SET TIMEZONE ERROR", e);
                showToast("Не удалось обновить регион");
            }
        });
    });

    toggleBtn.addEventListener("click", async () => {
        try {
            const data = await postJSON("/api/settings/toggle_media");

            if (typeof data.share_on === "boolean") {
                toggleBtn.classList.toggle("active", data.share_on);
                toggleBtn.innerText = data.share_on ? "🟢 Включено" : "⚪ Выключено";
            } else {
                toggleBtn.classList.toggle("active");

                if (toggleBtn.classList.contains("active")) {
                    toggleBtn.innerText = "🟢 Включено";
                } else {
                    toggleBtn.innerText = "⚪ Выключено";
                }
            }

            showToast("Настройка обновлена");
        } catch (e) {
            console.error("TOGGLE MEDIA ERROR", e);
            showToast("Не удалось обновить настройку");
        }
    });

    loadSettings(overlay, postJSON);
}

async function loadSettings(overlay, postJSON) {
    try {
        const data = await postJSON("/api/settings");

        if (!data.ok) return;

        overlay.querySelectorAll("[data-tone]").forEach((btn) => {
            btn.classList.toggle("active", btn.dataset.tone === data.tone);
        });

        overlay.querySelectorAll("[data-tz]").forEach((btn) => {
            btn.classList.toggle("active", btn.dataset.tz === data.timezone);
        });

        const toggleBtn = overlay.querySelector("#toggle-media");

        if (data.share_on) {
            toggleBtn.classList.add("active");
            toggleBtn.innerText = "🟢 Включено";
        } else {
            toggleBtn.classList.remove("active");
            toggleBtn.innerText = "⚪ Выключено";
        }
    } catch (e) {
        console.error("SETTINGS LOAD ERROR", e);
        showToast("Не удалось загрузить настройки");
    }
}

function showToast(text) {
    let toast = document.querySelector(".custom-toast");

    if (!toast) {
        toast = document.createElement("div");
        toast.className = "custom-toast";
        document.body.appendChild(toast);
    }

    toast.innerText = text;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2000);
}