export function renderGraph(canvas, data){

    if(!canvas || !data || !data.length) return

    const ctx = canvas.getContext("2d")

    const width = canvas.clientWidth
    const height = canvas.clientHeight

    canvas.width = width
    canvas.height = height

    ctx.clearRect(0,0,width,height)

    // =========================
    // EDGE CASE (1 точка)
    // =========================

    if(data.length === 1){
        ctx.beginPath()
        ctx.arc(width/2, height/2, 3, 0, Math.PI*2)
        ctx.fillStyle = "#22c55e"
        ctx.fill()
        return
    }

    // =========================
    // МИН / МАКС
    // =========================

    const values = data.map(d => d.score)

    const min = Math.min(...values)
    const max = Math.max(...values)

    const range = max - min || 1

    // =========================
    // ТОЧКИ
    // =========================

    const points = data.map((d, i) => {

        const x = (i / (data.length - 1)) * width
        const y = height - ((d.score - min) / range) * height

        return { x, y }
    })

    // =========================
    // ЦВЕТ ПО ТРЕНДУ
    // =========================

    const trend = values[values.length - 1] - values[0]
    const color = trend >= 0 ? "#22c55e" : "#ef4444"

    // =========================
    // РИСОВАНИЕ ЛИНИИ
    // =========================

    function drawLine(alpha){

        ctx.clearRect(0,0,width,height)
        ctx.globalAlpha = alpha

        ctx.lineWidth = 2
        ctx.strokeStyle = color

        ctx.beginPath()

        for(let i = 0; i < points.length; i++){

            const p = points[i]

            if(i === 0){
                ctx.moveTo(p.x, p.y)
            }else{
                const prev = points[i - 1]
                const cx = (prev.x + p.x) / 2

                ctx.quadraticCurveTo(
                    prev.x,
                    prev.y,
                    cx,
                    (prev.y + p.y)/2
                )
            }
        }

        const last = points[points.length - 1]
        ctx.lineTo(last.x, last.y)

        ctx.stroke()

        // точка текущего дня
        ctx.globalAlpha = 1
        ctx.fillStyle = color

        ctx.beginPath()
        ctx.arc(last.x, last.y, 3, 0, Math.PI * 2)
        ctx.fill()
    }

    // =========================
    // АНИМАЦИЯ
    // =========================

    let progress = 0

    function animate(){

        progress += 0.05

        drawLine(progress)

        if(progress < 1){
            requestAnimationFrame(animate)
        }
    }

    animate()
}