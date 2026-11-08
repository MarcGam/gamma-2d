// gamma-2d.js - libreria 2D minimalissima ispirata a p5.js


(function() {

    // === STATO INTERNO E MAPPATURE ===

    const _KEY_MAP = {
        'arrowleft': 37,
        'arrowup': 38,
        'arrowright': 39,
        'arrowdown': 40,
        'escape': 27,
        'enter': 13,
        'backspace': 8,
        'tab': 9,
        'shift': 16,
        'control': 17,
        'alt': 18,
        ' ': 32, // Spazio
    };

    const Mini = {
        canvas: null,
        ctx: null,
        width: 600,
        height: 400,
        bgColor: 'white',
        bgImage: null,
        fillStyle: 'black',
        strokeStyle: 'black',
        frameRate: 60,
        _mouseX: 0,
        _mouseY: 0,
        _mousePressed: false,
        _mouseWasPressed: false,
        _keysDown: {},
        _keysReleased: {},
        _running: false,
        _lastFrameTime: 0,
        _currentFPS: 0,
        _draggedObject: null,
        _noStroke: false,
        _font: '16px sans-serif',
        _textAlign: 'left',
        _textBaseline: 'alphabetic',

        // NUOVO: Stato di Debug
        debugMode: false,
        frameCount: 0,
        _spritesMap: {},
        _groupsMap: {}, //Mappa per raggruppare gli Sprite per TAG/Nome Gruppo
    };

    let _buttonClicked = false;
    let _totalSpritesToLoad = 0;
    let _spritesLoaded = 0;

    // Esporre proprietà utili in globale
    Object.defineProperties(window, {
        mouseX: {
            get: () => Mini._mouseX
        },
        mouseY: {
            get: () => Mini._mouseY
        },
        mousePressed: {
            get: () => Mini._mousePressed
        },
        width: {
            get: () => Mini.width
        },
        height: {
            get: () => Mini.height
        },
        frameCount: {
            get: () => Mini.frameCount
        },
    });

    // === NUOVE CLASSI UTILITY ===

    window.Vector = class Vector {
        constructor(x = 0, y = 0) {
            this.x = x;
            this.y = y;
        }

        copy() {
            return new Vector(this.x, this.y);
        }

        add(v) {
            if (v instanceof Vector) {
                this.x += v.x;
                this.y += v.y;
            } else {
                this.x += v;
                this.y += v;
            }
            return this;
        }

        sub(v) {
            if (v instanceof Vector) {
                this.x -= v.x;
                this.y -= v.y;
            } else {
                this.x -= v;
                this.y -= v;
            }
            return this;
        }

        mult(n) {
            this.x *= n;
            this.y *= n;
            return this;
        }

        div(n) {
            if (n !== 0) {
                this.x /= n;
                this.y /= n;
            }
            return this;
        }

        mag() {
            return Math.sqrt(this.x * this.x + this.y * this.y);
        }

        normalize() {
            const m = this.mag();
            if (m > 0) {
                this.div(m);
            }
            return this;
        }

        dist(v) {
            const dx = this.x - v.x;
            const dy = this.y - v.y;
            return Math.sqrt(dx * dx + dy * dy);
        }

        static add(v1, v2) {
            return v1.copy().add(v2);
        }

        static sub(v1, v2) {
            return v1.copy().sub(v2);
        }

        static dist(v1, v2) {
            return v1.dist(v2);
        }
    };

    // === NUOVE FUNZIONI MATEMATICHE GLOBALI ===

    window.map = function(value, start1, stop1, start2, stop2) {
        return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1));
    };

    window.constrain = function(value, min, max) {
        return Math.max(Math.min(value, max), min);
    };

    window.getFrameRate = function() {
        return Mini._currentFPS;
    };
    // <--- AGGIUNTO: Funzione globale per recuperare lo Sprite per nome
    window.getSpriteByName = function(name) {
        if (typeof name !== 'string' || !name) {
            console.error("getSpriteByName richiede una stringa non vuota come nome.");
            return null;
        }
        const sprite = Mini._spritesMap[name];
        if (!sprite) {
            console.warn(`MiniLib Warning: Sprite con nome '${name}' non trovato.`);
        }
        return sprite || null;
    };
    //Funzione per ottenere un intero casuale tra min e max (inclusi)
    window.randomInt = function(min, max) {
        // Math.ceil(min) assicura che min sia incluso
        min = Math.ceil(min);
        // Math.floor(max) assicura che max sia incluso
        max = Math.floor(max);
        // La formula standard per interi casuali inclusivi
        return Math.floor(Math.random() * (max - min + 1)) + min;
    };

    /**
     * Calcola la distanza euclidea tra i punti centrali di due oggetti di gioco.
     * Gli oggetti devono avere proprietà 'x', 'y', 'w' e 'h'.
     * NOTA: Non usare oggetti Vector, usa oggetti Sprite/Rect/Ellipse.
     * @param {Object} objA - Il primo oggetto (Sprite, Rect, Ellipse, ecc.).
     * @param {Object} objB - Il secondo oggetto (Sprite, Rect, Ellipse, ecc.).
     * @returns {number} La distanza tra i centri degli oggetti.
     */
    window.dist = function(objA, objB) {
        // Calcola il centro del primo oggetto
        const centerAx = objA.x + (objA.w / 2);
        const centerAy = objA.y + (objA.h / 2);

        // Calcola il centro del secondo oggetto
        const centerBx = objB.x + (objB.w / 2);
        const centerBy = objB.y + (objB.h / 2);

        // Calcola la distanza
        const dx = centerAx - centerBx;
        const dy = centerAy - centerBy;

        return Math.sqrt(dx * dx + dy * dy);
    };

    // FUNZIONI ARRAY UTILITY (Shuffle e Estrazione Casuale)

    /**
     * Mescola casualmente gli elementi di un array (Fisher-Yates shuffle).
     * Modifica l'array originale.
     * @param {Array} array - L'array da mescolare.
     * @returns {Array} L'array mescolato.
     */
    window.shuffle = function(array) {
        let currentIndex = array.length,
            randomIndex;

        while (currentIndex !== 0) {
            // Seleziona un elemento rimanente.
            randomIndex = Math.floor(Math.random() * currentIndex);
            currentIndex--;

            // Scambia l'elemento corrente con quello casuale.
            [array[currentIndex], array[randomIndex]] = [
                array[randomIndex], array[currentIndex]
            ];
        }
        return array;
    };

    /**
     * Estrae un elemento casuale dall'array, lo rimuove e lo restituisce.
     * Simula l'estrazione di una carta da un mazzo mescolato. Modifica l'array originale.
     * NOTA: Se l'array è vuoto, restituisce 'undefined'. È consigliato verificare la lunghezza
     * dell'array prima di chiamare questa funzione (es. 'if (array.length > 0) { ... }').
     * @param {Array} array - L'array da cui estrarre.
     * @returns {*} L'elemento estratto, o 'undefined' se l'array è vuoto.
     */
    window.extractRandom = function(array) {
        if (array.length === 0) {
            return undefined; // Ritorna undefined se il mazzo è vuoto, come richiesto.
        }
        // Sceglie un indice casuale
        const randomIndex = Math.floor(Math.random() * array.length);

        // Rimuove 1 elemento all'indice casuale e restituisce l'elemento rimosso [0]
        const extracted = array.splice(randomIndex, 1);

        return extracted[0]; // Restituisce l'elemento estratto.
    };

    // === UTILITY ESISTENTI (Mantienute) ===

    window.keyIsDown = function(key) {
        if (typeof key === 'number') return !!Mini._keysDown[key];
        if (typeof key === 'string') {
            const lowerKey = key.toLowerCase();
            if (_KEY_MAP[lowerKey]) {
                return !!Mini._keysDown[_KEY_MAP[lowerKey]];
            }
            return !!Mini._keysDown[lowerKey.charCodeAt(0)];
        }
        return false;
    };

    window.keyWasReleased = function(key) {
        if (typeof key === 'number') return !!Mini._keysReleased[key];
        if (typeof key === 'string') {
            const lowerKey = key.toLowerCase();
            if (_KEY_MAP[lowerKey]) {
                return !!Mini._keysReleased[_KEY_MAP[lowerKey]];
            }
            return !!Mini._keysReleased[lowerKey.charCodeAt(0)];
        }
        return false;
    };

    window.createMiniCanvas = function(w, h) {
        Mini.width = w || Mini.width;
        Mini.height = h || Mini.height;
        let c = document.getElementById('minicanvas');
        if (!c) {
            c = document.createElement('canvas');
            c.id = 'minicanvas';
            document.body.appendChild(c);
        }
        c.width = Mini.width;
        c.height = Mini.height;
        c.style.border = '3px solid #ccc';
        c.style.display = 'block';
        Mini.canvas = c;
        Mini.ctx = c.getContext('2d');
        return c;
    };

    function colorToCSS(a, b, c) {
        if (a === undefined) return 'black';
        if (typeof a === 'string') return a;
        if (b === undefined) {
            return `rgb(${a},${a},${a})`;
        }
        return `rgb(${a},${b},${c})`;
    }

    window.background = function(a, b, c) {
        if (typeof a === 'string' && a.match(/\.(jpeg|jpg|gif|png|webp|bmp)$/i)) {
            if (!Mini.bgImage || Mini.bgImage.src !== a) {
                Mini.bgImage = new Image();
                Mini.bgImage.src = a;
            }
        } else {
            Mini.bgColor = colorToCSS(a, b, c);
            Mini.bgImage = null;
        }

        if (!Mini.ctx) return;
        const ctx = Mini.ctx;
        ctx.save();
        if (Mini.bgImage && Mini.bgImage.complete && Mini.bgImage.naturalWidth !== 0) {
            ctx.drawImage(Mini.bgImage, 0, 0, Mini.width, Mini.height);
        } else {
            ctx.fillStyle = Mini.bgColor;
            ctx.fillRect(0, 0, Mini.width, Mini.height);
        }
        ctx.restore();
    };

    window.fill = function(a, b, c) {
        Mini.fillStyle = colorToCSS(a, b, c);
        if (Mini.ctx) Mini.ctx.fillStyle = Mini.fillStyle;
    };

    window.stroke = function(a, b, c) {
        Mini._noStroke = false;
        Mini.strokeStyle = colorToCSS(a, b, c);
        if (Mini.ctx) Mini.ctx.strokeStyle = Mini.strokeStyle;
    };

    window.noStroke = function() {
        Mini._noStroke = true;
    };

    window.strokeWeight = function(w) {
        if (Mini.ctx) Mini.ctx.lineWidth = w;
    };

    window.clear = function() {
        if (!Mini.ctx) return;
        Mini.ctx.clearRect(0, 0, Mini.width, Mini.height);
    };

    window.text = function(str, x, y) {
        if (!Mini.ctx) return;
        const ctx = Mini.ctx;
        ctx.save();
        ctx.fillStyle = Mini.fillStyle;
        ctx.font = Mini._font;
        ctx.textAlign = Mini._textAlign;
        ctx.textBaseline = Mini._textBaseline;
        ctx.fillText(String(str), x, y);
        ctx.restore();
    };

    window.textSize = function(s) {
        Mini._font = `${s}px sans-serif`;
    };

    window.textAlign = function(alignment) {
        Mini._textAlign = alignment;
    };

    window.textBaseline = function(baseline) {
        Mini._textBaseline = baseline;
    };

    window.textWidth = function(str) {
        if (!Mini.ctx) return 0;
        Mini.ctx.font = Mini._font;
        return Mini.ctx.measureText(String(str)).width;
    };

    // === FUNZIONI DI CARICAMENTO SPRITE ===

    function _checkAllSpritesLoaded() {
        if (_spritesLoaded === _totalSpritesToLoad) {
            console.log("Tutti gli sprite sono stati caricati!");
            if (typeof draw === 'function') {
                window._MiniLib._internal._running = true;
                requestAnimationFrame(_loopStep);
            }
        }
    }

    window.getSpritesByTag = function(tag) {
        if (typeof tag !== 'string' || !tag) {
            console.error("getSpritesByTag richiede una stringa non vuota come tag.");
            return [];
        }
        // Restituisce l'array del gruppo o un array vuoto se non trovato
        return Mini._groupsMap[tag] || [];
    };

    window.collidesWithGroup = function(sprite, tag) {
        const group = getSpritesByTag(tag);

        for (let i = 0; i < group.length; i++) {
            const member = group[i];

            // Importante: Controlla che non sia lo sprite stesso
            if (sprite !== member) {
                // Riutilizza il metodo collidesWith esistente (AABB o Pixel-Perfect)
                if (sprite.collidesWith(member)) {
                    // Restituisce il membro del gruppo con cui è avvenuta la collisione
                    return member;
                }
            }
        }
        // Nessuna collisione trovata
        return null;
    };

    function _loadSpriteImageAndMask(sprite, imagePath) {
        if (sprite.image && sprite.image.src === imagePath) return;

        sprite.image = new Image();
        sprite.image.crossOrigin = "Anonymous";

        // 1. Controlla se l'immagine è Base64 (non ha bisogno di attesa di rete)
        const isBase64 = imagePath.startsWith('data:');

        if (!isBase64) {
            _totalSpritesToLoad++;
        }

        sprite.image.onload = () => {
            if (!sprite._originalW) sprite.w = sprite.image.naturalWidth;
            if (!sprite._originalH) sprite.h = sprite.image.naturalHeight;

            sprite.createMask();

            if (!isBase64) {
                _spritesLoaded++;
                _checkAllSpritesLoaded();
            }
        };
        sprite.image.onerror = () => {
            console.error(`Impossibile caricare l'immagine: ${imagePath}`);
            if (!isBase64) {
                _spritesLoaded++;
                _checkAllSpritesLoaded();
            }
        };
        sprite.image.src = imagePath;

        // Se è Base64, l'onload viene chiamato immediatamente (o molto velocemente)
        // Se MiniLib non aspetta il caricamento, possiamo chiamare check subito per sicurezza.
        if (isBase64 && sprite.image.complete) {
            sprite.image.onload();
        }
    }

    // === CLASSI FORME E OGGETTI DI GIOCO ===

    window.Sprite = class Sprite {
        constructor(imagePath, x, y, w, h, name = null, tag = null) {
            this.x = x || 0;
            this.y = y || 0;
            this.w = w || 0;
            this.h = h || 0;
            this.image = null;
            this.mask = null;
            this.visible = true;
            this._toDelete = false; // Flag di eliminazione

            this._offsetX = 0;
            this._offsetY = 0;
            this._imagePath = imagePath;
            this._originalW = w;
            this._originalH = h;
            this.frame = {
                x: 0,
                y: 0,
                w: w || 0,
                h: h || 0,
                totalFrames: 1,
                currentFrame: 0,
                frameRate: 10,
                lastFrameTime: 0
            };
            this._isAnimating = false;
            this._count = 0;
            this.vel = new Vector(0, 0); // NUOVO: Vettore velocità
            this.gravityVec = new Vector(0, 0); // NUOVO: Vettore gravità
            //Rotazione e Flip
            this.rotation = 0; // Angolo in radianti
            this.flipH = false; // Capovolgimento orizzontale
            this._flipV = false; // NUOVO: Capovolgimento verticale

            // <--- AGGIUNTO: Logica di registrazione del nome
            this.name = null;
            if (name && typeof name === 'string') {
                if (Mini._spritesMap[name]) {
                    console.warn(`MiniLib Warning: Uno Sprite con nome '${name}' esiste già e la vecchia istanza è stata sovrascritta.`);
                }
                this.name = name;
                Mini._spritesMap[name] = this;
            }
            // ----------------------------------------------

            // <--- NUOVA LOGICA: Registrazione del Gruppo/Tag ---
            this.tag = tag;
            if (tag && typeof tag === 'string') {
                if (!Mini._groupsMap[tag]) {
                    Mini._groupsMap[tag] = []; // Crea l'array se non esiste
                }
                Mini._groupsMap[tag].push(this); // Aggiunge lo Sprite al gruppo
            }
            // ----------------------------------------------------

            if (imagePath) {
                _loadSpriteImageAndMask(this, imagePath);
            }
        }

        // Nuovo metodo: Imposta il tag (utile se lo sprite cambia gruppo in gioco)
        setTag(newTag) {
            // Rimuove dal vecchio gruppo (logica avanzata)

            this.tag = newTag;
            if (!Mini._groupsMap[newTag]) {
                Mini._groupsMap[newTag] = [];
            }
            Mini._groupsMap[newTag].push(this);
        }

        getName() {
            return this.name;
        }

        setCount(value) {
            this._count = value;
        }
        getCount() {
            return this._count;
        }
        changeImage(newImagePath) {
            this._imagePath = newImagePath;
            _loadSpriteImageAndMask(this, newImagePath);
        }
        getImage() {
            return this.image;
        }
        getPath() {
            return this._imagePath;
        }


        animate(frameW, frameH, totalFrames, fps = 10, startFrame = 0) {
            this.frame.w = frameW;
            this.frame.h = frameH;
            this.frame.totalFrames = totalFrames;
            this.frame.frameRate = fps;
            this.frame.currentFrame = startFrame;
            this.frame.lastFrameTime = 0;
            this._isAnimating = true;

            if (!this._originalW) this.w = frameW;
            if (!this._originalH) this.h = frameH;
        }

        _updateAnimation() {
            if (!this._isAnimating || this.frame.totalFrames <= 1) return;
            const now = performance.now();
            const period = 1000 / this.frame.frameRate;

            if (now - this.frame.lastFrameTime >= period) {
                this.frame.currentFrame = (this.frame.currentFrame + 1) % this.frame.totalFrames;
                this.frame.lastFrameTime = now;
                this.frame.x = this.frame.currentFrame * this.frame.w;
                this.frame.y = 0;
            }
        }

        createMask() {
            if (!this.image || !this.image.complete) return;
            const displayW = this.w || this.image.naturalWidth;
            const displayH = this.h || this.image.naturalHeight;
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = displayW;
            tempCanvas.height = displayH;
            const tempCtx = tempCanvas.getContext('2d');
            tempCtx.drawImage(this.image, 0, 0, displayW, displayH);
            const imageData = tempCtx.getImageData(0, 0, displayW, displayH);
            this.mask = imageData.data;
        }
        // Attiva/disattiva il capovolgimento orizzontale
        flip(enable) {
            this.flipH = !!enable;
        }

        // Attiva/disattiva il capovolgimento verticale  
        flipV(enable) {
            this._flipV = !!enable;
        }
        // Imposta la rotazione in gradi
        rotate(degrees) {
            this.rotation = degrees * (Math.PI / 180); // Converte in radianti
        }
        // NUOVO: Metodo per marcare l'oggetto per l'eliminazione
        markForDeletion() {
            this._toDelete = true;
        }

        draw() {
            this._updateAnimation();
            if (this.visible && Mini.ctx && this.image && this.image.complete) {
                const ctx = Mini.ctx;
                ctx.save();

                // Calcola il punto centrale
                const centerX = this.x + this.w / 2;
                const centerY = this.y + this.h / 2;

                // 1. TRASLAZIONE (Sposta al centro per la rotazione/flip)
                ctx.translate(centerX, centerY);

                // 2. ROTAZIONE
                if (this.rotation !== 0) {
                    ctx.rotate(this.rotation);
                }
                // 3. FLIP
                let scaleX = this.flipH ? -1 : 1;
                let scaleY = this._flipV ? -1 : 1; //Gestione flip V
                ctx.scale(scaleX, scaleY);


                // Dati da disegnare (si assume che le coordinate siano relative al centro traslato)
                const drawX = -this.w / 2;
                const drawY = -this.h / 2;

                if (this._isAnimating && this.frame.w > 0 && this.frame.h > 0) {
                    ctx.drawImage(
                        this.image,
                        this.frame.x, this.frame.y, this.frame.w, this.frame.h,
                        drawX, drawY, this.w, this.h
                    );
                } else {
                    ctx.drawImage(this.image, drawX, drawY, this.w, this.h);
                }

                // Bounding Box in debug mode (disegnato prima del restore)
                if (Mini.debugMode) {
                    ctx.strokeStyle = 'red';
                    ctx.lineWidth = 1;
                    // Disegna il box attorno alle coordinate del centro
                    ctx.strokeRect(drawX, drawY, this.w, this.h);
                }

                ctx.restore(); // Ripristina tutte le trasformazioni
            }
        }
        // Gravità:
        addGravity(gVec) {
            if (gVec instanceof Vector) {
                this.gravityVec = gVec.copy();
            } else {
                console.warn("addGravity richiede un oggetto Vector.");
            }
        }
        collidesWith(otherSprite) {
            if (!this.visible || !otherSprite.visible) return false;
            // ... (Logica di collisione esistente) ...
            if (!this.mask || !otherSprite.mask) {
                return (
                    this.x < otherSprite.x + otherSprite.w &&
                    this.x + this.w > otherSprite.x &&
                    this.y < otherSprite.y + otherSprite.h &&
                    this.y + this.h > otherSprite.y
                );
            }

            const rect1 = {
                x: this.x,
                y: this.y,
                w: this.w,
                h: this.h
            };
            const rect2 = {
                x: otherSprite.x,
                y: otherSprite.y,
                w: otherSprite.w,
                h: otherSprite.h
            };

            if (rect1.x >= rect2.x + rect2.w || rect1.x + rect1.w <= rect2.x ||
                rect1.y >= rect2.y + rect2.h || rect1.y + rect1.h <= rect2.y) {
                return false;
            }

            const overlapX = Math.max(rect1.x, rect2.x);
            const overlapY = Math.max(rect1.y, rect2.y);
            const overlapW = Math.min(rect1.x + rect1.w, rect2.x + rect2.w) - overlapX;
            const overlapH = Math.min(rect1.y + rect1.h, rect2.y + rect2.h) - overlapY;

            for (let y = 0; y < overlapH; y++) {
                for (let x = 0; x < overlapW; x++) {
                    const pixel1X = (overlapX - rect1.x) + x;
                    const pixel1Y = (overlapY - rect1.y) + y;
                    const pixel2X = (overlapX - rect2.x) + x;
                    const pixel2Y = (overlapY - rect2.y) + y;
                    const index1 = (pixel1Y * rect1.w + pixel1X) * 4;
                    const index2 = (pixel2Y * rect2.w + pixel2X) * 4;
                    if (this.mask[index1 + 3] > 0 && otherSprite.mask[index2 + 3] > 0) {
                        return true;
                    }
                }
            }
            return false;
        }

        isHovered() {
            return (
                this.visible &&
                mouseX > this.x && mouseX < this.x + this.w &&
                mouseY > this.y && mouseY < this.y + this.h
            );
        }

        isDragged() {
            if (!mousePressed) {
                Mini._draggedObject = null;
                return false;
            }

            if (Mini._draggedObject === this || (Mini._draggedObject === null && this.isHovered() && Mini._mousePressed)) {
                if (Mini._draggedObject === null) {
                    this._offsetX = mouseX - this.x;
                    this._offsetY = mouseY - this.y;
                    Mini._draggedObject = this;
                }
                this.x = mouseX - this._offsetX;
                this.y = mouseY - this._offsetY;
                return true;
            }
            return false;
        }
    };
    // ==========================================================
    // CLASSE: eSprite (Emoji Sprite) 
    // ==========================================================

    window.eSprite = class eSprite {
        /**
         * @param {string} emojiText - Il carattere emoji da disegnare (es. '😀').
         * @param {number} x - Coordinata X dell'angolo superiore sinistro.
         * @param {number} y - Coordinata Y dell'angolo superiore sinistro.
         * @param {number} [size=30] - Dimensione del carattere (in pixel).
         */
        constructor(emojiText, x, y, size = 30) {
            this.emojiText = emojiText || '😃';
            this.x = x || 0;
            this.y = y || 0;
            this.textSize = size;
            this.h = size; // Altezza base del bounding box (determinata dalla dimensione del font)
            this.w = 0; // Larghezza del bounding box (calcolata in draw() tramite textWidth)

            this.visible = true;
            this._toDelete = false; // NUOVO: Flag di eliminazione

            this._offsetX = 0;
            this._offsetY = 0;
            this.vel = new Vector(0, 0);
            this.gravityVec = new Vector(0, 0);
            // NUOVO: Rotazione e Flip
            this.rotation = 0; // Angolo in radianti
            this.flipH = false; // Capovolgimento orizzontale
            this._flipV = false; // Capovolgimento verticale
        }

        // Metodi di utilità (ereditati dalle funzionalità dello Sprite)
        // Cambia l'emoji visualizzata
        // Accetta solo una stringa emoji come nuovo valore.
        changeEmoji(newEmojiString) {
            if (typeof newEmojiString === 'string' && newEmojiString.length > 0) {
                this.emojiText = newEmojiString;
            } else {
                console.warn("changeEmoji richiede una stringa emoji valida.");
            }
            // La larghezza (this.w) verrà ricalcolata nel prossimo draw()
        }
        getEmoji() {
            return this.emojiText;
        }
        addGravity(gVec) {
            if (gVec instanceof Vector) {
                this.gravityVec = gVec.copy();
            } else {
                console.warn("addGravity richiede un oggetto Vector.");
            }
        }

        // L'eSprite utilizza una semplice collisione basata sul bounding box (rettangolo)
        collidesWith(other) {
            if (!this.visible || !other.visible) return false;
            return (this.x < other.x + other.w && this.x + this.w > other.x &&
                this.y < other.y + other.h && this.y + this.h > other.y);
        }

        isHovered() {
            return (
                this.visible &&
                mouseX > this.x && mouseX < this.x + this.w &&
                mouseY > this.y && mouseY < this.y + this.h
            );
        }

        isDragged() {
            if (!mousePressed) {
                window._MiniLib._internal._draggedObject = null;
                return false;
            }

            if (window._MiniLib._internal._draggedObject === this || (window._MiniLib._internal._draggedObject === null && this.isHovered() && Mini._mousePressed)) {
                if (window._MiniLib._internal._draggedObject === null) {
                    this._offsetX = mouseX - this.x;
                    this._offsetY = mouseY - this.y;
                    window._MiniLib._internal._draggedObject = this;
                }
                this.x = mouseX - this._offsetX;
                this.y = mouseY - this._offsetY;
                return true;
            }
            return false;
        }
        // AGGIUNGI O VERIFICA QUESTI METODI NELLA CLASSE eSprite:

        // Attiva/disattiva il capovolgimento orizzontale
        flip(enable) {
            this.flipH = !!enable;
        }

        // Attiva/disattiva il capovolgimento verticale
        flipV(enable) {
            this._flipV = !!enable;
        }

        // Imposta la rotazione in gradi
        rotate(degrees) {
            // Converte i gradi in radianti e lo salva nella proprietà
            this.rotation = degrees * (Math.PI / 180);
        }
        // NUOVO: Metodo per marcare l'oggetto per l'eliminazione
        markForDeletion() {
            this._toDelete = true;
        }

        draw() {
            if (!this.visible || !Mini.ctx) return;

            const ctx = Mini.ctx;
            ctx.save();

            // Calcola il punto centrale per la rotazione
            const centerX = this.x + this.w / 2;
            const centerY = this.y + this.h / 2;

            // Imposta lo stile del testo per calcolare la larghezza (this.w)
            textSize(this.textSize);
            this.w = textWidth(this.emojiText);

            // 1. TRASLAZIONE (Sposta al centro per la rotazione/flip)
            ctx.translate(centerX, centerY);

            // 2. ROTAZIONE
            if (this.rotation !== 0) {
                ctx.rotate(this.rotation);
            }

            // 3. FLIP (Gestisce sia orizzontale che verticale)
            let scaleX = this.flipH ? -1 : 1;
            let scaleY = this._flipV ? -1 : 1; // Gestione flip V
            ctx.scale(scaleX, scaleY);

            //let flipScale = 1;
            //if (this.flipH) {
            //   flipScale = -1;
            //}
            //ctx.scale(flipScale, 1);

            // Imposta il colore e l'allineamento
            fill('black');
            textAlign('center'); // Usa 'center' per disegnare in (0, 0)
            textBaseline('middle');

            // Calcolo Y: (0) è il centro, quindi la Y è corretta
            // Usiamo una leggera compensazione per allineare l'emoji al centro verticale del font
            let textYOffset = this.h * 0.1; // Compensazione verticale (regola il centro verticale)

            // 4. Disegna l'Emoji (a (0, 0) - drawX/drawY sono 0)
            text(this.emojiText, 0, textYOffset);

            // 5. Bounding Box (Debug Mode)
            if (Mini.debugMode) {
                ctx.strokeStyle = 'purple';
                ctx.lineWidth = 1;
                // Disegna il box attorno al centro traslato
                ctx.strokeRect(-this.w / 2, -this.h / 2, this.w, this.h);
            }

            ctx.restore();
        }

        // Metodi di Sprite non applicabili (lasciati come placeholder o rimossi)
        // Non supporta animazione o cambio immagine
    }
    window.Rect = class Rect {
        constructor(x, y, w, h) {
            this.x = x || 0;
            this.y = y || 0;
            this.w = w || 0;
            this.h = h || 0;
            this._offsetX = 0;
            this._offsetY = 0;
            this.visible = true;
            this._toDelete = false; // NUOVO: Flag di eliminazione
            this.vel = new Vector(0, 0); // NUOVO: Vettore velocità
            this.gravityVec = new Vector(0, 0); // NUOVO: Vettore gravità
        }

        draw() {
            if (!Mini.ctx || !this.visible) return;
            const ctx = Mini.ctx;
            ctx.save();
            if (!Mini._noStroke) {
                ctx.strokeStyle = Mini.strokeStyle;
                ctx.lineWidth = Mini.ctx.lineWidth || 1;
            }
            ctx.fillStyle = Mini.fillStyle;
            ctx.beginPath();
            ctx.rect(this.x, this.y, this.w, this.h);
            ctx.fill();
            if (!Mini._noStroke) ctx.stroke();

            // NUOVO: Disegna Bounding Box in debug mode
            if (Mini.debugMode) {
                ctx.strokeStyle = 'lime';
                ctx.lineWidth = 1;
                ctx.strokeRect(this.x, this.y, this.w, this.h);
            }
            ctx.restore();
        }
        // NUOVO METODO:
        addGravity(gVec) {
            if (gVec instanceof Vector) {
                this.gravityVec = gVec.copy();
            } else {
                console.warn("addGravity richiede un oggetto Vector.");
            }
        }
        // NUOVO: Metodo per marcare l'oggetto per l'eliminazione
        markForDeletion() {
            this._toDelete = true;
        }
        collidesWith(other) {
            if (!this.visible || !other.visible) return false;
            return (this.x < other.x + other.w && this.x + this.w > other.x &&
                this.y < other.y + other.h && this.y + this.h > other.y);
        }

        isHovered() {
            return (
                this.visible &&
                mouseX > this.x && mouseX < this.x + this.w &&
                mouseY > this.y && mouseY < this.y + this.h
            );
        }

        isDragged() {
            if (!mousePressed) {
                Mini._draggedObject = null;
                return false;
            }

            if (Mini._draggedObject === this || (Mini._draggedObject === null && this.isHovered() && Mini._mousePressed)) {
                if (Mini._draggedObject === null) {
                    this._offsetX = mouseX - this.x;
                    this._offsetY = mouseY - this.y;
                    Mini._draggedObject = this;
                }
                this.x = mouseX - this._offsetX;
                this.y = mouseY - this._offsetY;
                return true;
            }
            return false;
        }
    };

    window.Ellipse = class Ellipse {
        constructor(x, y, w, h) {
            this.x = x || 0;
            this.y = y || 0;
            this.w = w || 0;
            this.h = h || 0;
            this._offsetX = 0;
            this._offsetY = 0;
            this.visible = true;
            this._toDelete = false; // NUOVO: Flag di eliminazione
            this.vel = new Vector(0, 0); // NUOVO: Vettore velocità
            this.gravityVec = new Vector(0, 0); // NUOVO: Vettore gravità
        }

        draw() {
            if (!Mini.ctx || !this.visible) return;
            const ctx = Mini.ctx;
            ctx.save();
            ctx.beginPath();
            ctx.ellipse(this.x, this.y, this.w / 2, this.h / 2, 0, 0, Math.PI * 2);
            ctx.fillStyle = Mini.fillStyle;
            ctx.fill();
            if (!Mini._noStroke) {
                ctx.strokeStyle = Mini.strokeStyle;
                ctx.stroke();
            }

            // NUOVO: Disegna Bounding Box in debug mode
            if (Mini.debugMode) {
                const rectX = this.x - this.w / 2;
                const rectY = this.y - this.h / 2;
                ctx.strokeStyle = 'lime';
                ctx.lineWidth = 1;
                ctx.strokeRect(rectX, rectY, this.w, this.h);
            }
            ctx.restore();
        }
        // NUOVO METODO:
        addGravity(gVec) {
            if (gVec instanceof Vector) {
                this.gravityVec = gVec.copy();
            } else {
                console.warn("addGravity richiede un oggetto Vector.");
            }
        }
        // NUOVO: Metodo per marcare l'oggetto per l'eliminazione
        markForDeletion() {
            this._toDelete = true;
        }
        collidesWith(other) {
            if (!this.visible || !other.visible) return false;
            // Collisione box to box (come prima)
            const rect1 = {
                x: this.x - this.w / 2,
                y: this.y - this.h / 2,
                w: this.w,
                h: this.h
            };
            const rect2 = other instanceof Ellipse ? {
                x: other.x - other.w / 2,
                y: other.y - other.h / 2,
                w: other.w,
                h: other.h
            } : {
                x: other.x,
                y: other.y,
                w: other.w,
                h: other.h
            };

            return (rect1.x < rect2.x + rect2.w && rect1.x + rect1.w > rect2.x &&
                rect1.y < rect2.y + rect2.h && rect1.y + rect1.h > rect2.y);
        }

        isHovered() {
            if (!this.visible) return false;
            const left = this.x - this.w / 2;
            const right = this.x + this.w / 2;
            const top = this.y - this.h / 2;
            const bottom = this.y + this.h / 2;
            return (mouseX > left && mouseX < right && mouseY > top && mouseY < bottom);
        }

        isDragged() {
            if (!Mini._mousePressed) {
                Mini._draggedObject = null;
                return false;
            }

            if (Mini._draggedObject === this || (Mini._draggedObject === null && this.isHovered() && Mini._mousePressed)) {
                if (Mini._draggedObject === null) {
                    this._offsetX = mouseX - this.x;
                    this._offsetY = mouseY - this.y;
                    Mini._draggedObject = this;
                }
                this.x = mouseX - this._offsetX;
                this.y = mouseY - this._offsetY;
                return true;
            }
            return false;
        }
    };

    window.Button = class Button {
        constructor(x, y, w, h, textLabel) {
            this.x = x || 0;
            this.y = y || 0;
            this.w = w || 100;
            this.h = h || 40;
            this.label = textLabel || 'Button';
            this.bgColor = 'rgb(0, 150, 255)';
            this.hoverColor = 'rgb(0, 180, 255)';
            this.activeColor = 'rgb(0, 100, 200)';
            this.textColor = 'white';
            this.textSize = 20;
            this._isHovered = false;
            this._isPressed = false;
            this.visible = true;
        }

        isHovered() {
            return (
                this.visible &&
                mouseX > this.x && mouseX < this.x + this.w &&
                mouseY > this.y && mouseY < this.y + this.h
            );
        }

        isClicked() {
            if (!this.visible) return false;

            this._isHovered = this.isHovered();
            this._isPressed = this._isHovered && Mini._mousePressed;

            if (this._isHovered && Mini._mouseWasPressed && !Mini._mousePressed) {
                Mini._buttonClicked = true;
                return true;
            }
            return false;
        }

        draw() {
            if (!Mini.ctx || !this.visible) return;
            const ctx = Mini.ctx;
            let color = this.bgColor;
            if (this._isPressed) {
                color = this.activeColor;
            } else if (this._isHovered) {
                color = this.hoverColor;
            }

            ctx.save();
            ctx.fillStyle = color;
            ctx.beginPath();
            const radius = Math.min(8, this.h / 4);
            ctx.roundRect(this.x, this.y, this.w, this.h, radius);
            ctx.fill();
            ctx.restore();

            ctx.save();
            fill(this.textColor);
            textSize(this.textSize);
            textAlign('center');
            textBaseline('middle');

            const textX = this.x + this.w / 2;
            const textY = this.y + this.h / 2;

            text(this.label, textX, textY);

            // Ripristina impostazioni predefinite
            textAlign('left');
            textBaseline('alphabetic');
            ctx.restore();

            // NUOVO: Disegna Bounding Box in debug mode
            if (Mini.debugMode) {
                ctx.save();
                ctx.strokeStyle = 'lime';
                ctx.lineWidth = 1;
                ctx.strokeRect(this.x, this.y, this.w, this.h);
                ctx.restore();
            }
        }
    };

    window.Sound = class Sound {
        constructor(path) {
            this.audio = new Audio(path);
            this.audio.preload = 'auto';
            this.isLooping = false;
            this.audio.addEventListener('ended', () => {
                if (this.isLooping) {
                    this.audio.currentTime = 0;
                    this.audio.play();
                }
            });
        }

        play() {
            this.audio.play().catch(e => console.error("Errore nella riproduzione dell'audio:", e));
        }

        stop() {
            this.audio.pause();
            this.audio.currentTime = 0;
        }

        loop() {
            this.isLooping = true;
            this.play();
        }

        noLoop() {
            this.isLooping = false;
        }

        setVolume(volume) {
            if (volume >= 0 && volume <= 1) {
                this.audio.volume = volume;
            } else {
                console.warn("Il volume deve essere un valore tra 0 e 1.");
            }
        }

        isPlaying() {
            return !this.audio.paused && this.audio.currentTime > 0 && !this.audio.ended;
        }
    };


    // === TIMER E LOOP PRINCIPALE ===

    window.frameRate = function(fps) {
        Mini.frameRate = Math.max(1, fps || 60);
    };

    // NUOVO: Funzione globale per attivare/disattivare la modalità debug
    window.debugMode = function(enabled) {
        Mini.debugMode = enabled === undefined ? true : !!enabled;
    };

    function _drawDebugInfo() {
        if (!Mini.ctx) return;
        Mini.ctx.save();
        fill('rgba(0,0,0,0.7)');
        textSize(14);
        textAlign('left');
        textBaseline('top');

        const fpsText = `FPS: ${Mini._currentFPS.toFixed(1)}`;
        const mouseText = `Mouse: (${Mini._mouseX}, ${Mini._mouseY})`;

        const textX = 10;
        const textY = 10;

        text(fpsText, textX, textY);
        text(mouseText, textX, textY + 20);

        Mini.ctx.restore();
        // Ripristina i valori di stile di Mini per non interferire con draw()
        fill(Mini.fillStyle);
        stroke(Mini.strokeStyle);
        textSize(parseInt(Mini._font));
    }

    function _loopStep(timestamp) {
        if (!Mini._running) return;
        const period = 1000 / Mini.frameRate;
        if (!Mini._lastFrameTime) Mini._lastFrameTime = timestamp;
        const elapsed = timestamp - Mini._lastFrameTime;

        if (elapsed >= period) {
            Mini._currentFPS = 1000 / elapsed; // Calcola FPS corrente
            Mini._lastFrameTime = timestamp - (elapsed % period);

            try {
                if (typeof draw === 'function') {
                    // Gestione Sfondo
                    if (Mini.bgImage && Mini.bgImage.complete && Mini.bgImage.naturalWidth !== 0) {
                        Mini.ctx.drawImage(Mini.bgImage, 0, 0, Mini.width, Mini.height);
                    } else {
                        Mini.ctx.save();
                        Mini.ctx.fillStyle = Mini.bgColor;
                        Mini.ctx.fillRect(0, 0, Mini.width, Mini.height);
                        Mini.ctx.restore();
                    }

                    Mini._noStroke = false;
                    Mini.frameCount++;
                    // Esecuzione logica di gioco
                    draw();

                    // Disegna informazioni di debug
                    if (Mini.debugMode) {
                        _drawDebugInfo();
                    }
                }
            } catch (e) {
                console.error('Errore in draw():', e);
                Mini._running = false;
            }

            Mini._mouseWasPressed = Mini._mousePressed;
            Mini._keysReleased = {};
        }
        requestAnimationFrame(_loopStep);
    }

    // === INIZIALIZZAZIONE E GESTIONE EVENTI ===

    function getKeyMapping(ev) {
        const mappings = [];
        mappings.push(ev.keyCode);
        if (ev.key.length === 1 && ev.key.match(/[a-z0-9]/i)) {
            mappings.push(ev.key.toLowerCase().charCodeAt(0));
        }
        return mappings;
    }

    function init() {
        // ... (Logica di inizializzazione canvas esistente) ...
        if (!document.getElementById('minicanvas')) {
            createMiniCanvas(Mini.width, Mini.height);
        } else {
            const c = document.getElementById('minicanvas');
            Mini.canvas = c;
            Mini.ctx = c.getContext('2d');
            Mini.width = c.width || Mini.width;
            Mini.height = c.height || Mini.height;
        }

        if (Mini.ctx) {
            Mini.ctx.fillStyle = Mini.fillStyle;
            Mini.ctx.strokeStyle = Mini.strokeStyle;
            Mini.ctx.lineWidth = 1;
        }

        // Event listeners per mouse, tastiera e touch... (come prima)
        Mini.canvas.addEventListener('mousemove', (ev) => {
            const rect = Mini.canvas.getBoundingClientRect();
            Mini._mouseX = Math.round((ev.clientX - rect.left) * (Mini.canvas.width / rect.width));
            Mini._mouseY = Math.round((ev.clientY - rect.top) * (Mini.canvas.height / rect.height));
        });

        Mini.canvas.addEventListener('mousedown', () => (Mini._mousePressed = true));
        Mini.canvas.addEventListener('mouseup', () => (Mini._mousePressed = false));
        Mini.canvas.addEventListener('mouseleave', () => (Mini._mousePressed = false));

        window.addEventListener('keydown', (ev) => {
            getKeyMapping(ev).forEach(key => {
                Mini._keysDown[key] = true;
            });
            if (typeof keyPressed === 'function') keyPressed(ev); // NUOVO: Hook per keyPressed()
        });

        window.addEventListener('keyup', (ev) => {
            getKeyMapping(ev).forEach(key => {
                delete Mini._keysDown[key];
                Mini._keysReleased[key] = true;
            });
            if (typeof keyReleased === 'function') keyReleased(ev); // NUOVO: Hook per keyReleased()
        });

        Mini.canvas.addEventListener('click', (ev) => {
            if (typeof mouseClicked === 'function') mouseClicked(ev); // NUOVO: Hook per mouseClicked()
        });

        // Touch support... (come prima)
        Mini.canvas.addEventListener('touchstart', (ev) => {
            ev.preventDefault();
            const touch = ev.touches[0];
            const rect = Mini.canvas.getBoundingClientRect();
            Mini._mouseX = Math.round((touch.clientX - rect.left) * (Mini.canvas.width / rect.width));
            Mini._mouseY = Math.round((touch.clientY - rect.top) * (Mini.canvas.height / rect.height));
            Mini._mousePressed = true;
        });

        Mini.canvas.addEventListener('touchmove', (ev) => {
            ev.preventDefault();
            const touch = ev.touches[0];
            const rect = Mini.canvas.getBoundingClientRect();
            Mini._mouseX = Math.round((touch.clientX - rect.left) * (Mini.canvas.width / rect.width));
            Mini._mouseY = Math.round((touch.clientY - rect.top) * (Mini.canvas.height / rect.height));
        });

        Mini.canvas.addEventListener('touchend', (ev) => {
            ev.preventDefault();
            Mini._mousePressed = false;
        });

        try {
            if (typeof setup === 'function') {
                setup();
                _checkAllSpritesLoaded();
            } else {
                _checkAllSpritesLoaded();
            }
        } catch (e) {
            console.error('Errore in setup():', e);
            return;
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        setTimeout(init, 0);
    }

    window._MiniLib = {
        _internal: Mini,
        stop: () => (Mini._running = false),
        start: () => {
            if (!Mini._running) {
                Mini._running = true;
                Mini._lastFrameTime = 0;
                requestAnimationFrame(_loopStep);
            }
        },
        reset: () => {
            Mini._keysDown = {};
            Mini._keysReleased = {};
            Mini._mousePressed = false;
            Mini._mouseWasPressed = false;
            Mini._draggedObject = null;
        }
    };
})();