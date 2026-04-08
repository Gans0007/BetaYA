// ================================
// 🌐 BASE REQUEST (общий fetch)
// ================================

async function post(url, data = {}) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })

    if (!response.ok) {
        console.error("API ERROR:", url)
        return null
    }

    return await response.json()
}


// ================================
// 📊 DASHBOARD
// ================================

export async function getDashboard(initData) {
    return await post("/api/dashboard", {
        initData: initData
    })
}


// ================================
// 🎮 CHALLENGES
// ================================

export async function getChallenges(initData) {
    return await post("/api/challenges", {
        initData: initData
    })
}


// ================================
// 👤 USER (на будущее)
// ================================

export async function getUser(initData) {
    return await post("/api/user", {
        initData: initData
    })
}


// ================================
// 🧠 SETTINGS (на будущее)
// ================================

export async function updateSettings(initData, settings) {
    return await post("/api/settings", {
        initData: initData,
        settings: settings
    })
}