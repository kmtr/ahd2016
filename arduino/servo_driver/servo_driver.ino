#include <Servo.h>

#define LEFT 0
#define RIGHT 1
#define NUM_OF_ARMS_PER_SIDE 4
#define LEFT_ZERO_PORT 4
#define RIGHT_ZERO_PORT LEFT_ZERO_PORT + 4
#define WAIT_MILLIS 500
#define LED_PIN 13
#define SERIAL_BAUDRATE 57600

Servo servo[2][NUM_OF_ARMS_PER_SIDE];
unsigned long servo_busy[2][NUM_OF_ARMS_PER_SIDE];

void recvStr() {
  if (Serial.available() > 0) {
    String str = Serial.readString();
    Serial.print(str);
    int cmd[] = {-1, 0, 0};
    parseCommand(str, cmd);
    if (cmd[0] != -1) {
      moveArm(cmd[0], cmd[1], cmd[2]);
    }
  }
}

// led command
//  lOFF(0)|ON(1)\n
// move command
//  LEFT(0)|RIGHT(1);index;move\n
void parseCommand(String str, int *cmd) {
  int buffer_len = str.length() + 1;
  char buffer[buffer_len];
  str.toCharArray(buffer, buffer_len);

  if (buffer[0] == 'l') {
    if (buffer[1] == '0') {
      digitalWrite(LED_PIN, LOW);
    } else {
      digitalWrite(LED_PIN, HIGH);
    }
    return;
  }
  sscanf(buffer, "%d;%d;%d", &cmd[0], &cmd[1], &cmd[2]);
}

void moveArm(int side, int idx, int move) {
  unsigned long current = millis();
  if (current - servo_busy[side][idx] < WAIT_MILLIS) {
    return;
  }
  servo_busy[side][idx] = true;
  if (move < 0) {
    move = 0;
  } else if (move > 180) {
    move = 180;
  }
  servo[side][idx].write(move);
  servo_busy[side][idx] = current;
}

void setup() {
  pinMode(LED_PIN, OUTPUT);
  delay(WAIT_MILLIS + 10);
  // setup left arms
  for (int i = 0; i < NUM_OF_ARMS_PER_SIDE; i++) {
    servo_busy[0][i] = 0;
    servo[0][i].attach(LEFT_ZERO_PORT + i);
    moveArm(0, i, 0);
  }
  // setup right arms
  for (int i = 0; i < NUM_OF_ARMS_PER_SIDE; i++) {
    servo_busy[0][i] = 0;
    servo[1][i].attach(RIGHT_ZERO_PORT + i);
    moveArm(1, i, 0);
  }
  digitalWrite(LED_PIN, HIGH);
  Serial.begin(SERIAL_BAUDRATE);
  Serial.write("start");
}

void loop() {
  if (Serial.available() > 0) {
    recvStr();
  }
}
