async function login_andrew(){
    await fetch("/api/login/asdev", {method: "POST"})
    location.pathname = "/"
}

async function login_grad(){
    await fetch("/api/login/asgrad", {method: "POST"})
    location.pathname = "/"
}

async function logout(){
    eraseCookie("token")
    location.pathname = "/"
}

function eraseCookie(name) {
    document.cookie = name + '=; Max-Age=0'
}