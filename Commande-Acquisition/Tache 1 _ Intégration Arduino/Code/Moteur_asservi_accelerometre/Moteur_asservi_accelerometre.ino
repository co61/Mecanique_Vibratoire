// Lien vers les soruces utilisées
// https://www.arduino.cc/en/Reference/PortManipulation
// https://www.pololu.com/product/2824

#include <PID_v1.h>  // Pour le PID  (librairie à télécharger : https://github.com/br3ttb/Arduino-PID-Library/blob/master/PID_v1.h)

#define ENCODEURA 2
#define ENCODEURB 4
#define A 5       // Contrôle vitesse moteur 1
#define B 7       //controle direction moteur 1
#define C 8       //controle direction moteur 1

const int potentiometerInPin = A5;// pour les valeurs analogue du potentiometre
int potentiometerValue = 0;

double Setpoint, Input, Output;

double Kp = 2.0, Ki = 30.0, Kd = 10.0;


PID PID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

// volatile => pour toute variable qui sera utilise dans les interruptions

int count = 0; // comptage de tick d'encoder qui sera incrémenté
//sur interruption " On change " sur l'interruption 1
float speedM = 0; // vitesse du moteur


double valueAcc;
unsigned long timeAcc=0;

float commande = 0; // consigne pour le moteur

int valeur;  //lecture de la consigne via le moniteur serie


void setup()
{

  //initialisation moniteur serie
  Serial.begin(115200);       // facultatif uniquement pour feedback

  // on initialise les entrées et sorties
  pinMode(ENCODEURA, INPUT_PULLUP);
  pinMode(ENCODEURB, INPUT_PULLUP);

  // Pin moteur en output
  pinMode(A, OUTPUT);
  pinMode(B, OUTPUT);
  pinMode(C, OUTPUT);

  //potentiomètre pour réglage vitesse moteur 
  pinMode(potentiometerInPin, INPUT);

  attachInterrupt(digitalPinToInterrupt(2), counter, CHANGE);

  //Réglages des timers 1 et 2 pour fréuence asservissement et échantillonage accéléromètre
  cli();//stop interrupts

  //set timer1 interrupt at 10Hz
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

  // PID
  Input = 0;
  Setpoint = 0;
  //active le PID
  PID.SetMode(AUTOMATIC);
  PID.SetOutputLimits(0, 255);
}

ISR(TIMER1_COMPA_vect){//timer1 interrupt 10Hz, calcul de la vitesse pour l'asservissement
  speedM = (count*10.0)/64.0/30.0;
  count = 0;  
}
ISR(TIMER2_COMPA_vect){//timer0 interrupt 1kH, acquisition de l'accéléromètre 
  valueAcc = analogRead(A0);
  timeAcc+= 1;
}

void loop() {

  // setting command with potentiometer
  potentiometerValue = analogRead(potentiometerInPin);//  lire les valeurs donner par potentiometre
  commande = 2.0;//map(potentiometerValue, 0, 1023, 0, 2.55);// Mappé les valeurs de potentiometre en Rpm
  
  //test affichage pour voir si la vitesse est correctement corrigée
  //int testCommande = map(potentiometerValue, 0, 1023, 0, 255);
  /*if (Serial.available()) {
    commande = Serial.parseInt(); //récupération des caractères sur le port série
    if (valeur != 0) {
      commande = valeur;
    }
    }*/
  //Calcul du PID (par une librairie, voir le code STM32 pour implémenter personnelement l'asservissement)
  Setpoint = commande;
  Input = speedM;
  PID.Compute();
  int output = (int)Output;

  Serial.print(commande*100.0);
  //Serial.print(",");
  //Serial.print(output);
  Serial.print(",");
  Serial.print(speedM*100.0);
  Serial.print(",");
  Serial.print(valueAcc);
  Serial.print(",");
  Serial.print(800);
  Serial.print(",");
  Serial.println(0);
  //Serial.print(",");
  //Serial.println(timeAcc);
  
  //utilisation de la sortie du PID pour asservir les moteurs
  if (output >= 0) {
    advance(output);
  }
  if (output < 0) {
    back_off(abs(output));
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

// Encoder counter 0 at up front and down front
void counter()
{
  count++;
}
