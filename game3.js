/**
 * MiniLib Bounce Paddle
 * Simula una fisica di rimbalzo con una paletta controllata dal mouse.
 * Usa Ellipse, Rect, Vector e constrain().
 */

let paddle;
let ball;
let score = 0;
let gameState = 'PLAYING';

const BALL_SPEED = 7;

// === SETUP ===
function setup() {
    createMiniCanvas(640, 480);
    frameRate(60);
    
    // Inizializza la paletta (Rect) in basso
    const paddleW = 100;
    const paddleH = 15;
    paddle = new Rect(width / 2 - paddleW / 2, height - paddleH - 20, paddleW, paddleH);
    fill(70); // Grigio scuro
    
    resetBall();
    
    debugMode(false); 
}

// Funzione per resettare la palla
function resetBall() {
    // Inizializza la palla (Ellipse)
    const ballSize = 20;
    ball = new Ellipse(width / 2, height / 2, ballSize, ballSize);
    
    // Inizializza il Vettore velocità in una direzione casuale (45 gradi in alto a destra/sinistra)
    let initialX = (Math.random() > 0.5 ? 1 : -1) * BALL_SPEED * 0.7; // Componente X
    let initialY = -BALL_SPEED * 0.7; // Componente Y (verso l'alto)
    
    // Assegna il Vettore velocità
    ball.vel = new Vector(initialX, initialY);
    
    fill(255, 0, 100); // Rosa acceso
    
    gameState = 'PLAYING';
    score = 0;
}


// === GESTIONE LOGICA E FISICA ===
function updateGame() {
    // 1. Movimento della Paletta (Paddle)
    // La paletta segue la posizione X del mouse, centrata
    paddle.x = mouseX - paddle.w / 2;
    
    // **USO DI constrain()**: Limita la paletta ai bordi del canvas
    paddle.x = constrain(paddle.x, 0, width - paddle.w);
    
    // 2. Movimento della Palla (Ellipse)
    ball.x += ball.vel.x;
    ball.y += ball.vel.y;

    // 3. Collisione Palla vs Bordi
    
    // Rimbalzo orizzontale
    if (ball.x - ball.w / 2 < 0 || ball.x + ball.w / 2 > width) {
        ball.vel.x *= -1;
        // Impedisce alla palla di incastrarsi nel muro
        ball.x = constrain(ball.x, ball.w / 2, width - ball.w / 2); 
    }

    // Rimbalzo sul soffitto
    if (ball.y - ball.h / 2 < 0) {
        ball.vel.y *= -1;
        ball.y = ball.h / 2; // Riporta la palla sotto il bordo
    }
    
    // 4. Collisione Palla vs Paletta (**USO DI collidesWith**)
    // ball è un Ellipse, paddle è un Rect. collidesWith fa un check box-to-box.
    if (ball.collidesWith(paddle)) {
        // Inverte la direzione Y per farla rimbalzare verso l'alto
        ball.vel.y *= -1;
        
        // Calcolo della deviazione X in base al punto di impatto
        const impactPoint = ball.x - (paddle.x + paddle.w / 2); // Distanza dal centro
        const maxOffset = paddle.w / 2;
        
        // Mappa l'impatto (-maxOffset a +maxOffset) a una deviazione X (-1 a 1)
        const newXDirection = map(impactPoint, -maxOffset, maxOffset, -1, 1);
        
        // Normalizza e ricalcola la velocità per mantenere una velocità costante
        const newVelX = newXDirection * BALL_SPEED * 0.7;
        const newVelY = -Math.sqrt(BALL_SPEED * BALL_SPEED - newVelX * newVelX); // Mantiene il modulo del vettore
        
        ball.vel = new Vector(newVelX, newVelY);
        
        // Sposta la palla sopra la paletta per evitare collisioni multiple nello stesso frame
        ball.y = paddle.y - ball.h / 2 - 1; 
        
        score += 1;
    }
    
    // 5. Condizione di Sconfitta (Palla mancata)
    if (ball.y - ball.h / 2 > height) {
        gameState = 'GAME_OVER';
    }
}

// === DISEGNO ===
function drawGame() {
    // Disegna la palla
    fill(255, 0, 100);
    noStroke();
    ball.draw();
    
    // Disegna la paletta
    fill(70);
    paddle.draw();
}

function drawUI() {
    // Score
    fill(0);
    textSize(25);
    textAlign('left');
    textBaseline('top');
    text(`Rimbalzi: ${score}`, 10, 10);
}

function drawGameOver() {
    fill(255, 50, 50);
    textSize(60);
    textAlign('center');
    textBaseline('middle');
    text('GAME OVER', width / 2, height / 2 - 40);
    
    textSize(30);
    text(`Punti: ${score}`, width / 2, height / 2 + 10);
    
    textSize(20);
    fill(0, 0, 200);
    text('Premi INVIO per ricominciare', width / 2, height / 2 + 70);
}

function draw() {
    background(240); // Sfondo grigio chiaro

    if (gameState === 'PLAYING') {
        updateGame();
        drawGame();
        drawUI();
    } else if (gameState === 'GAME_OVER') {
        drawGame(); // Disegna la palla e la paletta ferme
        drawUI();
        drawGameOver();
    }
    
    // Assicurati che il drag sia terminato se il mouse non è premuto
    if (!mousePressed) {
        window._MiniLib._internal._draggedObject = null;
    }
}

// === GESTIONE INPUT ===
function keyPressed() {
    // Permette di attivare/disattivare il debug mode con la barra spaziatrice
    if (keyWasReleased(' ')) {
        debugMode(!Mini._internal.debugMode);
    }
    
    // Ricomincia il gioco in caso di GAME OVER
    if (gameState === 'GAME_OVER' && keyWasReleased('enter')) {
        resetBall();
    }
}