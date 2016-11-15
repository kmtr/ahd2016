#define MOTOR_CTRPIN 2

#define MOTOR0 0
#define MOTOR0_A 3
#define MOTOR0_B 4

#define MOTOR1 1
#define MOTOR1_A 5
#define MOTOR1_B 6

#define MOTOR2 2
#define MOTOR2_A 7
#define MOTOR2_B 8

#define MOTOR3 3
#define MOTOR3_A 9
#define MOTOR3_B 10

#define MOTOR4 4
#define MOTOR4_A 11
#define MOTOR4_B 12

#define LED_PIN 13

#define STEP_ANGLE 7.5 // 7.5 degree
#define STEP_FOR_360 360.0 / STEP_ANGLE

#define PulseWidth 10.0

int mIndexes[] = {0, 0, 0, 0, 0};

struct OUTPUT_PIN_MAP {
  int A;
  int B;
};

struct OUTPUT_PIN_MAP opMap[4] = {
    HIGH, HIGH, //
    LOW,  HIGH, //
    LOW,  LOW,  //
    HIGH, LOW   //
};

void step(int mIndex, int s) {
  if (s == 0) {
    return;
  }

  int count;

  if (s >= 0) {
    count = s;
  } else {
    count = s * -1;
  }

  for (int i = 0; i < count; i++) {
    if (s >= 0) {
      mIndexes[mIndex] = mIndexes[mIndex] + 1;
      if (mIndexes[mIndex] > 3) {
        mIndexes[mIndex] = 0;
      }
    } else {
      mIndexes[mIndex] = mIndexes[mIndex] - 1;
      if (mIndexes[mIndex] < 0) {
        mIndexes[mIndex] = 3;
      }
    }

    switch (mIndex) {
    case 0:
      digitalWrite(MOTOR0_A, opMap[mIndexes[mIndex]].A);
      digitalWrite(MOTOR0_B, opMap[mIndexes[mIndex]].B);
      break;
    case 1:
      digitalWrite(MOTOR1_A, opMap[mIndexes[mIndex]].A);
      digitalWrite(MOTOR1_B, opMap[mIndexes[mIndex]].B);
      break;
    case 2:
      digitalWrite(MOTOR2_A, opMap[mIndexes[mIndex]].A);
      digitalWrite(MOTOR2_B, opMap[mIndexes[mIndex]].B);
      break;
    case 3:
      digitalWrite(MOTOR3_A, opMap[mIndexes[mIndex]].A);
      digitalWrite(MOTOR3_B, opMap[mIndexes[mIndex]].B);
      break;
    case 4:
      digitalWrite(MOTOR4_A, opMap[mIndexes[mIndex]].A);
      digitalWrite(MOTOR4_B, opMap[mIndexes[mIndex]].B);
      break;
    }
    delay(PulseWidth);
  }
}

void recvStr(char *buf) {
  int i = 0;
  char c;
  while (1) {
    if (Serial.available()) {
      c = Serial.read();
      buf[i] = c;
      if (c == '\n') {
        break;
      }
      i++;
    }
  }
  buf[i] = '\0'; // \0: end of string
}

// command
// std:  M0;M1;M2;M3;M4;LED\n
//       ex:
//          10;-10;20;30;1\n
void parseCommand(char *str, int *cmd) {
  sscanf(str, "%d;%d;%d;%d;%d;%d", cmd[0], cmd[1], cmd[2], cmd[3], cmd[4]);
}

void setup() {
  pinMode(MOTOR_CTRPIN, OUTPUT);

  pinMode(MOTOR0_A, OUTPUT);
  pinMode(MOTOR0_B, OUTPUT);

  pinMode(MOTOR1_A, OUTPUT);
  pinMode(MOTOR1_B, OUTPUT);

  pinMode(MOTOR2_A, OUTPUT);
  pinMode(MOTOR2_B, OUTPUT);

  pinMode(MOTOR3_A, OUTPUT);
  pinMode(MOTOR3_B, OUTPUT);

  pinMode(MOTOR4_A, OUTPUT);
  pinMode(MOTOR4_B, OUTPUT);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(MOTOR_CTRPIN, LOW);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(9600);
}

void loop() {
  char str[255];
  if (Serial.available() > 0) {
    recvStr(str);
    int cmd[] = {0, 0, 0, 0, 0, 0};
    Serial.write(str);
    parseCommand(str, cmd);

    if (cmd[5] == 1) {
      digitalWrite(LED_PIN, HIGH);
    } else {
      digitalWrite(LED_PIN, LOW);
    }

    digitalWrite(MOTOR_CTRPIN, HIGH);

    step(MOTOR0, cmd[MOTOR0]);
    step(MOTOR1, cmd[MOTOR1]);
    step(MOTOR2, cmd[MOTOR2]);
    step(MOTOR3, cmd[MOTOR3]);
    step(MOTOR4, cmd[MOTOR4]);
  }
}
