Failures = [
    "/static/failures/1.jpeg",
    "/static/failures/2.jpeg",
    "/static/failures/3.jpeg",
    "/static/failures/4.webp",
    "/static/failures/5.webp",
    "/static/failures/6.jpeg",
    "/static/failures/7.jpeg",
    "/static/failures/8.webp"
]
cur_failure = 0
failure_use_image1 = true;

window.onload = ()=>{
    $("#slideshow__image").attr("src", Failures[0])
    setInterval(()=>{
        let before = cur_failure;
        cur_failure += 1
        if (cur_failure >= Failures.length){
            cur_failure = 0
        }
        let after = cur_failure;
        if (failure_use_image1){
            $("#slideshow__image").removeClass("fadein").addClass("fadeout")
            $("#slideshow__image_2").attr("src", Failures[after]).show().removeClass("fadeout").addClass("fadein")
            failure_use_image1 = !failure_use_image1
        }else{
            $("#slideshow__image_2").removeClass("fadein").addClass("fadeout")
            $("#slideshow__image").attr("src", Failures[after]).show().removeClass("fadeout").addClass("fadein")
            failure_use_image1 = !failure_use_image1
        }
    }, 4000)
}
