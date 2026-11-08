let player;
let piattaforme = [];

function setup() {
    createMiniCanvas(800, 600);

    player = new Rect(400, 100, 40, 40);
    player.gravity = GRAVITY.EARTH;   // ⭐ una riga!

    piattaforme.push(new Rect(0, 550, 800, 50));
    piattaforme.push(new Rect(200, 400, 150, 20));
    piattaforme.push(new Rect(500, 300, 150, 20));
}

function draw() {
    background('skyblue');

    // Input
    if (keyIsDown('arrowleft'))       player.vel.x = -5;
    else if (keyIsDown('arrowright')) player.vel.x = 5;
    else                              player.vel.x = 0;

    // Salto (solo se tocca il suolo)
    if (keyIsDown('arrowup') && player.y >= 500) {
        player.vel.y = -12;
    }

    // Fisica
    player.update();

    // Collisioni con piattaforme
    for (const p of piattaforme) {
        if (player.collidesWith(p) && player.vel.y > 0) {
            player.y = p.y - player.h;
            player.vel.y = 0;
        }
    }

    // Disegno
    fill('brown');
    piattaforme.forEach(p => p.draw());
    fill('red');
    player.draw();
}
