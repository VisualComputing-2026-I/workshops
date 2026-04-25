import oscP5.*;

OscP5 oscP5;

final int OSC_PORT = 12000;

String currentShape = "circle";
String lastSentence = "Waiting for voice command...";

color currentColor;
boolean animationEnabled = true;
boolean spinningEnabled = true;

float rotationAngle = 0.0;
float pulse = 0.0;
float spinSpeed = 0.025;

void settings() {
  size(1024, 576);
}

void setup() {
  surface.setTitle("Local Voice Commands - Processing Receiver");
  surface.setResizable(true);
  oscP5 = new OscP5(this, OSC_PORT);
  currentColor = color(66, 135, 245);

  textAlign(LEFT, TOP);
  rectMode(CENTER);
  ellipseMode(CENTER);
}

void draw() {
  drawBackground();
  drawSceneObject();
  drawHUD();
}

void drawBackground() {
  background(14, 18, 28);

  noStroke();
  for (int i = 0; i < 14; i++) {
    float x = map(i, 0, 13, -30, width + 30);
    float yOffset = sin(frameCount * 0.015 + i * 0.45) * 26;
    fill(30 + i * 5, 36 + i * 4, 48 + i * 3, 70);
    ellipse(x, height * 0.22 + yOffset, 200, 200);
  }
}

void drawSceneObject() {
  float sizeBase = 170;

  if (animationEnabled) {
    pulse += 0.05;
  }

  if (spinningEnabled) {
    rotationAngle += spinSpeed;
  }

  float animatedSize = animationEnabled ? sizeBase + sin(pulse) * 24 : sizeBase;

  pushMatrix();
  translate(width * 0.5, height * 0.56);
  rotate(rotationAngle);

  fill(currentColor);
  stroke(255, 45);
  strokeWeight(2.0);

  if (currentShape.equals("square")) {
    rect(0, 0, animatedSize, animatedSize, 20);
  } else if (currentShape.equals("triangle")) {
    float h = animatedSize * 0.92;
    triangle(0, -h * 0.62, -animatedSize * 0.57, h * 0.36, animatedSize * 0.57, h * 0.36);
  } else if (currentShape.equals("star")) {
    drawStar(0, 0, animatedSize * 0.36, animatedSize * 0.72, 5);
  } else {
    ellipse(0, 0, animatedSize, animatedSize);
  }

  popMatrix();
}

void drawStar(float x, float y, float innerRadius, float outerRadius, int points) {
  float step = TWO_PI / points;
  float half = step * 0.5;

  beginShape();
  for (float a = -HALF_PI; a < TWO_PI - HALF_PI; a += step) {
    vertex(x + cos(a) * outerRadius, y + sin(a) * outerRadius);
    vertex(x + cos(a + half) * innerRadius, y + sin(a + half) * innerRadius);
  }
  endShape(CLOSE);
}

void drawHUD() {
  fill(255);
  textSize(28);
  text("Local Voice Visualizer", 28, 20);

  fill(210);
  textSize(15);
  text("OSC Port: " + OSC_PORT, 28, 62);
  text("Shape: " + currentShape, 28, 84);
  text("Animation: " + (animationEnabled ? "on" : "off"), 28, 106);
  text("Spinning: " + (spinningEnabled ? "on" : "off"), 28, 128);
  text("Spin speed: " + nf(spinSpeed, 1, 3), 28, 150);

  fill(255);
  textSize(17);
  text("Last sentence:", 28, height - 84);
  textSize(22);
  text(lastSentence, 28, height - 58);

  fill(currentColor);
  rect(width - 58, 54, 48, 48, 10);
}

void oscEvent(OscMessage message) {
  String address = message.addrPattern();
  String value = normalize(extractArg(message));

  if (address.equals("/color")) {
    applyColor(value);
    return;
  }

  if (address.equals("/shape")) {
    applyShape(value);
    return;
  }

  if (address.equals("/anim")) {
    applyAnimation(value);
    return;
  }

  if (address.equals("/spin")) {
    if (value.equals("toggle")) {
      spinningEnabled = !spinningEnabled;
    }
    return;
  }

  if (address.equals("/speed")) {
    if (value.equals("up")) {
      spinSpeed = min(spinSpeed + 0.01, 0.12);
    } else if (value.equals("down")) {
      spinSpeed = max(spinSpeed - 0.01, 0.0);
    }
    return;
  }

  if (address.equals("/reset")) {
    if (value.equals("now")) {
      resetState();
    }
    return;
  }

  if (address.equals("/text")) {
    lastSentence = extractArg(message);
  }
}

String extractArg(OscMessage message) {
  String typeTag = message.typetag();
  if (typeTag == null || typeTag.length() == 0) {
    return "";
  }

  char first = typeTag.charAt(0);
  if (first == 's') {
    return trim(message.get(0).stringValue());
  }

  if (first == 'i') {
    return str(message.get(0).intValue());
  }

  if (first == 'f') {
    return str(message.get(0).floatValue());
  }

  return "";
}

String normalize(String value) {
  return trim(value.toLowerCase());
}

void applyColor(String name) {
  if (name.equals("red")) {
    currentColor = color(234, 84, 85);
  } else if (name.equals("green")) {
    currentColor = color(58, 201, 99);
  } else if (name.equals("blue")) {
    currentColor = color(66, 135, 245);
  } else if (name.equals("yellow")) {
    currentColor = color(241, 196, 15);
  } else if (name.equals("orange")) {
    currentColor = color(243, 156, 18);
  } else if (name.equals("purple")) {
    currentColor = color(155, 89, 182);
  } else if (name.equals("white")) {
    currentColor = color(236, 240, 241);
  } else if (name.equals("black")) {
    currentColor = color(35, 35, 35);
  }
}

void applyShape(String shapeName) {
  if (shapeName.equals("circle") || shapeName.equals("square") || shapeName.equals("triangle") || shapeName.equals("star")) {
    currentShape = shapeName;
  }
}

void applyAnimation(String action) {
  if (action.equals("start") || action.equals("on")) {
    animationEnabled = true;
  } else if (action.equals("stop") || action.equals("off")) {
    animationEnabled = false;
  }
}

void resetState() {
  currentShape = "circle";
  currentColor = color(66, 135, 245);
  animationEnabled = true;
  spinningEnabled = true;
  spinSpeed = 0.025;
  lastSentence = "State reset";
}
