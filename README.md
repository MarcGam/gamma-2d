# 📘 Documentazione Completa: gamma-2d.js

Libreria JavaScript 2D minimalista ispirata a **p5.js**, progettata per creare giochi e animazioni interattive direttamente nel browser usando l'elemento `<canvas>`. Offre un'API semplice e intuitiva con supporto per sprite, animazioni, emoji, forme geometriche, collisioni pixel-perfect, drag & drop, audio e molto altro.

---

## 📑 Indice

1. [Panoramica e Filosofia](#1-panoramica-e-filosofia)
2. [Installazione e Setup](#2-installazione-e-setup)
3. [Ciclo di Vita e Hook Globali](#3-ciclo-di-vita-e-hook-globali)
4. [Proprietà Globali](#4-proprietà-globali)
5. [Gestione Canvas e Sfondo](#5-gestione-canvas-e-sfondo)
6. [Disegno Base: Fill, Stroke, Text](#6-disegno-base-fill-stroke-text)
7. [Classe `Vector`](#7-classe-vector)
8. [Funzioni Matematiche e Utility](#8-funzioni-matematiche-e-utility)
9. [Input: Tastiera e Mouse](#9-input-tastiera-e-mouse)
10. [Classe `Sprite`](#10-classe-sprite)
11. [Classe `eSprite` (Emoji Sprite)](#11-classe-esprite-emoji-sprite)
12. [Classe `Rect`](#12-classe-rect)
13. [Classe `Ellipse`](#13-classe-ellipse)
14. [Classe `Button`](#14-classe-button)
15. [Classe `Sound`](#15-classe-sound)
16. [Sistema di Tag e Gruppi](#16-sistema-di-tag-e-gruppi)
17. [Debug Mode e Frame Rate](#17-debug-mode-e-frame-rate)
18. [Esempi Completi](#18-esempi-completi)
19. [Best Practice e Note](#19-best-practice-e-note)

---

## 1. Panoramica e Filosofia

`gamma-2d.js` è una libreria **leggera** (un singolo file, nessuna dipendenza) che espone funzioni globali simili a **p5.js** (`fill`, `text`, `background`, ecc.) arricchite con classi per oggetti di gioco (`Sprite`, `Rect`, `Ellipse`, `Button`, `eSprite`, `Sound`).

**Caratteristiche principali:**

| Feature | Descrizione |
|---|---|
| 🎨 **Disegno 2D** | Funzioni globali per sfondo, forme, testo |
| 🖼️ **Sprite** | Con animazione, rotazione, flip, maschere pixel-perfect |
| 😀 **eSprite** | Sprite basati su emoji (nessuna immagine richiesta) |
| 🎮 **Collisioni** | AABB + pixel-perfect per sprite con maschera |
| 🖱️ **Input** | Mouse, tastiera, touch |
| 🖱️ **Drag & Drop** | Built-in per tutti gli oggetti |
| 🔊 **Audio** | Classe `Sound` con loop e volume |
| 🏷️ **Tag/Gruppi** | Organizzazione degli sprite per collisioni di gruppo |
| 🐞 **Debug Mode** | FPS, coordinate mouse, bounding box |

---

## 2. Installazione e Setup

Includi il file nel tuo HTML **prima** del tuo script di gioco:

```html
<script src="gamma-2d.js"></script>
<script src="game.js"></script>
<script src="https://cdn.jsdelivr.net/gh/MarcGam/gamma-2d@1.0.0/gamma-2d.js"></script>
```

### Script di gioco minimo (`game.js`)

```javascript
function setup() {
    createMiniCanvas(800, 600);
}

function draw() {
    background(200);
    fill('red');
    text('Ciao!', 20, 20);
}
```

> ⚠️ **Non serve chiamare `createMiniCanvas` se non vuoi**: la libreria crea automaticamente un canvas 600×400 al caricamento.

---

## 3. Ciclo di Vita e Hook Globali

La libreria cerca automaticamente queste funzioni globali e le chiama se definite:

| Hook | Quando viene chiamato |
|---|---|
| `setup()` | Una volta, al caricamento (dopo il DOM). |
| `draw()` | Ad ogni frame (60 FPS di default). |
| `keyPressed(event)` | Ad ogni `keydown` del browser. |
| `keyReleased(event)` | Ad ogni `keyup` del browser. |
| `mouseClicked(event)` | Ad ogni click sul canvas. |

**Nota:** `draw()` inizia ad essere chiamato **solo dopo che tutti gli sprite sono stati caricati** (se presenti).

---

## 4. Proprietà Globali

Queste proprietà sono esposte come **getter globali** (sola lettura):

| Proprietà | Tipo | Descrizione |
|---|---|---|
| `mouseX` | `number` | X del mouse **relativa al canvas** |
| `mouseY` | `number` | Y del mouse relativa al canvas |
| `mousePressed` | `boolean` | `true` se il tasto sinistro è premuto |
| `width` | `number` | Larghezza del canvas |
| `height` | `number` | Altezza del canvas |
| `frameCount` | `number` | Numero di frame disegnati dall'inizio |

```javascript
function draw() {
    if (mousePressed) {
        fill('red');
    } else {
        fill('blue');
    }
    text(`Frame: ${frameCount}`, 10, 30);
}
```

---

## 5. Gestione Canvas e Sfondo

### `createMiniCanvas(w, h)`

Crea (o ridimensiona) il canvas principale.

| Parametro | Tipo | Default | Descrizione |
|---|---|---|---|
| `w` | number | 600 | Larghezza |
| `h` | number | 400 | Altezza |

**Ritorna:** l'elemento `<canvas>`.

```javascript
createMiniCanvas(1024, 768);
```

> Se il canvas esiste già (id `minicanvas`), viene ridimensionato.

---

### `background(color | r, g, b | imagePath)`

Imposta lo sfondo. Può essere:

- **Colore CSS**: `background('skyblue')`
- **RGB**: `background(255, 200, 100)`
- **Scala di grigi**: `background(128)`
- **Immagine**: `background('assets/sfondo.png')`

```javascript
background('black');
background(30, 60, 90);
background('assets/space.jpg'); // riempie tutto il canvas
```

> ⚠️ Le immagini di sfondo vengono ridimensionate per riempire il canvas.

---

### `clear()`

Pulisce tutto il canvas (trasparente).

```javascript
function draw() {
    clear(); // utile per disegnare con scie
}
```

---

## 6. Disegno Base: Fill, Stroke, Text

### `fill(color | r, g, b)`

Imposta il colore di riempimento per le forme successive.

```javascript
fill('red');
fill(255, 0, 0);
fill(200); // grigio
```

### `stroke(color | r, g, b)`

Imposta il colore del bordo.

```javascript
stroke('black');
```

### `noStroke()`

Disattiva il bordo per le forme successive.

```javascript
noStroke();
```

### `strokeWeight(w)`

Imposta lo spessore del bordo in pixel.

```javascript
strokeWeight(4);
```

### `text(str, x, y)`

Disegna del testo.

| Parametro | Tipo | Descrizione |
|---|---|---|
| `str` | string/number | Il testo |
| `x` | number | Coordinata X |
| `y` | number | Coordinata Y |

```javascript
text('Punteggio: ' + punteggio, 10, 30);
```

### `textSize(size)`

Imposta la dimensione del font (in pixel).

```javascript
textSize(24);
```

### `textAlign(alignment)`

Imposta l'allineamento orizzontale: `'left'`, `'center'`, `'right'`.

### `textBaseline(baseline)`

Imposta l'allineamento verticale: `'top'`, `'middle'`, `'bottom'`, `'alphabetic'`.

### `textWidth(str)`

Restituisce la larghezza in pixel del testo con il font corrente.

```javascript
const w = textWidth('Ciao');
```

**Esempio completo:**

```javascript
function draw() {
    background(240);
    fill('navy');
    textSize(32);
    textAlign('center');
    textBaseline('middle');
    text('Benvenuto!', width / 2, height / 2);
    textAlign('left');
    textBaseline('alphabetic');
}
```

---

## 7. Classe `Vector`

Un vettore 2D mutable, con metodi **fluent** (ritornano `this`).

### Costruttore

```javascript
new Vector(x = 0, y = 0)
```

### Metodi d'istanza

| Metodo | Descrizione |
|---|---|
| `copy()` | Ritorna un nuovo Vector con gli stessi valori |
| `add(v)` | Somma un Vector **o uno scalare** (fluent) |
| `sub(v)` | Sottrae un Vector o scalare |
| `mult(n)` | Moltiplica per scalare |
| `div(n)` | Divide per scalare (ignora divisione per 0) |
| `mag()` | Restituisce il modulo (lunghezza) |
| `normalize()` | Normalizza a lunghezza 1 (fluent) |
| `dist(v)` | Distanza dal vettore `v` |

### Metodi statici

```javascript
Vector.add(v1, v2)   // ritorna nuovo Vector
Vector.sub(v1, v2)   // ritorna nuovo Vector
Vector.dist(v1, v2)  // numero
```

### Esempio

```javascript
const vel = new Vector(3, -2);
const acc = new Vector(0, 0.5);
vel.add(acc).mult(0.98); // attrito

// Applicare un impulso
if (keyIsDown(' ')) {
    vel.y = -10;
}
```

> 💡 `Vector` è usato internamente da `Sprite`, `Rect`, `Ellipse` e `eSprite` (proprietà `vel` e `gravityVec`).

---

## 8. Funzioni Matematiche e Utility

### `map(value, start1, stop1, start2, stop2)`

Rimappa `value` dall'intervallo `[start1, stop1]` a `[start2, stop2]`.

```javascript
const normalized = map(mouseX, 0, width, 0, 1);
```

### `constrain(value, min, max)`

Limita `value` tra `min` e `max`.

```javascript
const x = constrain(mouseX, 50, width - 50);
```

### `randomInt(min, max)`

Intero casuale **incluso** tra `min` e `max`.

```javascript
const d6 = randomInt(1, 6); // 1..6 inclusi
```

### `dist(objA, objB)`

Distanza tra **i centri** di due oggetti con proprietà `x, y, w, h`.

```javascript
const d = dist(player, nemico);
if (d < 100) { /* vicini */ }
```

> ⚠️ Non usare con `Vector`: usa `Vector.dist(v1, v2)` in quel caso.

### `shuffle(array)`

Mescola **in-place** un array (Fisher–Yates). Ritorna l'array stesso.

```javascript
const mazzo = shuffle([1, 2, 3, 4, 5]);
```

### `extractRandom(array)`

Estrae e **rimuove** un elemento casuale dall'array. Ritorna `undefined` se vuoto.

```javascript
const carta = extractRandom(mazzo);
if (carta !== undefined) { /* ... */ }
```

---

## 9. Input: Tastiera e Mouse

### `keyIsDown(key)`

Verifica se un tasto è premuto. Accetta:

- **Numero** (keyCode): `keyIsDown(37)` (freccia sinistra)
- **Stringa singola**: `keyIsDown('a')`, `keyIsDown(' ')`
- **Nome speciale**: `'arrowleft'`, `'arrowup'`, `'arrowright'`, `'arrowdown'`, `'escape'`, `'enter'`, `'backspace'`, `'tab'`, `'shift'`, `'control'`, `'alt'`

```javascript
if (keyIsDown('arrowright')) player.x += 5;
if (keyIsDown(' ')) spara();
```

### `keyWasReleased(key)`

Come `keyIsDown` ma verifica il **rilascio** nel frame corrente (utile per azioni "one-shot" da tastiera).

```javascript
if (keyWasReleased('enter')) {
    avviaPartita();
}
```

### Mouse

- `mouseX`, `mouseY` → coordinate
- `mousePressed` → `true` se premuto
- Hook `mouseClicked(event)` → chiamata ad ogni click

> Per il **click singolo ripetibile**, è meglio usare `Button.isClicked()` o gestire manualmente lo stato.

---

## 10. Classe `Sprite`

Rappresenta uno sprite basato su immagine con animazione, rotazione, flip, collisioni pixel-perfect, drag & drop, gravità.

### Costruttore

```javascript
new Sprite(imagePath, x, y, w, h, name = null, tag = null)
```

| Parametro | Tipo | Descrizione |
|---|---|---|
| `imagePath` | string | URL immagine (anche base64) |
| `x, y` | number | Posizione angolo superiore sinistro |
| `w, h` | number | Dimensioni |
| `name` | string | (opzionale) Nome univoco per `getSpriteByName` |
| `tag` | string | (opzionale) Gruppo per `getSpritesByTag` |

```javascript
const player = new Sprite('player.png', 100, 100, 64, 64, 'player', 'giocatori');
```

### Proprietà pubbliche

| Proprietà | Tipo | Descrizione |
|---|---|---|
| `x, y, w, h` | number | Posizione e dimensioni |
| `visible` | boolean | Se `false`, non viene disegnato né collide |
| `vel` | Vector | Velocità |
| `gravityVec` | Vector | Accelerazione gravitazionale |
| `rotation` | number | Rotazione in radianti |
| `flipH` | boolean | Flip orizzontale |
| `name` | string | Nome (impostato dal costruttore) |
| `tag` | string | Gruppo (impostato dal costruttore) |
| `image` | HTMLImageElement | L'immagine caricata |
| `mask` | Uint8ClampedArray | Maschera alpha per collisioni pixel-perfect |
| `frame` | object | Stato animazione |

### Metodi principali

#### `draw()`

Disegna lo sprite. Va chiamato **ogni frame** dentro `draw()`.

```javascript
function draw() {
    player.draw();
}
```

#### `animate(frameW, frameH, totalFrames, fps = 10, startFrame = 0)`

Configura un'animazione **spritesheet** (le cornici sono in orizzontale).

```javascript
player.animate(64, 64, 8, 12); // 8 frame 64x64 a 12 FPS
```

#### `changeImage(newImagePath)`

Cambia l'immagine dello sprite (ricarica anche la maschera).

```javascript
player.changeImage('player_hit.png');
```

#### `getImage()`, `getPath()`

Getter dell'immagine caricata e del percorso.

#### `flip(enable)` / `flipV(enable)`

Imposta flip orizzontale / verticale.

```javascript
player.flip(true);  // specchia orizzontalmente
player.flipV(true); // capovolge verticalmente
```

#### `rotate(degrees)`

Imposta la rotazione **in gradi** (internamente convertita in radianti).

```javascript
player.rotate(45);
```

#### `addGravity(Vector)`

Imposta la gravità applicata dall'utente (non applicata automaticamente — devi integrarla in `vel` nel tuo `draw()`).

```javascript
const GRAVITY = new Vector(0, 0.5);
player.addGravity(GRAVITY);

function draw() {
    player.vel.add(player.gravityVec);
    player.x += player.vel.x;
    player.y += player.vel.y;
    player.draw();
}
```

#### `collidesWith(otherSprite)`

Collisione **pixel-perfect** se entrambi hanno maschera, altrimenti **AABB**.

```javascript
if (player.collidesWith(nemico)) {
    console.log('COLPITO!');
}
```

#### `isHovered()`

`true` se il mouse è sopra il rettangolo dello sprite (ignora rotazione/flip).

#### `isDragged()`

Se lo sprite è sotto il mouse e premuto, lo trascina. Ritorna `true` mentre è in corso il drag.

```javascript
function draw() {
    player.isDragged(); // gestisce il drag automaticamente
    player.draw();
}
```

> 💡 Solo **un oggetto alla volta** può essere trascinato in tutta la libreria.

#### `markForDeletion()`

Marca lo sprite per l'eliminazione logica (flag `_toDelete`). Devi tu rimuoverlo dall'array nel tuo codice.

```javascript
nemico.markForDeletion();

// Nel tuo update:
nemici = nemici.filter(n => !n._toDelete);
```

#### `setTag(tag)`

Cambia il gruppo di appartenenza (aggiunge al nuovo gruppo; il vecchio gruppo **non viene pulito automaticamente** — comportamento attuale).

#### `getName()`, `getCount()`, `setCount(value)`

Metadati utili per logica di gioco.

---

## 11. Classe `eSprite` (Emoji Sprite)

Versione leggera di `Sprite` basata su **emoji** — ideale per prototipi rapidi senza asset grafici.

### Costruttore

```javascript
new eSprite(emojiText, x, y, size = 30)
```

| Parametro | Tipo | Descrizione |
|---|---|---|
| `emojiText` | string | Emoji (es. `'😀'`, `'🚀'`) |
| `x, y` | number | Posizione angolo superiore sinistro |
| `size` | number | Dimensione font in pixel |

```javascript
const player = new eSprite('🚀', 100, 100, 48);
```

### Differenze rispetto a `Sprite`

| Feature | `Sprite` | `eSprite` |
|---|---|---|
| Immagine | ✅ | ❌ (usa emoji) |
| Animazione | ✅ | ❌ |
| Collisione pixel-perfect | ✅ | ❌ (solo AABB) |
| Rotazione/Flip | ✅ | ✅ |
| Drag & Drop | ✅ | ✅ |
| Gravità | ✅ | ✅ |
| `changeImage()` | ✅ | ❌ |
| `changeEmoji()` | ❌ | ✅ |
| `getEmoji()` | ❌ | ✅ |

### Metodi

| Metodo | Descrizione |
|---|---|
| `draw()` | Disegna l'emoji |
| `changeEmoji(str)` | Cambia l'emoji |
| `getEmoji()` | Ritorna l'emoji corrente |
| `flip(enable)` / `flipV(enable)` | Flip orizzontale / verticale |
| `rotate(degrees)` | Rotazione in gradi |
| `addGravity(Vector)` | Imposta gravità |
| `collidesWith(other)` | AABB |
| `isHovered()` | Mouse sopra |
| `isDragged()` | Drag & drop |
| `markForDeletion()` | Flag eliminazione |

> ⚠️ `eSprite.w` viene calcolato **al primo `draw()`** (dipende dal rendering del font). Prima del primo draw, `w = 0`.

```javascript
const cuore = new eSprite('❤️', 100, 100, 32);
cuore.changeEmoji('💔');
```

---

## 12. Classe `Rect`

Rettangolo disegnabile, con drag & drop, collisioni, gravità.

### Costruttore

```javascript
new Rect(x, y, w, h)
```

### Proprietà

| Proprietà | Tipo |
|---|---|
| `x, y, w, h` | number |
| `visible` | boolean |
| `vel` | Vector |
| `gravityVec` | Vector |

### Metodi

| Metodo | Descrizione |
|---|---|
| `draw()` | Disegna il rettangolo con `fill`/`stroke` correnti |
| `addGravity(v)` | Imposta gravità |
| `collidesWith(other)` | AABB |
| `isHovered()` | Mouse sopra |
| `isDragged()` | Drag & drop |
| `markForDeletion()` | Flag eliminazione |

> 💡 Il colore viene da `fill()` e `stroke()` globali al momento di `draw()`.

```javascript
const piattaforma = new Rect(0, 500, 800, 20);

function draw() {
    fill('brown');
    piattaforma.draw();
}
```

---

## 13. Classe `Ellipse`

Ellisse disegnabile. **Nota:** `x` e `y` rappresentano il **centro**, non l'angolo.

### Costruttore

```javascript
new Ellipse(x, y, w, h)
```

| Parametro | Descrizione |
|---|---|
| `x, y` | **Centro** dell'ellisse |
| `w, h` | Diametri (larghezza e altezza totali) |

### Metodi

Identici a `Rect`: `draw()`, `addGravity()`, `collidesWith()`, `isHovered()`, `isDragged()`, `markForDeletion()`.

> ⚠️ **Differenza importante:** a differenza di `Rect` e `Sprite`, in `Ellipse` il punto `(x, y)` è il **centro**. In `Rect` è l'angolo superiore sinistro.

```javascript
const palla = new Ellipse(400, 300, 60, 60); // cerchio di 60px centrato in (400,300)

function draw() {
    fill('red');
    palla.draw();
}
```

---

## 14. Classe `Button`

Pulsante cliccabile con stati hover/pressed automatici.

### Costruttore

```javascript
new Button(x, y, w, h, textLabel)
```

### Proprietà pubbliche (personalizzabili)

| Proprietà | Default | Descrizione |
|---|---|---|
| `bgColor` | `'rgb(0, 150, 255)'` | Colore di sfondo |
| `hoverColor` | `'rgb(0, 180, 255)'` | Colore hover |
| `activeColor` | `'rgb(0, 100, 200)'` | Colore premuto |
| `textColor` | `'white'` | Colore testo |
| `textSize` | `20` | Dimensione testo |
| `label` | stringa | Testo del pulsante |
| `visible` | `true` | Se `false`, non disegnato e non interattivo |

### Metodi

| Metodo | Descrizione |
|---|---|
| `draw()` | Disegna il pulsante (chiama **sempre** prima `isClicked()`) |
| `isClicked()` | Ritorna `true` **una volta sola** al click (edge detection) |
| `isHovered()` | `true` se mouse sopra |

### Esempio

```javascript
let bottone = new Button(300, 400, 200, 60, 'START');

function draw() {
    background(30);
    bottone.draw();
    
    if (bottone.isClicked()) {
        console.log('Partita avviata!');
    }
}
```

> ⚠️ L'ordine conta: **prima `draw()`, poi `isClicked()`** (per aggiornare gli stati).

---

## 15. Classe `Sound`

Wrapper attorno all'elemento `<audio>` con loop e volume.

### Costruttore

```javascript
new Sound('assets/musica.mp3')
```

### Metodi

| Metodo | Descrizione |
|---|---|
| `play()` | Riproduce dall'inizio |
| `stop()` | Ferma e riavvolge |
| `loop()` | Riproduce in loop infinito |
| `noLoop()` | Disattiva il loop |
| `setVolume(v)` | Volume tra `0.0` e `1.0` |
| `isPlaying()` | `true` se in riproduzione |

### Esempio

```javascript
const bgm = new Sound('assets/background.mp3');
const esplosione = new Sound('assets/boom.wav');

function setup() {
    createMiniCanvas(800, 600);
    bgm.setVolume(0.3);
    bgm.loop();
}

function keyPressed(ev) {
    if (ev.key === ' ') esplosione.play();
}
```

> ⚠️ I browser moderni richiedono un'**interazione utente** prima di far partire l'audio. Avvia la musica in un handler (`click`, `keydown`, ecc.).

---

## 16. Sistema di Tag e Gruppi

Ogni `Sprite` può essere associato a un **tag** al momento della creazione. Tutti gli sprite con lo stesso tag vengono raccolti in un gruppo consultabile.

### `getSpriteByName(name)`

Ritorna lo sprite con quel nome (o `null`).

```javascript
const player = getSpriteByName('player');
player.x += 10;
```

> ⚠️ I nomi sono **globali**. Un nome duplicato genera un warning e sovrascrive il riferimento (ma non distrugge il vecchio sprite).

### `getSpritesByTag(tag)`

Ritorna l'array di sprite con quel tag (o `[]`).

```javascript
const nemici = getSpritesByTag('nemici');
for (const n of nemici) {
    if (n._toDelete) continue;
    if (player.collidesWith(n)) { /* ... */ }
}
```

### `collidesWithGroup(sprite, tag)`

Verifica se `sprite` collide con **uno qualsiasi** degli sprite del gruppo. Ritorna **lo sprite** che collide, o `null`.

```javascript
const colpito = collidesWithGroup(player, 'nemici');
if (colpito) {
    colpito.markForDeletion();
    punteggio += 10;
}
```

**Esempio completo:**

```javascript
let player;
let nemici = [];

function setup() {
    createMiniCanvas(800, 600);
    player = new Sprite('player.png', 400, 500, 40, 40, 'player', 'giocatori');

    for (let i = 0; i < 5; i++) {
        nemici.push(new Sprite(
            'alien.png',
            randomInt(50, 750), randomInt(50, 200),
            40, 40, null, 'nemici'
        ));
    }
}

function draw() {
    background(10);
    player.draw();
    for (const n of nemici) n.draw();

    const colpito = collidesWithGroup(player, 'nemici');
    if (colpito) {
        colpito.markForDeletion();
    }
    nemici = nemici.filter(n => !n._toDelete);
}
```

> ⚠️ `collidesWithGroup` è ottimizzato per un numero limitato di oggetti. Per centinaia/migliaia di sprite, implementa un **broad-phase** (es. spatial hashing).

---

## 17. Debug Mode e Frame Rate

### `debugMode(enabled = true)`

Attiva/disattiva la modalità debug. Mostra:

- **FPS** in alto a sinistra
- **Coordinate mouse** in alto a sinistra
- **Bounding box** colorati per tutti gli oggetti

```javascript
debugMode();        // attiva
debugMode(false);   // disattiva
debugMode(true);    // attiva esplicitamente
```

I colori dei box sono:

| Oggetto | Colore |
|---|---|
| `Sprite` | 🔴 rosso |
| `eSprite` | 🟣 viola |
| `Rect` | 🟢 lime |
| `Ellipse` | 🟢 lime |
| `Button` | 🟢 lime |

### `frameRate(fps)`

Imposta il limite di FPS (default `60`). Accetta valori ≥ 1.

```javascript
frameRate(30);
```

### `getFrameRate()`

Ritorna gli FPS medi correnti (calcolati in tempo reale).

```javascript
if (getFrameRate() < 30) {
    console.warn('Lag!');
}
```

> 💡 Internamente il loop usa `requestAnimationFrame` + limitazione software.

---

## 18. Esempi Completi

### 🎮 Esempio 1: "Clicca il quadrato"

```javascript
let punteggio = 0;
let target;

function setup() {
    createMiniCanvas(800, 600);
    spawnTarget();
}

function spawnTarget() {
    target = new Rect(
        randomInt(50, width - 100),
        randomInt(50, height - 100),
        80, 80
    );
}

function draw() {
    background(240);
    fill('orange');
    target.draw();

    fill('black');
    textSize(24);
    text('Punteggio: ' + punteggio, 20, 30);

    if (mousePressed && target.isHovered()) {
        punteggio++;
        spawnTarget();
    }
}
```

---

### 🚀 Esempio 2: Player con gravità e piattaforme

```javascript
let player, piattaforme = [], gravita = new Vector(0, 0.6);

function setup() {
    createMiniCanvas(800, 600);

    player = new Rect(400, 100, 40, 40);
    player.addGravity(gravita);

    piattaforme.push(new Rect(0, 550, 800, 50));
    piattaforme.push(new Rect(200, 400, 150, 20));
    piattaforme.push(new Rect(500, 300, 150, 20));
}

function draw() {
    background('skyblue');

    // Fisica player
    player.vel.add(player.gravityVec);
    player.x += player.vel.x;
    player.y += player.vel.y;

    // Input
    if (keyIsDown('arrowleft')) player.vel.x = -5;
    else if (keyIsDown('arrowright')) player.vel.x = 5;
    else player.vel.x = 0;

    if (keyIsDown('arrowup') && player.y >= 550 - player.h - 1) {
        player.vel.y = -12;
    }

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
```

---

### 💥 Esempio 3: Sparatutto con eSprite

```javascript
let player, proiettili = [], nemici = [], cooldown = 0;

function setup() {
    createMiniCanvas(800, 600);
    player = new eSprite('🚀', 380, 500, 40);

    for (let i = 0; i < 8; i++) {
        nemici.push(new eSprite('👾', 50 + i * 90, 60, 32));
    }
}

function draw() {
    background(10, 10, 40);

    // Movimento player
    if (keyIsDown('arrowleft')) player.x -= 6;
    if (keyIsDown('arrowright')) player.x += 6;

    // Sparo
    if (keyIsDown(' ') && cooldown <= 0) {
        const p = new eSprite('💥', player.x + 12, player.y - 20, 20);
        p.vel.y = -10;
        proiettili.push(p);
        cooldown = 15;
    }
    if (cooldown > 0) cooldown--;

    // Aggiorna proiettili
    for (const b of proiettili) {
        b.y += b.vel.y;
        if (b.y < -20) b.markForDeletion();
    }
    proiettili = proiettili.filter(b => !b._toDelete);

    // Collisioni
    for (const b of proiettili) {
        for (const n of nemici) {
            if (!n._toDelete && b.collidesWith(n)) {
                b.markForDeletion();
                n.markForDeletion();
            }
        }
    }
    proiettili = proiettili.filter(b => !b._toDelete);
    nemici = nemici.filter(n => !n._toDelete);

    // Disegno
    player.draw();
    proiettili.forEach(b => b.draw());
    nemici.forEach(n => n.draw());

    // HUD
    fill('white');
    textSize(20);
    text('Nemici: ' + nemici.length, 20, 30);
}
```

---

### 🏷️ Esempio 4: Uso completo di tag e nome

```javascript
let player;

function setup() {
    createMiniCanvas(800, 600);

    player = new Sprite('hero.png', 400, 500, 50, 50, 'hero', 'giocatori');

    for (let i = 0; i < 10; i++) {
        new Sprite('coin.png',
            randomInt(20, 750),
            randomInt(50, 550),
            24, 24, null, 'monete');
    }
}

function draw() {
    background(20);

    // Ottieni il player tramite nome (utile con editor/UI)
    const hero = getSpriteByName('hero');
    if (keyIsDown('arrowleft')) hero.x -= 4;
    if (keyIsDown('arrowright')) hero.x += 4;

    hero.draw();

    // Collisioni con gruppo "monete"
    const moneta = collidesWithGroup(hero, 'monete');
    if (moneta) {
        moneta.markForDeletion();
        hero.setCount(hero.getCount() + 1);
    }

    // Disegna tutte le monete rimaste
    for (const c of getSpritesByTag('monete')) {
        if (!c._toDelete) c.draw();
    }
}
```

---

## 19. Best Practice e Note

### ✅ Da fare

- **Chiama `draw()` su ogni oggetto** dentro il tuo `draw()` principale, dopo aver aggiornato la fisica.
- Usa **`markForDeletion()`** + filtro dell'array per rimuovere oggetti, invece di `delete`.
- Per **molti oggetti** (centinaia), evita `collidesWithGroup` con collisioni pixel-perfect: usa prima AABB.
- Usa `name` per pochi oggetti "speciali" (player, UI), `tag` per gruppi numerosi.
- Se usi immagini remote, imposta `crossOrigin` (già fatto per te) e servi da server HTTP (non `file://`).

### ⚠️ Attenzioni

| Situazione | Nota |
|---|---|
| Immagini base64 | Non aspettano il caricamento (immediate). |
| `eSprite.w` | È `0` finché non viene chiamato `draw()` la prima volta. |
| Drag & Drop | Solo **un oggetto** alla volta globalmente. |
| `Ellipse` | `x, y` è il **centro**, non l'angolo. |
| Rotazione | Il bounding box AABB **non ruota** con l'oggetto. |
| `setTag` | Non pulisce il vecchio gruppo. |
| `background(image)` | L'immagine viene stirata al canvas. |
| `keyPressed` / `keyReleased` | L'evento passato è quello nativo del browser. |

### 🔧 Personalizzazioni consigliate

- **Effetti particellari**: usa `eSprite` con `markForDeletion` e `vel`.
- **Menu**: combina `Button` + `frameCount` per fade-in.
- **Tilemap**: array di `Rect` con collisioni AABB.
- **Debug UI**: attiva `debugMode()` con un tasto (es. `'d'`).

---

## 📌 Riepilogo API — Cheat Sheet

```javascript
// === SETUP ===
createMiniCanvas(w, h)
function setup() {}
function draw() {}

// === SFONDO & STILE ===
background(color|r,g,b|imagePath)
clear()
fill(color|r,g,b)
stroke(color|r,g,b)
noStroke()
strokeWeight(n)

// === TESTO ===
text(str, x, y)
textSize(px)
textAlign('left'|'center'|'right')
textBaseline('top'|'middle'|'bottom'|'alphabetic')
textWidth(str)

// === INPUT ===
mouseX, mouseY, mousePressed
keyIsDown('a' | 'arrowleft' | 65)
keyWasReleased('enter')

// === MATH ===
map(v, s1, e1, s2, e2)
constrain(v, min, max)
randomInt(min, max)
dist(objA, objB)
shuffle(arr)
extractRandom(arr)

// === OGGETTI ===
new Vector(x, y)
new Sprite(path, x, y, w, h, name?, tag?)
new eSprite(emoji, x, y, size)
new Rect(x, y, w, h)
new Ellipse(cx, cy, w, h)
new Button(x, y, w, h, label)
new Sound(path)

// === METODI OGGETTI ===
obj.draw()
obj.collidesWith(other)
obj.isHovered()
obj.isDragged()
obj.addGravity(vector)
obj.markForDeletion()
obj.flip(bool) / obj.flipV(bool)
obj.rotate(degrees)
sprite.animate(fw, fh, n, fps)
sprite.changeImage(path)
esprite.changeEmoji(str)

// === GRUPPI ===
getSpriteByName('player')
getSpritesByTag('nemici')
collidesWithGroup(sprite, 'nemici')

// === DEBUG ===
debugMode(true|false)
frameRate(fps)
getFrameRate()

// === HOOK ===
function keyPressed(ev) {}
function keyReleased(ev) {}
function mouseClicked(ev) {}
```

---

# 🔧 Bundler GUI per gamma-2d

Ecco la versione del bundler, con le seguenti caratteristiche e migliorie:

### 🆕 Modifiche principali

| Modifica | Dettaglio |
|---|---|
| **Auto-detect libreria** | Cerca `gamma-2d.min.js`, se non esiste usa `gamma-2d.js` (come nel tuo caso) |
| **Ordine HTML corretto** | Libreria **prima** del codice gioco (così `Sprite`, `Rect`, ecc. sono disponibili anche a livello top) |
| **Helper `getAsset()`** | Funzione inclusa nell'HTML generato per accedere agli asset in modo trasparente |
| **Estensioni ampliate** | Aggiunti `.gif`, `.webp`, `.bmp`, `.ogg`, `.m4a`, `.aac` |
| **Status migliorato** | Mostra conteggio asset, dimensione output e percorso finale |
| **Validazioni più chiare** | Messaggi d'errore espliciti se la libreria non viene trovata |
| **UI più informativa** | Conteggio asset in tempo reale, indicatore presenza libreria, bottone disabilitato durante build |

### 📄 `bundler_gui.py`

```python
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import base64
import mimetypes
import pathlib
import sys


# --- FUNZIONE PER GESTIRE I PERCORSI IN PYTHON E PYINSTALLER ---
def get_base_dir():
    """Restituisce la directory base dell'applicazione (script o eseguibile)."""
    if getattr(sys, 'frozen', False):
        return pathlib.Path(sys.executable).parent
    return pathlib.Path(__file__).parent


# --- CONFIGURAZIONE ---
CURRENT_DIR = get_base_dir()


def find_minilib():
    """Cerca la libreria gamma-2d, preferendo la versione minificata."""
    candidates = ['gamma-2d.min.js', 'gamma-2d.js']
    for name in candidates:
        path = CURRENT_DIR / name
        if path.exists():
            return path
    # Fallback per il messaggio d'errore
    return CURRENT_DIR / 'gamma-2d.js'


MINILIB_FILE = find_minilib()
ASSETS_DIR = CURRENT_DIR / 'assets'

# Estensioni supportate (allineate con la libreria gamma-2d)
IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg')
AUDIO_EXTS = ('.mp3', '.wav', '.ogg', '.m4a', '.aac')
ALL_EXTS = IMAGE_EXTS + AUDIO_EXTS


class BundlerApp:
    def __init__(self, master):
        self.master = master
        master.title("gamma-2d Bundler GUI")
        master.resizable(False, False)

        self.game_file_path = ""
        self.minilib_path = MINILIB_FILE
        self.assets_dir = ASSETS_DIR

        # --- Stili ---
        style = ttk.Style()
        style.configure('TFrame', padding=10)
        style.configure('TLabel', padding=5)
        style.configure('TButton', padding=10)
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))

        main_frame = ttk.Frame(master, padding="15 15 15 15")
        main_frame.pack()

        # --- Titolo ---
        ttk.Label(
            main_frame,
            text="gamma-2d Standalone Creator",
            style='Header.TLabel'
        ).grid(row=0, column=0, columnspan=3, pady=10)

        # --- 1. File JS del gioco ---
        ttk.Label(main_frame, text="File JavaScript del Gioco (.js):").grid(row=1, column=0, sticky="w")
        self.game_path_entry = ttk.Entry(main_frame, width=40)
        self.game_path_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Sfoglia", command=self.select_game_file).grid(row=1, column=2)

        # --- 2. Nome output HTML ---
        ttk.Label(main_frame, text="Nome File Standalone (.html):").grid(row=2, column=0, sticky="w")
        self.output_name_entry = ttk.Entry(main_frame, width=40)
        self.output_name_entry.insert(0, "gioco_standalone.html")
        self.output_name_entry.grid(row=2, column=1, padx=5, pady=5)

        # --- 3. Libreria (display con indicatore) ---
        ttk.Label(main_frame, text="Libreria gamma-2d:").grid(row=3, column=0, sticky="w")
        lib_status = "✅" if self.minilib_path.exists() else "❌ (non trovata)"
        ttk.Label(
            main_frame,
            text=f"{lib_status}  {self.minilib_path.name}"
        ).grid(row=3, column=1, sticky="w")
        ttk.Label(
            main_frame,
            text=f"in: {self.minilib_path.parent.name}/",
            foreground="gray"
        ).grid(row=3, column=2, sticky="w")

        # --- 4. Assets (display con conteggio) ---
        ttk.Label(main_frame, text="Cartella Assets:").grid(row=4, column=0, sticky="w")
        ttk.Label(
            main_frame,
            text=f"📁 {self.assets_dir.name}/"
        ).grid(row=4, column=1, sticky="w")
        self.assets_count_label = ttk.Label(main_frame, text=self._get_assets_summary())
        self.assets_count_label.grid(row=4, column=2, sticky="w")

        # --- 5. Bottone principale ---
        self.bundle_button = ttk.Button(
            main_frame,
            text="🚀 Crea File Standalone",
            command=self.run_bundling
        )
        self.bundle_button.grid(row=5, column=0, columnspan=3, pady=20)

        # --- 6. Status ---
        self.status_label = ttk.Label(main_frame, text="", foreground="blue")
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)

    # ------------------------------------------------------------
    # HELPERS UI
    # ------------------------------------------------------------
    def _get_assets_summary(self):
        """Ritorna una stringa con il conteggio degli asset trovati."""
        if not self.assets_dir.exists():
            return "(cartella non trovata)"
        count = sum(
            1 for f in self.assets_dir.iterdir()
            if f.is_file() and f.suffix.lower() in ALL_EXTS
        )
        return f"({count} file trovati)" if count > 0 else "(vuota)"

    def select_game_file(self):
        """Dialog per selezionare il file JS del gioco."""
        filetypes = (
            ('JavaScript files', '*.js'),
            ('All files', '*.*')
        )
        self.game_file_path = filedialog.askopenfilename(
            initialdir=CURRENT_DIR,
            title="Seleziona il codice del gioco",
            filetypes=filetypes
        )
        if self.game_file_path:
            self.game_path_entry.delete(0, tk.END)
            self.game_path_entry.insert(0, self.game_file_path)

    # ------------------------------------------------------------
    # CONVERSIONE ASSET IN BASE64
    # ------------------------------------------------------------
    def file_to_base64(self, file_path):
        """Converte un file in stringa Base64 con MIME type corretto."""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            ext = pathlib.Path(file_path).suffix.lower()
            fallbacks = {
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.ogg': 'audio/ogg',
                '.m4a': 'audio/mp4',
                '.aac': 'audio/aac',
                '.svg': 'image/svg+xml',
                '.webp': 'image/webp',
            }
            mime_type = fallbacks.get(ext, 'application/octet-stream')

        with open(file_path, 'rb') as f:
            data = base64.b64encode(f.read()).decode('utf-8')

        return f'data:{mime_type};base64,{data}'

    # ------------------------------------------------------------
    # BUNDLING
    # ------------------------------------------------------------
    def run_bundling(self):
        """Esegue il bundling al click del bottone."""
        game_file_path = self.game_path_entry.get().strip()
        output_file_name = self.output_name_entry.get().strip()

        # --- Validazione ---
        if not game_file_path or not os.path.exists(game_file_path):
            messagebox.showerror("Errore", "Seleziona un file JavaScript valido.")
            return

        if not output_file_name:
            messagebox.showerror("Errore", "Inserisci un nome per il file di output.")
            return

        if not output_file_name.lower().endswith('.html'):
            messagebox.showerror("Errore", "Il nome del file di output deve terminare con .html")
            return

        if not self.minilib_path.exists():
            messagebox.showerror(
                "Errore",
                f"Libreria gamma-2d non trovata!\n\n"
                f"Cartella cercata:\n{self.minilib_path.parent}\n\n"
                f"Nomi accettati:\n"
                f"  • gamma-2d.js\n"
                f"  • gamma-2d.min.js\n\n"
                f"Assicurati che uno dei due file sia presente nella stessa cartella del bundler."
            )
            return

        self.status_label.config(text="⏳ Creazione in corso...", foreground="orange")
        self.bundle_button.config(state='disabled')
        self.master.update()

        try:
            # --- 1. Carica libreria e codice gioco ---
            minilib_code = self.minilib_path.read_text(encoding='utf-8')
            game_code = pathlib.Path(game_file_path).read_text(encoding='utf-8')

            # --- 2. Processa assets ---
            base64_definitions = 'const ASSETS = {};\n'
            asset_count = 0

            if self.assets_dir.exists():
                asset_files = sorted(
                    [f for f in self.assets_dir.iterdir()
                     if f.is_file() and f.suffix.lower() in ALL_EXTS],
                    key=lambda f: f.name.lower()
                )

                for asset_path in asset_files:
                    base64_string = self.file_to_base64(asset_path)
                    # Chiave = nome file (es. 'player.png')
                    base64_definitions += f"ASSETS['{asset_path.name}'] = '{base64_string}';\n"
                    asset_count += 1

            # --- 3. Template HTML ---
            # Ordine: ASSETS → LIBRERIA → CODICE GIOCO
            # (così Sprite/Sound/eSprite sono definiti anche a livello top del game code)
            html_template = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{output_file_name[:-5]}</title>
    <style>
        body {{
            margin: 0;
            background: #1a1a1a;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: sans-serif;
        }}
        canvas {{
            box-shadow: 0 0 24px rgba(0,0,0,0.6);
            border-radius: 4px;
        }}
    </style>
</head>
<body>
<script>
// ============================================================
// 1) ASSETS EMBEDDED (Base64)
// ============================================================
// Ogni file è disponibile come ASSETS['nomefile.ext']
//
// Esempi d'uso nel codice del gioco:
//   new Sprite(ASSETS['player.png'], 100, 100, 32, 32)
//   new Sound(ASSETS['boom.wav'])
//   background(ASSETS['sfondo.png'])
//
// Oppure usa l'helper getAsset() che tollera path tipo 'assets/player.png':
//   new Sprite(getAsset('assets/player.png'), 100, 100, 32, 32)
{base64_definitions}

function getAsset(path) {{
    if (!path || typeof path !== 'string') return path;
    if (path.startsWith('data:')) return path;
    const name = path.split('/').pop();
    return ASSETS[name] || path;
}}

// ============================================================
// 2) GAMMA-2D LIBRARY
// ============================================================
{minilib_code}

// ============================================================
// 3) CODICE DEL GIOCO
// ============================================================
{game_code}
</script>
</body>
</html>
"""

            # --- 4. Scrivi file ---
            output_path = CURRENT_DIR / output_file_name
            output_path.write_text(html_template.strip(), encoding='utf-8')

            size_kb = output_path.stat().st_size / 1024
            self.assets_count_label.config(text=self._get_assets_summary())

            self.status_label.config(
                text=f"✅ Creato: {output_file_name}  •  {asset_count} asset  •  {size_kb:.1f} KB",
                foreground="green"
            )

            messagebox.showinfo(
                "Successo!",
                f"File standalone creato con successo!\n\n"
                f"📁 Percorso:\n{output_path}\n\n"
                f"📦 Asset incorporati: {asset_count}\n"
                f"💾 Dimensione: {size_kb:.1f} KB"
            )

        except Exception as e:
            self.status_label.config(
                text="❌ ERRORE: controlla il messaggio",
                foreground="red"
            )
            messagebox.showerror(
                "Errore Bundling",
                f"Si è verificato un errore durante l'elaborazione:\n\n{e}"
            )
        finally:
            self.bundle_button.config(state='normal')


# --- Avvio ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BundlerApp(root)
    root.mainloop()
```

---

### 📌 Cosa fare nel tuo codice di gioco

Per sfruttare il bundler, nel gioco scrivi gli asset così:

```javascript
// ✅ Corretto (funziona in dev E nel file standalone)
const player = new Sprite(ASSETS['player.png'], 100, 100, 32, 32);
const boom = new Sound(ASSETS['boom.wav']);
background(ASSETS['sfondo.png']);

// ✅ Alternativa con helper (tollera path tipo 'assets/player.png')
const player = new Sprite(getAsset('assets/player.png'), 100, 100, 32, 32);
```

```javascript
// ❌ Da evitare (nel file standalone il path relativo non esisterà)
const player = new Sprite('assets/player.png', 100, 100, 32, 32);
```

### 🔄 Flusso consigliato (dev ↔ build)

Nel tuo `game.js`, puoi mantenere compatibilità con entrambe le modalità:

```javascript
// Fallback in dev se ASSETS non esiste
const A = (typeof ASSETS !== 'undefined') ? ASSETS : {
    'player.png': 'assets/player.png',
    'boom.wav':   'assets/boom.wav',
};

const player = new Sprite(A['player.png'], 100, 100, 32, 32);
```

Così apri `index.html` in dev con la cartella `assets/` reale, e usi il bundler per distribuire un **singolo file** senza dipendenze esterne. 🎉