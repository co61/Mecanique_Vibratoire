#include <TimerOne.h>
const int zInput = A0;
double valueAcc;
unsigned long timeAcc=0;
void setup() 
{
  pinMode(zInput,INPUT);
  Serial.begin(115200);
  cli();//stop interrupts

//set timer2 interrupt at 1kHz
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
  
  
}
void loop() 
 { 
/*Serial.print(timeAcc);
  Serial.print(",");*/
  Serial.print(valueAcc);
  Serial.print(",");
  Serial.print(800);
  Serial.print(",");
  Serial.println(0);
 } 

ISR(TIMER2_COMPA_vect){//timer0 interrupt 1kHz
  valueAcc = analogRead(A0);
  timeAcc+= 1;
}
