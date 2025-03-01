    const keys={};

    let xCoord=10,yCoord=580;
    let xCoord2=890,yCoord2=580;

    let spriteYCoord=380;
    let spriteYCoord2=380;

    let xVel=0,yVel=0;
    let xVel2=0,yVel2=0;

    let personHeight=200,personHeight2=200;

    let jumpHeight=-10;
    let gravity=0.6;

    let jumpingState=false,jumpingState2=false;


    let ground=580,ground2=580;

    let rest=false, rest2=false;

    let p1Direction="R";
    let p2Direction="L";

    addEventListener("keydown",function(e){
        keys[e.code] = true;
        console.log(e.code);
    })

    addEventListener("keyup",function(e){
        keys[e.code] = false;
    })

    function player1Rest(){
        setTimeout(()=>{
            rest=false;
        },500);//500ms
    }

    function player2Rest(){
        setTimeout(()=>{
            rest2=false;
        },500)
    }




    setInterval(()=>{

        //-----------------------PLAYER 1 CONTROLS------------------------

        //-----------------------MOVEMENT CONTROLS------------------------
        if(keys["KeyD"]){
            if(xCoord<900){
                xVel=5;
            }
            else{
                xVel=0;
            }
        }
        else if (keys["KeyA"]){
            if(xCoord>0){
                xVel=-5;
            }
            else{
                xVel=0;
            }

        }
        else{
            xVel = 0;
        }

        if(keys["KeyS"]&&!jumpingState){
            if(personHeight==200){   //stand state
                yCoord+=(personHeight-100);
            }
            personHeight=100;
        }
        else{
            if(personHeight==100){ //crouch state
                yCoord-=(200-personHeight);
            }
            personHeight=200;
        }

        if(keys["KeyW"]&&!jumpingState){
            yVel=jumpHeight;
            jumpingState=true;
        }

        yVel+=gravity;
        yCoord+=yVel;
        spriteYCoord=yCoord;

        if(yCoord>=ground-personHeight){
            spriteYCoord=ground-personHeight;
            yCoord=ground-personHeight; //get back to ground
            yVel=0;
            jumpingState=false;
        }
        //-----------------------ATTACK CONTROLS--------------------------

        if(keys["KeyC"]&&!rest){
            if(Math.abs(xCoord-xCoord2)<=100 && Math.abs(yCoord-yCoord2)<=50){
                if(rest2){
                    player2Health-=20;
                }
                else{
                    player2Health-=5;
                }
            }
            rest=true;
            player1Rest();
        }
        if(keys["KeyV"]&&!rest){
            if(Math.abs(xCoord-xCoord2)<=100 && Math.abs(yCoord-yCoord2)<=50){
                if(rest2){
                    player2Health-=20;
                }
                else{
                    player2Health-=5;
                }
            }
            rest=true;
            player1Rest();
        }



        //-----------------------PLAYER 2 CONTROLS------------------------

        //-----------------------MOVEMENT CONTROLS------------------------
        if(keys["ArrowRight"]){
            if(xCoord2<900){
                xVel2=5;
            }
            else{
                xVel2=0;
            }
        }else if(keys["ArrowLeft"]){
            if(xCoord2 > 0) {
                xVel2 = -5;
            }
            else{
                xVel2 = 0;
            }
        }
        else{
            xVel2 = 0;
        }

        if(keys["ArrowDown"]&&!jumpingState2){ //stand state 2
            if(personHeight2==200){
                yCoord2+=(personHeight2-100);
            }
            personHeight2=100;
        }
        else{
            if(personHeight2==100){ //crouch state 2
                yCoord2-=(200-personHeight2);
            }
            personHeight2=200;
        }
        if(keys["ArrowUp"]&&!jumpingState2){
            yVel2=jumpHeight;
            jumpingState2=true;
        }

        yVel2+=gravity;
        yCoord2+=yVel2;
        spriteYCoord2=yCoord2;

        if(yCoord2>=ground2-personHeight2){
            yCoord2=ground2-personHeight2; //get back to ground
            yVel2=0;
            jumpingState2=false;
        }
        //-----------------------ATTACK CONTROLS--------------------------

        if(keys["ShiftRight"]&&!rest2){
            if(Math.abs(xCoord-xCoord2)<=100 && Math.abs(yCoord-yCoord2)<=50){
                if(rest){
                    player1Health-=20;
                }
                else{
                    player1Health-=5;
                }
            }
            rest2=true;
            player2Rest();
        }
        if(keys["Enter"]&&!rest2){
            if(Math.abs(xCoord-xCoord2)<=100 && Math.abs(yCoord-yCoord2)<=50){
                if(rest){
                    player1Health-=20;
                }
                else{
                    player1Health-=5;
                }
            }
            rest2=true;
            player2Rest();
        }

        document.getElementById("p1health").innerHTML = `Player 1 Health: ${player1Health}`;
        document.getElementById("p2health").innerHTML = `Player 2 Health: ${player2Health}`;

        if(rest){
            document.getElementById("p1combat").innerHTML=`Vulnerable`;
        }
        else{
            document.getElementById("p1combat").innerHTML=`Invulnerable`;
        }
        if(rest2){
            document.getElementById("p2combat").innerHTML=`Vulnerable`;
        }
        else{
            document.getElementById("p2combat").innerHTML=`Invulnerable`;
        }

    }, 16);//update per 16ms / 60fps
