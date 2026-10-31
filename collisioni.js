let player;
let wall;
let mySound;
function setup() {
    createMiniCanvas(600, 400);
    player = new Sprite(ASSETS['player.png'], 50, 150, 50, 50);
    mySound = new Sound(ASSETS['fire.mp3'])
    wall = new Rect(300, 100, 20, 200);
}

function draw() {
    background(240);
    
    // Movimento del Giocatore controllato dall'input
    if (keyIsDown('arrowright')) player.x += 3;
    if (keyIsDown('arrowleft')) player.x -= 3;
    
    // Disegno dei due oggetti
    fill('gray');
    wall.draw();
    player.draw();
    
    // Controlla la collisione nel ciclo draw()
    if (player.collidesWith(wall)) {
        mySound.play();
        text("COLLISIONE!", width / 2, 50);
        
        // Logica di blocco: Riporta indietro il giocatore di 3 pixel
        if (keyIsDown('arrowright')) player.x -= 3;
        if (keyIsDown('arrowleft')) player.x += 3;
    }
}