let ship;
const GRAVITY = new Vector(0.01,0.01);
function setup() {
    createMiniCanvas(800, 600);
    ship = new Sprite(ASSETS['shuttle.png'],200,200);
    ship.addGravity(GRAVITY);
}

function draw() {
    background(30, 30, 40);
    
    ship.vel.add(ship.gravityVec);
    ship.y += ship.vel.y;
    ship.draw();
    if(keyIsDown(' '))ship.vel.y-=0.02;
    if(keyIsDown('arrowleft')) ship.vel.x-=0.01;
    //if(keyIsDown('arrowright')) ship.x+=0.01;
}
