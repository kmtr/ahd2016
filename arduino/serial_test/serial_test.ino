#define LED_PIN 13
#define BUF_MAX 32

void recvStr(char *buf){
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
  buf[i] = '\0';  // \0: end of string
}

void setup() {
  // put your setup code here, to run once:
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  Serial.begin(9600);
}

void loop() {
  char str[255];
  if (Serial.available()) {
    recvStr(str);
    int m0, m1, m2;
    sscanf(str, "%d:%d:%d", &m0, &m1, &m2);
    Serial.println("//----");
    Serial.print("m0: ");
    Serial.println(m0);
    Serial.print("m1: ");
    Serial.println(m1);
    Serial.print("m2: ");
    Serial.println(m2);
    Serial.println("----//");
    if(m0 > 0) {
      digitalWrite(LED_PIN, HIGH);
    } else if(m0 < 0) {
      digitalWrite(LED_PIN, LOW);
    }
  }
}