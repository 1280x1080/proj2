console.log("script js successfully loaded")
const canvas=document.getElementById("canvas"),ctx=canvas.getContext("2d")

let player1Health=100;
let player2Health=100;

const lookRightAnimation= new Image();

lookRightAnimation.src="../files/images/characters/chopped_chin/standing/chopped_chin_sprite.png";


//---------------------SPRITE PROPERTIES-----------------
const frameWidth=32;
const frameHeight=64;

let p1FrameCount=0;
let p2FrameCount=0;

const totalFrames=5; //eye of rah = 8 chopped chin = 5
const frameDelay=8;  //eye of rah = 5 chopped chin = 8

let frameCounter=0;

function flipImage(image,x,y,width,height,flip,frameCount){
    ctx.save();
    if(flip){
        ctx.scale(-1,1);
        ctx.drawImage(
            image,
            frameCount*frameWidth,
            0,
            frameWidth,
            frameHeight,
            -x-width,
            y,
            width,
            height
        );
    }
    else{
        ctx.drawImage(
            image,
            frameCount*frameWidth,
            0,
            frameWidth,
            frameHeight,
            x,
            y,
            width,
            height
        );
    }
    ctx.restore();
}



function loadFrame(){
    ctx.clearRect(0,0, canvas.width, canvas.height);


    xCoord+=xVel;
    yCoord+=yVel;

    xCoord2+=xVel2;
    yCoord2+=yVel2;

    frameCounter++;

    if(frameCounter>=frameDelay){
        frameCounter=0;
        p1FrameCount=(p1FrameCount+1)%totalFrames;
        p2FrameCount=(p2FrameCount+1)%totalFrames;
    }

    //--------------------LOOK DIRECTION-----------------

    let p2FaceLeft=xCoord<xCoord2; //if true: p1--><--p2
    let p1FaceLeft=xCoord>xCoord2; //if true: p2--><--p1

    //--------------------SPRITE LOADING AND FLIP------------------
    //PLAYER 1 - SPRITE
    flipImage(
        lookRightAnimation,
        xCoord,
        spriteYCoord,
        frameWidth*3,
        frameHeight*3,
        p1FaceLeft,
        p1FrameCount
    );
    //PLAYER 1 - HIT BOX

    ctx.strokeStyle = "red";
    ctx.lineWidth = 1;
    ctx.strokeRect(xCoord, yCoord, 100, 200);

    //PLAYER 2 - SPRITE
    flipImage(
        lookRightAnimation,
        xCoord2,
        spriteYCoord2,
        frameWidth*3,
        frameHeight*3,
        p2FaceLeft,
        p2FrameCount
    );
    //PLAYER 2 - HITBOX

    ctx.strokeStyle = "blue";
    ctx.lineWidth = 1;
    ctx.strokeRect(xCoord2, yCoord2, 100, 200);


    //--------------------GROUND COLOR UNDER PLAYER--------------------

    ctx.fillStyle="red";
    ctx.fillRect(xCoord,590,100,10);

    ctx.fillStyle="blue";
    ctx.fillRect(xCoord2,590,100,10);

    requestAnimationFrame(loadFrame);

    console.log(`coord 1: (${xCoord},${yCoord}) coord 2: (${xCoord2},${yCoord2})`);
}
requestAnimationFrame(loadFrame);
