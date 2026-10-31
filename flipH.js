let em1;
let em2;
let btn1, btn2;
function setup() {
  createMiniCanvas(640, 480);
  em1 = new eSprite('🐈', 120,120,64,64);
  em2 = new eSprite('✏️', 380,120,64,64);
  textAlign('center');
  btn1 = new Button(width/2-180, height/2,100,40, 'Flip!');
  btn2 = new Button(width/2+50, height/2,100,40, 'Reset!');
}

function draw() {
  background(120,10,45);
  em1.draw();
  em2.draw();
  btn1.draw();
  btn2.draw();

  if(btn1.isClicked()){
    em1.flip(true);
    em2.flipV(true);
  }
  if(btn2.isClicked()){
    em1.flip(false);
    em2.flipV(false);
  }
}