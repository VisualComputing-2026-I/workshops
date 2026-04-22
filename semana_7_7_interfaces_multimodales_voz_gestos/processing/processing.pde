import oscP5.*;
import netP5.*;

OscP5 oscP5;

final int OSC_PORT = 12000;

String currentShape = "circulo";
String lastCommand = "Esperando comandos OSC...";
boolean animationEnabled = true;

int objectColor;
float rotationAngle = 0;
float pulsePhase = 0;

void settings() {
  size(960, 540);   
}

void setup() {
  surface.setTitle("Visualizador OSC con Processing");
  oscP5 = new OscP5(this, OSC_PORT);
  objectColor = color(52, 152, 219);
  textAlign(LEFT, TOP);
  ellipseMode(CENTER);
  rectMode(CENTER);
}

void draw() {
  drawBackground();

  pushMatrix();
  translate(width * 0.5, height * 0.55);

  if (animationEnabled) {
    rotationAngle += 0.02;
    pulsePhase += 0.05;
    rotate(rotationAngle);
  }

  float baseSize = 140;
  float animatedSize = animationEnabled ? baseSize + sin(pulsePhase) * 30 : baseSize;
  drawShape(currentShape, animatedSize);
  popMatrix();

  drawHud();
}

void drawBackground() {
  background(16, 18, 28);

  noStroke();
  for (int i = 0; i < 16; i++) {
    float x = map(i, 0, 15, 0, width);
    float wave = animationEnabled ? sin(frameCount * 0.02 + i * 0.35) * 24 : 0;
    fill(30 + i * 4, 38 + i * 2, 56 + i, 70);
    ellipse(x, height * 0.25 + wave, 180, 180);
  }
}

void drawShape(String shapeName, float sizeValue) {
  fill(objectColor);
  stroke(255, 40);
  strokeWeight(2);

  if (shapeName.equals("cuadrado")) {
    rect(0, 0, sizeValue, sizeValue, 18);
    return;
  }

  if (shapeName.equals("triangulo")) {
    float h = sizeValue * 0.9;
    triangle(0, -h * 0.65, -sizeValue * 0.58, h * 0.35, sizeValue * 0.58, h * 0.35);
    return;
  }

  if (shapeName.equals("estrella")) {
    drawStar(0, 0, sizeValue * 0.33, sizeValue * 0.72, 5);
    return;
  }

  ellipse(0, 0, sizeValue, sizeValue);
}

void drawStar(float x, float y, float innerRadius, float outerRadius, int points) {
  float angleStep = TWO_PI / points;
  float halfStep = angleStep * 0.5;

  beginShape();
  for (float angle = -HALF_PI; angle < TWO_PI - HALF_PI; angle += angleStep) {
    vertex(x + cos(angle) * outerRadius, y + sin(angle) * outerRadius);
    vertex(x + cos(angle + halfStep) * innerRadius, y + sin(angle + halfStep) * innerRadius);
  }
  endShape(CLOSE);
}

void drawHud() {
  fill(255);
  textSize(26);
  text("Visualizador OSC", 28, 24);

  fill(200);
  textSize(15);
  text("Puerto: " + OSC_PORT, 28, 62);
  text("Forma: " + currentShape, 28, 84);
  text("Animacion: " + (animationEnabled ? "activa" : "detenida"), 28, 106);

  fill(255, 220);
  textSize(18);
  text("Ultimo comando:", 28, height - 92);

  fill(255);
  textSize(24);
  text(lastCommand, 28, height - 62);

  fill(red(objectColor), green(objectColor), blue(objectColor));
  rect(width - 64, 56, 52, 52, 10);
}

void oscEvent(OscMessage message) {
  String address = message.addrPattern();
  String rawValue = extractStringArgument(message);
  String normalizedValue = normalizeToken(rawValue);

  if (address.equals("/color")) {
    applyColor(normalizedValue);
    lastCommand = "/color " + rawValue;
    return;
  }

  if (address.equals("/shape")) {
    applyShape(normalizedValue);
    lastCommand = "/shape " + rawValue;
    return;
  }

  if (address.equals("/anim")) {
    applyAnimation(normalizedValue);
    lastCommand = "/anim " + rawValue;
    return;
  }

  if (address.equals("/text")) {
    lastCommand = "/text " + rawValue;
    return;
  }

  lastCommand = "Comando desconocido: " + address;
}

String extractStringArgument(OscMessage message) {
  String typeTag = message.typetag();

  if (typeTag == null || typeTag.length() == 0) {
    return "";
  }

  char firstType = typeTag.charAt(0);

  if (firstType == 's') {
    return trim(message.get(0).stringValue());
  }

  if (firstType == 'i') {
    return str(message.get(0).intValue());
  }

  if (firstType == 'f') {
    return str(message.get(0).floatValue());
  }

  return "";
}

String normalizeToken(String value) {
  return trim(value.toLowerCase());
}

void applyColor(String colorName) {
  if (colorName.equals("rojo")) {
    objectColor = color(231, 76, 60);
  } else if (colorName.equals("verde")) {
    objectColor = color(46, 204, 113);
  } else if (colorName.equals("azul")) {
    objectColor = color(52, 152, 219);
  } else if (colorName.equals("amarillo")) {
    objectColor = color(241, 196, 15);
  } else if (colorName.equals("naranja")) {
    objectColor = color(230, 126, 34);
  } else if (colorName.equals("morado")) {
    objectColor = color(155, 89, 182);
  } else if (colorName.equals("rosa")) {
    objectColor = color(232, 67, 147);
  } else if (colorName.equals("cian")) {
    objectColor = color(0, 206, 201);
  } else if (colorName.equals("blanco")) {
    objectColor = color(236, 240, 241);
  } else if (colorName.equals("negro")) {
    objectColor = color(30, 30, 30);
  }
}

void applyShape(String shapeName) {
  if (shapeName.equals("circulo") || shapeName.equals("cuadrado") || shapeName.equals("triangulo") || shapeName.equals("estrella")) {
    currentShape = shapeName;
  }
}

void applyAnimation(String action) {
  if (action.equals("start") || action.equals("iniciar") || action.equals("on")) {
    animationEnabled = true;
    return;
  }

  if (action.equals("stop") || action.equals("detener") || action.equals("off")) {
    animationEnabled = false;
    return;
  }

  if (action.equals("toggle")) {
    animationEnabled = !animationEnabled;
  }
}
