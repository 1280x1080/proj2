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

let dots=0;
const loadingText=document.getElementById("loadingText");

setInterval(()=>{
    dots=(dots%3)+1;
    loadingText.innerHTML="Going to the arena"+".".repeat(dots);
},500)

const arenas=[
    "../../files/images/arena/arena1.png",
    "../../files/images/arena/arena2.png",
    "../../files/images/arena/arena3.png",
]

const arenasName=[
    "Train Station",
    "Public Market",
    "Castle of Sigma"
]

const arenaImage=document.getElementById("arenaShow");
const arenaName=document.getElementById("arenaName");
let currIdx=0;

arenaImage.style.backgroundImage=`url(${arenas[currIdx]})`;
arenaName.innerHTML=arenasName[currIdx];

function prevLast(){
    if(currIdx==0){
        currIdx=arenas.length-1;
    }else{
        currIdx--;
    }
    arenaImage.style.backgroundImage=`url(${arenas[currIdx]})`;
    arenaName.innerHTML=arenasName[currIdx];
}

function prevNext(){
    if(currIdx==arenas.length-1){
        currIdx=0;
    }else{
        currIdx++;
    }
    arenaImage.style.backgroundImage=`url(${arenas[currIdx]})`;
    arenaName.innerHTML=arenasName[currIdx];

}


const characters=[
    {name: "Eye of Rah", sheet: "../../files/images/characters/eye_of_rah/standing/standing_sprite.png", frames: 8},
    {name: "Chopped Chin", sheet: "../../files/images/characters/chopped_chin/standing/chopped_chin_sprite.png", frames: 5}
]

const char1Sprite=document.getElementById("char1Display");
const char2Sprite=document.getElementById("char2Display");

let char1Name=document.getElementById("char1Name");
let char2Name=document.getElementById("char2Name");

let currChar=0;
let currChar2=0;
let currFrame=0;
let currFrame2=0;
let frameWidth=128;
let animInterval;

char1Name.innerHTML=characters[currChar].name;
char2Name.innerHTML=characters[currChar2].name;

function startAnim(){
    clearInterval(animInterval);
    animInterval=setInterval(()=>{
        currFrame=(currFrame+1)%characters[currChar].frames;
        currFrame2=(currFrame2+1)%characters[currChar2].frames;
        char1Sprite.style.backgroundPosition=`${-currFrame*frameWidth}px 0`;
        char2Sprite.style.backgroundPosition=`${-currFrame2*frameWidth}px 0`;
        char2Sprite.style.transform = "scaleX(-1)";
    }, 100)
}

function updateChar(){
    char1Sprite.style.backgroundImage=`url(${characters[currChar].sheet})`;
    char2Sprite.style.backgroundImage=`url(${characters[currChar2].sheet})`;

    char1Sprite.style.imageRendering = "pixelated";
    char2Sprite.style.imageRendering = "pixelated";
    startAnim();
}

function char1Prev(){
    currChar=(currChar==0)?characters.length-1 : currChar-1;
    char1Name.innerHTML=characters[currChar].name;
    updateChar();
}

function char1Next(){
    currChar=(currChar==characters.length-1)?0:currChar+1;
    char1Name.innerHTML=characters[currChar].name;
    updateChar();
}

function char2Prev(){
    currChar2=(currChar2==0)?characters.length-1:currChar2-1;
    char2Name.innerHTML=characters[currChar2].name;
    updateChar();
}

function char2Next(){
    currChar2=(currChar2==characters.length-1)?0:currChar2+1;
    char2Name.innerHTML=characters[currChar2].name;
    updateChar();
}

updateChar();
