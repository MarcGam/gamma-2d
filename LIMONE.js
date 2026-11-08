let s, counter;
function setup() {
    createMiniCanvas(800, 600);
s = new Sprite(ASSETS['lemon.png'],120,230,91,61);
counter=0;
}

function draw() {
    background(30, 30, 40);
    s.draw();
    if(keyIsDown(' ')){
        counter+=2;
        s.x+=3;
        s.rotate(counter);
    }
fill('yellow')
    text('Premi il tasto spazio', 40, 50);
}
