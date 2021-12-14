// Manipulation des ports
// PIND :  RX TX 2 3 4 5 6 7
// https://www.arduino.cc/en/Reference/PortManipulation
// https://www.pololu.com/product/2824

#include <PID_v1.h>  // Pour le PID
#include <TimerOne.h> // Pour le timer

#define ENCODEURA 2
#define ENCODEURB 4
#define A 5       // Contrôle vitesse moteur 1
#define B 7       //controle direction moteur 1
#define C 8       //controle direction moteur 1
const int potentiometerInPin = A1;// pour les valeurs analogue du potentiometre
int potentiometerValue = 0;

double Setpoint, Input, Output;

double Kp = 0.8, Ki = 10, Kd = 0.1;

PID PID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

// volatile => pour toute variable qui sera utilise dans les interruptions

volatile int count = 0; // comptage de tick d'encoder qui sera incrémenté
//sur interruption " On change " sur l'interruption 1
volatile double speedM = 0; // vitesse du moteur

volatile unsigned long time0 = 0; // stock un temps à un instant donné
volatile unsigned long timer = 0; // variable qui va contenir le derniers temps enregistré via millis
volatile byte laststate = 0; // etat précédent de l'encodeur

double valueAcc;
unsigned long timeAcc = 0;

volatile int commande = 0; // consigne pour le moteur

int valeur;  //lecture de la consigne via le moniteur serie

boolean RUN = false;

int mode = 1;
int freq = 1000;
int tacq = 5000;
int cmdM = 10;

void setup()
{

  //initialisation moniteur serie
  Serial.begin(115200);       // facultatif uniquement pour feedback
  while (!RUN) {
    if (Serial.available() >= 0 ) {
      String a = Serial.readString();
      if (a.substring(0, 5).equals("Mode ")) {
        //Serial.println("fait mode");
        mode = a.substring(5, a.length()).toInt();
        Serial.println(a);
      }
      if (a.substring(0, 5).equals("freq ")) {
        //Serial.println("fait mode");
        freq = a.substring(5, a.length()).toInt();
        Serial.println(a);
      }
      if (a.substring(0, 5).equals("tacq ")) {
        //Serial.println("fait mode");
        tacq = a.substring(5, a.length()).toInt();
        Serial.println(a);
      }
      if (a.substring(0, 5).equals("cmdM ")) {
        //Serial.println("fait mode");
        cmdM = a.substring(5, a.length()).toInt();
        Serial.println(a);
      }
      if (a.substring(0, a.length()).equals("RUN")) {
        Serial.println("fait mode");
        RUN = true;
        Serial.println(a);
      }
    }
  }
  Serial.println("test1");

  // on initialise les entrées et sorties
  pinMode(ENCODEURA, INPUT_PULLUP);
  pinMode(ENCODEURB, INPUT_PULLUP);

  pinMode(A, OUTPUT);
  pinMode(B, OUTPUT);
  pinMode(C, OUTPUT);
  // +> moteurs à l'arret

  pinMode(potentiometerInPin, INPUT);

  cli();//stop interrupts

  //set timer1 interrupt at 16Hz
  TCCR1A = 0;// set entire TCCR1A register to 0
  TCCR1B = 0;// same for TCCR1B
  TCNT1  = 0;//initialize counter value to 0
  // set compare match register for 10hz increments
  OCR1A = 1562;// = (16*10^6) / (10*1024) - 1 (must be <65536)
  // turn on CTC mode
  TCCR1B |= (1 << WGM12);
  // Set CS12 and CS10 bits for 1024 prescaler
  TCCR1B |= (1 << CS12) | (1 << CS10);
  // enable timer compare interrupt
  TIMSK1 |= (1 << OCIE1A);

  TCCR2A = 0;// set entire TCCR2A register to 0
  TCCR2B = 0;// same for TCCR2B
  TCNT2  = 0;//initialize counter value to 0
  // set compare match register for 8khz increments
  OCR2A = 249;// = (16*10^6) / (1000*64) - 1 (must be <256)
  // turn on CTC mode
  TCCR2A |= (1 << WGM21);
  // Set CS21 bit for 8 prescaler
  TCCR2B |= (1 << CS21) | (1 << CS20);
  // enable timer compare interrupt
  TIMSK2 |= (1 << OCIE2A);

  sei();//allow interrupts

  // Encoder quadrature counter
  attachInterrupt(digitalPinToInterrupt(2), counter, RISING);

  // PID
  Input = 0;
  Setpoint = 0;
  //active le PID
  PID.SetMode(AUTOMATIC);
  PID.SetOutputLimits(0, 255);
}

ISR(TIMER1_COMPA_vect) { //timer1 interrupt 10Hz
  speedM = count / 16;
  count = 0;
}
ISR(TIMER2_COMPA_vect) { //timer0 interrupt 1kHz
  valueAcc = analogRead(A0);
  timeAcc += 1;
}

void loop() {
  if (mode == 0) {
    Serial.print(0);
    Serial.print(",");
    Serial.print(0);
    Serial.print(",");
    Serial.print(0);
    Serial.print("    ,    ");
    Serial.print(valueAcc);
    Serial.print(",");
    Serial.println(timeAcc);
  }
  if (mode == 1) {
    // setting command with potentiometer
    potentiometerValue = analogRead(potentiometerInPin);//  lire les valeurs donner par potentiometre
    commande = map(potentiometerValue, 0, 1023, 0, 16);// Mappé les valeurs de potentiometre en Rpm
    int testCommande = map(potentiometerValue, 0, 1023, 0, 255);

    Setpoint = commande;
    Input = speedM;
    PID.Compute();
    int output = (int)Output;

    Serial.print(commande);
    Serial.print(",");
    Serial.print(output);
    Serial.print(",");
    Serial.print(speedM);
    Serial.print("    ,    ");
    Serial.print(valueAcc);
    Serial.print(",");
    Serial.println(timeAcc);

    //utilisation de la sortie du PID pour asservir les moteurs
    if (output >= 0) {
      advance(output);
    }
    if (output < 0) {
      back_off(abs(output));
    }
  } else {
    stopMotor();
  }
}


void advance(int a) // En avant
{
  analogWrite (A, a); // Contrôle de vitesse en PWM
  digitalWrite(B, LOW);
  digitalWrite(C, HIGH);
}

void back_off (int a) // En arrière
{
  analogWrite (A, a);
  digitalWrite(B, HIGH);
  digitalWrite(C, LOW);
}

void stopMotor() // En avant
{
  analogWrite (A, 0); // Contrôle de vitesse en PWM
  digitalWrite(B, LOW);
  digitalWrite(C, LOW);
}

// Encoder counter 0

void counter()
{
  //Serial.println(count);
  count++;
}


// Timer pour calculer la vitesse grace aux encodeurs

void timerIsr()
{
  speedM = count / 16;
  count = 0;
}
