window.onload = function() {
    setTimeout(() => {
        document.getElementById("preloader").classList.add("hide");
    }, 3000);
}

loadButton.onclick = function() {
    setTimeout(function() {
        let bgaudio=document.getElementById("lobby-audio");
        bgaudio.play();

    }, 1000); //2000 ms delay
};
