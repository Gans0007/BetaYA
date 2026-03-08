import {loadHabitsDashboard} from "./habits.js"
import {renderWeek} from "./calendar.js"
import {initNavigation} from "./navigation.js"
import {renderChatUser} from "./chat.js"

const tg = window.Telegram.WebApp
tg.expand()

const initData = tg.initData

renderWeek()
loadHabitsDashboard(initData)

renderChatUser()

initNavigation()