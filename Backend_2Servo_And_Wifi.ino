#include <ESP8266WiFi.h>
#include <Servo.h>

// Ganti dengan WiFi kamu
const char* ssid = "Fahiraarva";
const char* password = "fairusfitrah";

WiFiServer server(80);

// Motor dan sensor pin
#define PWMA D1
#define PWMB D2
#define DA D3
#define DB D4

#define S1 D6
#define S2 D7   
#define S3 A0
#define S4 D8
#define S5 10

#define SERVO1_PIN D0
#define SERVO2_PIN D5

Servo myServo1;
Servo myServo2;

void setup() {
  Serial.begin(115200);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  int retry = 0;
  while (WiFi.status() != WL_CONNECTED && retry < 20) {
    delay(1000);
    Serial.print(".");
    retry++;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nFailed to connect to WiFi.");
    return;
  }

  Serial.println("\nConnected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.begin();

  // Setup pin
  pinMode(PWMA, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(DA, OUTPUT);
  pinMode(DB, OUTPUT);

  pinMode(S1, INPUT);
  pinMode(S2, INPUT);
  pinMode(S4, INPUT);
  pinMode(S5, INPUT);

  myServo1.attach(SERVO1_PIN);
  myServo1.write(0);

  myServo2.attach(SERVO2_PIN);
  myServo2.write(0);

  stopMotors();
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected");
    String inputString = "";

    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        if (c == '\n') {
          inputString.trim();
          Serial.println("Received: " + inputString);

          if (inputString.startsWith("M:")) {
            int pwm = inputString.substring(2).toInt();
            if (pwm > 0) forward(pwm);
            else stopMotors();
          }
          else if (inputString.startsWith("B:")) {
            int pwm = inputString.substring(2).toInt();
            backward(pwm);
          }
          else if (inputString.startsWith("L:")) {
            int pwm = inputString.substring(2).toInt();
            turnLeft(pwm);
          }
          else if (inputString.startsWith("R:")) {
            int pwm = inputString.substring(2).toInt();
            turnRight(pwm);
          }
          else if (inputString.startsWith("S:")) {
            int angle = inputString.substring(2).toInt();
            myServo1.write(angle);
          }
          else if (inputString.startsWith("T:")) {
            int angle = inputString.substring(2).toInt();
            myServo2.write(angle);
          }

          inputString = "";
        } else {
          inputString += c;
        }
      }

      // Streaming data sensor ke GUI setiap 100ms
      String sensorData = getSensorData();
      client.println(sensorData);
      delay(100);
    }

    client.stop();
    Serial.println("Client disconnected");
  }
}

String getSensorData() {
  int s1 = digitalRead(S1);
  int s2 = digitalRead(S2);
  int s3 = analogRead(S3) > 500 ? 1 : 0;
  int s4 = digitalRead(S4);
  int s5 = digitalRead(S5);

  String data = String(s1) + "," + String(s2) + "," + String(s3) + "," + String(s4) + "," + String(s5);
  Serial.println(data);  // Buat debugging
  return data;
}

// Motor control
void forward(int pwm) {
  digitalWrite(DA, HIGH);
  digitalWrite(DB, HIGH);
  analogWrite(PWMA, pwm);
  analogWrite(PWMB, pwm);
}

void backward(int pwm) {
  digitalWrite(DA, LOW);
  digitalWrite(DB, LOW);
  analogWrite(PWMA, pwm);
  analogWrite(PWMB, pwm);
}

void turnLeft(int pwm) {
  digitalWrite(DA, LOW);
  digitalWrite(DB, HIGH);
  analogWrite(PWMA, pwm);
  analogWrite(PWMB, pwm);
}

void turnRight(int pwm) {
  digitalWrite(DA, HIGH);
  digitalWrite(DB, LOW);
  analogWrite(PWMA, pwm);
  analogWrite(PWMB, pwm);
}

void stopMotors() {
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
}
