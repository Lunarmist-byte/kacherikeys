
/*
  WIREKEYS v1.1
  ESP32 DevKit V1 - Classic ESP32

  8 capacitive touch electrodes
  KY-023 joystick
  Serial communication with Python audio engine

  Joystick:
  UP/DOWN    = Change instrument mode
  LEFT/RIGHT = Pitch transpose
  PRESS      = Sustain toggle
*/

const int touchPins[8] = {
  4, 13, 12, 14, 27, 33, 32, 15
};

const int midiNotes[8] = {
  60, 62, 64, 65, 67, 69, 71, 72
};

// Joystick connections
const int JOY_X = 34;
const int JOY_Y = 35;
const int JOY_SW = 25;

// Touch detection
uint16_t baseline[8];
int threshold[8];
bool keyPressed[8] = {false};

// Instrument state
int currentMode = 0;
int transpose = 0;
bool sustain = false;

// Joystick calibration
int joyXCenter = 2048;
int joyYCenter = 2048;

// Joystick direction handling
bool xArmed = true;
bool yArmed = true;

const int DEADZONE = 700;
const int RELEASE_ZONE = 350;

const int MIN_TRANSPOSE = -24;
const int MAX_TRANSPOSE = 24;

// Button debounce
bool lastButtonReading = HIGH;
bool stableButtonState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long DEBOUNCE_DELAY = 40;

// --------------------------------------------------
// Serial event functions
// --------------------------------------------------

void sendMode() {
  Serial.print("MODE ");
  Serial.println(currentMode);
}

void sendTranspose() {
  Serial.print("TRANSPOSE ");
  Serial.println(transpose);
}

void sendSustain() {
  Serial.print("SUSTAIN ");
  Serial.println(sustain ? 1 : 0);
}

// --------------------------------------------------
// Joystick calibration
// --------------------------------------------------

void calibrateJoystick() {
  long totalX = 0;
  long totalY = 0;

  Serial.println("Calibrating joystick. Keep it centered.");

  for (int i = 0; i < 50; i++) {
    totalX += analogRead(JOY_X);
    totalY += analogRead(JOY_Y);
    delay(10);
  }

  joyXCenter = totalX / 50;
  joyYCenter = totalY / 50;

  Serial.print("Joystick center X: ");
  Serial.println(joyXCenter);

  Serial.print("Joystick center Y: ");
  Serial.println(joyYCenter);
}

// --------------------------------------------------
// Touch calibration
// --------------------------------------------------

void calibrateTouch() {
  unsigned long totals[8] = {0};

  Serial.println("Touch calibration started.");
  Serial.println("Keep all electrodes untouched.");

  for (int sample = 0; sample < 100; sample++) {
    for (int i = 0; i < 8; i++) {
      totals[i] += touchRead(touchPins[i]);
    }

    delay(10);
  }

  for (int i = 0; i < 8; i++) {
    baseline[i] = totals[i] / 100;

    threshold[i] = max(
      8,
      (int)(baseline[i] * 0.18)
    );

    Serial.print("Key ");
    Serial.print(i + 1);
    Serial.print(" baseline: ");
    Serial.println(baseline[i]);
  }

  Serial.println("Touch calibration complete.");
}

// --------------------------------------------------
// Joystick movement
// --------------------------------------------------

void updateJoystick() {

  int x = analogRead(JOY_X);
  int y = analogRead(JOY_Y);

  // LEFT / RIGHT: Pitch control

  if (abs(x - joyXCenter) < RELEASE_ZONE) {
    xArmed = true;
  }

  if (xArmed) {

    if (x < joyXCenter - DEADZONE) {

      transpose--;

      transpose = constrain(
        transpose,
        MIN_TRANSPOSE,
        MAX_TRANSPOSE
      );

      sendTranspose();
      Serial.println("Joystick LEFT");

      xArmed = false;
    }

    else if (x > joyXCenter + DEADZONE) {

      transpose++;

      transpose = constrain(
        transpose,
        MIN_TRANSPOSE,
        MAX_TRANSPOSE
      );

      sendTranspose();
      Serial.println("Joystick RIGHT");

      xArmed = false;
    }
  }

  // UP / DOWN: Instrument selection

  if (abs(y - joyYCenter) < RELEASE_ZONE) {
    yArmed = true;
  }

  if (yArmed) {

    if (y < joyYCenter - DEADZONE) {

      currentMode--;

      if (currentMode < 0) {
        currentMode = 2;
      }

      sendMode();
      Serial.println("Joystick UP");

      yArmed = false;
    }

    else if (y > joyYCenter + DEADZONE) {

      currentMode++;

      if (currentMode > 2) {
        currentMode = 0;
      }

      sendMode();
      Serial.println("Joystick DOWN");

      yArmed = false;
    }
  }
}

// --------------------------------------------------
// Joystick button
// --------------------------------------------------

void updateJoystickButton() {

  bool reading = digitalRead(JOY_SW);

  if (reading != lastButtonReading) {
    lastDebounceTime = millis();
  }

  if (millis() - lastDebounceTime > DEBOUNCE_DELAY) {

    if (reading != stableButtonState) {

      stableButtonState = reading;

      if (stableButtonState == LOW) {

        sustain = !sustain;

        sendSustain();

        Serial.println(
          sustain ? "SUSTAIN ENABLED" : "SUSTAIN DISABLED"
        );
      }
    }
  }

  lastButtonReading = reading;
}

// --------------------------------------------------
// Touch detection
// --------------------------------------------------

void updateTouchKeys() {

  for (int i = 0; i < 8; i++) {

    int value = touchRead(touchPins[i]);

    int difference = (int)baseline[i] - value;

    // Key pressed
    if (!keyPressed[i] && difference > threshold[i]) {

      keyPressed[i] = true;

      int velocity = map(
        difference,
        threshold[i],
        threshold[i] * 3,
        45,
        127
      );

      velocity = constrain(velocity, 1, 127);

      Serial.print("ON ");
      Serial.print(midiNotes[i]);
      Serial.print(" ");
      Serial.println(velocity);
    }

    // Key released
    else if (
      keyPressed[i] &&
      difference < threshold[i] * 0.65
    ) {

      keyPressed[i] = false;

      Serial.print("OFF ");
      Serial.println(midiNotes[i]);
    }
  }
}

// --------------------------------------------------
// Setup
// --------------------------------------------------

void setup() {

  Serial.begin(115200);

  analogReadResolution(12);

  pinMode(JOY_SW, INPUT_PULLUP);

  delay(1000);

  calibrateJoystick();
  calibrateTouch();

  Serial.println();
  Serial.println("WIREKEYS READY");

  sendMode();
  sendTranspose();
  sendSustain();
}

// --------------------------------------------------
// Main loop
// --------------------------------------------------

void loop() {

  updateJoystick();
  updateJoystickButton();
  updateTouchKeys();

  delay(10);
}
