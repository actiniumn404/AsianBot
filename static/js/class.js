let police = new Audio('/static/police.mp3');
police.loop = true
let alarm = new Audio('/static/intruder_alert.mp3');
alarm.loop = true
let bad = new Audio('/static/bad.mp3');
bad.loop = true
let tts = new Audio('/static/tts.mp3');
tts.loop = true


document.onkeydown = ()=>{
    let focus = document.activeElement
    console.log("test")

    if (focus.tagName === "IFRAME"){
        console.log("confirmed")
    }
}

document.addEventListener("visibilitychange", (event) => {
    if (document.visibilityState === "visible") {
        alarm.pause();
        alarm.currentTime = 0
        police.pause()
        police.currentTime = 0
        bad.pause()
        bad.currentTime = 0
        tts.pause()
        tts.currentTime = 0
    } else {
        police.play()
        alarm.play()
        bad.play()
        tts.play()
    }
})