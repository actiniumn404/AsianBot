let police = new Audio('/static/police.mp3');
police.loop = true
let alarm = new Audio('/static/intruder_alert.mp3');
alarm.loop = true
let bad = new Audio('/static/bad.mp3');
bad.loop = true
let tts = new Audio('/static/tts.mp3');
tts.loop = true

$(".close").click((e)=>{
    $(e.currentTarget).parent().parent().parent().hide()
})

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i <ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function notify(reason){
    fetch("/api/violations/new", {
        method: "POST",
        body: JSON.stringify({
            jwt: getCookie("token"),
            type: reason
        }),
         headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
}

Array.from($(".timestamp")).forEach((e)=>{
    let d = new Date(parseInt($(e).html()) * 1000)
    $(e).html(`${d.getHours() % 12 == 0 ? 12: d.getHours() % 12}:${d.getMinutes() + 1} ${d.getHours() >= 12 ? "PM" : "AM"} ${d.getMonth() + 1}/${d.getDate()}/${d.getFullYear()}`)
})