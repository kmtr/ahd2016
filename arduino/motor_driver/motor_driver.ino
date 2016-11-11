#define MOTOR0_INAPIN 2
#define MOTOR0_INBPIN 3
#define MOTOR0_CTRPIN 4

#define MOTOR1_INAPIN 5
#define MOTOR1_INBPIN 6
#define MOTOR1_CTRPIN 7

#define MOTOR2_INAPIN 8
#define MOTOR2_INBPIN 9
#define MOTOR2_CTRPIN 10

#define LED_PIN 13

#define STEP_ANGLE 7.5 // 7.5 degree
#define STEP_FOR_360 360.0 / STEP_ANGLE

byte val;

void setup() {
  pinMode(MOTOR0_INAPIN, OUTPUT);
  pinMode(MOTOR0_INBPIN, OUTPUT);
  pinMode(MOTOR0_CTRPIN, OUTPUT);

  pinMode(MOTOR1_INAPIN, OUTPUT);
  pinMode(MOTOR1_INBPIN, OUTPUT);
  pinMode(MOTOR1_CTRPIN, OUTPUT);

  pinMode(MOTOR2_INAPIN, OUTPUT);
  pinMode(MOTOR2_INBPIN, OUTPUT);
  pinMode(MOTOR2_CTRPIN, OUTPUT);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(9600);
}

void loop() {
  if(Serial.available() > 0){
    val = Serial.read();
    Serial.write(val);
    if(val == 'A'){
      digitalWrite(LED_PIN, HIGH);
    }

    if(val == 'B'){
      digitalWrite(LED_PIN, LOW);
    }
  }
}
