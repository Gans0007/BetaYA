export function renderPartners(){

const root = document.getElementById("partners-root")
if(!root) return

root.innerHTML = `

<div class="partners-container">

<h2 class="partners-title">Партнерка</h2>

<div class="partners-buttons">

<button class="partners-btn">Достижения</button>
<button class="partners-btn">Партнерка</button>
<button class="partners-btn">Настройки</button>

</div>

</div>

`

}