#include <math.h> // biblioteka za matematicke operacije
#include "Wire.h" // biblioteka za AD/DA konvertor
#define PCF8591 (0x90 >> 1) // I2C bus address

long expo;     // ekspozicija
long n;        // broj faza
long alfa;     // ugao rotacije
float d = 37.8;  // konstanta resetke u mikronima ------

String s;
String s1;  // ekspozicija
String s2;  // broj faza
String s3;  // broj ekspozicija za snimanje test slike
String s4; // odabir motora kod pojedinacne rotacije motora 
String s5; // odabir smera kod pojedinacne rotacije motora
String s6; // odabir stepova kod pojedinacne rotacije motora
String s7; // DA konverzija za kontrolu snage laserske diode


long nstep = 800;    // broj stepova za punu rotaciju osovine motora -----
long cirlin = 500;   // linarna putanja u mirkonima za jednu rotaciju osovine motora -----


long pm = 3;         // faktor prenosnog mehanizma (1:3)
long stepercounter;  // brojac stepova tokom rotacije motora
float laststep;      // broj stepova tako da resetka bude pod uglom od 22.5 stepena
float corrposition;  // broj stepova tako da se resetka vrati u pocetni polozaj za novi mod rada
int motor; // promenljiva za izbor motora kod pojedinacne rotacije motora 
int direction; // promenljiva za izbor motora kod pojedinacne rotacije motora
int step; //promenljiva za broj stepova rotacije kod pojedinacne rotacije motora

float correct45[] = { 1.0823922, 2.61312593, 1.0823922, 2.61312593 };  //korekcioni faktor koji je posledica rotacije resetke pri uglu rotacije od 60 stepeni to su sinusi od 22.5 i sinusi od 67.5 stepeni pa na minus prvi kao korekcioni faktori
float correct60[] = { 1, 2, 2 }; //korekcioni faktor koji je posledica rotacije resetke pri uglu od 60 stepeni

float phase1[] = { 0 };
float phase3[] = { 11, 11 }; //broj stepova za koji treba da se pomeri resetka od 37um da bi mogli da snimimo 3 slike sa razlicitim fazama (period resetke je 32,31 step), faza se pomera dva puta a snima 3 slike
float phase6[] = { 5, 5, 5, 5, 5 }; //broj stepova za koji treba da se pomeri resetka od 37um da bi mogli da snimo 6 slika sa razlicitim fazama (period resetke je 32,31 step), faza se pomera 5 puta a snima 6 slika 


char Enumstep1[10]; // liste unosa iz serijske komunikacije
char Enumstep2[10];
char Enumstep3[10];
char Enumstep4[10];
char Enumstep5[10];
char Enumstep6[10];
char Enumstep7[10];

int ad; // promenljiva se odnosi se na DA konverziju 

const int stepPin1 = 10;  // prvi motor
const int dirPin1 = 11;   // prvi motor smer

const int stepPin2 = 12;  // drugi motor
const int dirPin2 = 13;   // drugi motor smer

int dellaser = 540;  //kasnjenje lasera u odnosu na triger signal

int delcam = 10;  //kasnjenje pocetka snimanja kamere u odnosu na triger signal

int ncam = 80;  //koeficijen pravca sa grafika zavisnosti trajanja snimanja slike u odnosu na ekspoziciju #nije koeficijent pravca nego odsecak

int nlas = 450;  //koeficijen pravca sa grafika zavisnosti trajanja impulsa lasera u odnosu na trajanje triger signala koji se salje laseru #nije koeficijent pravca nego odsecak

int k = 20;  //korekcioni faktor koji regulise pomeranje pocetka snimanja slike u odnosu na triger singal a ujedno utice i na duzinu trajanja laserskog impulsa

unsigned int t1 = dellaser - delcam + k;  //regulise trigere

unsigned int t2 = ncam + nlas - dellaser + delcam;  //regulise trigere


const int ledPin = 7; // pin lasera
const int trigCam = 3;  // pin kamere

void setup() {
  // put your setup code here, to run once:

  Serial.begin(9600); // serijska komunikacija
  Wire.begin(); // AD/DA konvertor

  pinMode(stepPin1, OUTPUT); // izlaz za broj stepova motora 1
  pinMode(dirPin1, OUTPUT); // izlaz za smer motora 1
  digitalWrite(dirPin1, HIGH); // inicijalno stanje smera motora 1

  pinMode(stepPin2, OUTPUT); // izlaz za broj stepova motora 2
  pinMode(dirPin2, OUTPUT); // izlaz za smer motora 2
  digitalWrite(dirPin2, HIGH); // inicijalno stanje smera motora 2

  pinMode(ledPin, OUTPUT); // izlaz za ukljucenje i iskljucenje laserske diode
  digitalWrite(ledPin,LOW); // inicijalno postavljeno da je dioda iskljucena

  pinMode(trigCam, OUTPUT); // izlaz zaq triger kamere
  digitalWrite(trigCam, HIGH); //inicijalno postavljeno HIGH zbog toga sto optokapler koji je iza kartce invertuje signale pa kamera vidi 0V
}

void loop() {
  // put your main code here, to run repeatedly:



  while (Serial.available() > 0) {
    // look for the incoming command serial stream:
    s = Serial.readString();

    if (s[0]=='H')  {digitalWrite(ledPin, HIGH); Serial.println("Laser on");} //komanda za ukljucenje laserske diode
    if (s[0]=='L')  {digitalWrite(ledPin, LOW); Serial.println("Laser off");} //komanda za iskljucenje laserske diode
    
    if (s[0] == 'A') {

        s7=s.substring(1,4); 
        strcpy(Enumstep7,&s7[0]);
        ad=atoi(Enumstep7);

        Wire.beginTransmission(PCF8591); // wake up PCF8591
        Wire.write(0x40); // control byte - turn on DAC (binary 1000000)
        Wire.write(ad); // value to send to DAC
        Wire.endTransmission(); // end tranmission
    }


    if (s[0] == 'T') {


      s1 = s.substring(1, 6);  // setuje ekspoziciju slike na osnovu ekspozicije zadate u aplikaciji
      strcpy(Enumstep1, &s1[0]);
      expo = (atoi(Enumstep1));

      if (s[6] == '1') alfa = 60;
      else alfa = 45;  //setuje ugao rotacije resetke resetka moze da rotira za ugao od 120 stepeni ili ugao od

      s2 = s.substring(7, 8);  // setuje broj faza izmedju dve rotacije resetke moze da ima 9 faza (ostavljeno jedno mesto)
      strcpy(Enumstep2, &s2[0]);
      n = atoi(Enumstep2);

      float faza[int((180*(n-1)) / alfa)] = {};  //setuje broj stepova rotacije motora tako da pomeri resetu za datu fazu. ako je broj faza 1 onda snima slike bey pomeranja faze, ako je broj faza 3 onda pomera dva puta fazu izmedju rotacija i tako dalje.   


      
      laststep = 0; //u nastavku se racunaju faze za pomeranje resetke

      int counterfaza=0;

      for (int j = 0; j < (180 / alfa); j++) {
        for (int i = 0; i < (n - 1); i++) {
          
    
          if (alfa == 60) {
            
            if (n == 3){
            //Serial.println(int(counterfaza));
            faza[int(counterfaza)] =round(correct60[j]*phase3[i]); //racuna ukupan broj stepova koji je potrebno pomeriti resetku za datu fazu
            //Serial.println(faza[int(counterfaza)]);; //stampa koji je to broj stepova
            laststep += faza[int(2*j+i)]; //racuna ukupan pomeraj resetke tokom jednog ciklusa kako bi mogli da vratimo resetku u pocetni polozaj
            }
            
            if (n == 6){
            //Serial.println(int(counterfaza));
            //Serial.println(round(correct60[j]*phase6[i]));
            faza[int(counterfaza)] =round(correct60[j]*phase6[i]); 
            //Serial.println(faza[int(counterfaza)]);;
            laststep += faza[int(2*j+i)]; 
            }

            
          }
          if (alfa == 45) {

            if (n == 3){
            //Serial.println(int(counterfaza));
            faza[int(counterfaza)] =round(correct45[j]*phase3[i]); //racuna ukupan broj stepova koji je potrebno pomeriti resetku za datu fazu
            //Serial.println(faza[int(counterfaza)]); //stampa koji je to broj stepova
            laststep += faza[int(2*j+i)]; //racuna ukupan pomeraj resetke tokom jednog ciklusa kako bi mogli da vratimo resetku u pocetni polozaj
            }
            
            if (n == 6){
            //Serial.println(int(counterfaza));
            faza[int(counterfaza)] =round(correct45[j]*phase6[i]); 
            //Serial.println(faza[int(counterfaza)]);
            laststep += faza[int(2*j+i)]; 
            }
            
            
          }
          
        counterfaza+=1;
        }
      }

      
  
      
      
      long stepercounter = pm * alfa * nstep / 360;  // definisemo koliko stepova treba da rotira osovina motora da bi se resetka rotirala za izabran ugao

      if (alfa == 45) {  // postavlja resetku u pocetni polozaj za uzastopne rotacije od 45 stepeni
        corrposition = 22.5 * pm * nstep / 360;
        //Serial.println(corrposition);
        steppermotor(corrposition, stepPin1);
      }

      int brojac= 0;
      for (int i = 1; i < (((360 * n) / alfa) + 1); i++) {
        //Serial.println(i);
        
        if (i % 2 == 1) {
          // ide funkcija laser kamera sada
          trigger(expo); //pokrece trigere kamere i laserske diode za izabranu ekspoziciju ostali parametri su ranije definisani
          


        } else {
          if ((alfa == 60 and (i == (2 * n) or i == (4 * n))) or (alfa == 45 and (i == (2 * n) or i == (4 * n) or i == (6 * n)))) {
            // ide funkcija za rotaciju resetke;
            //Serial.println(stepercounter);
            steppermotor(stepercounter, stepPin1);  //rotiram resetku za izabran broj stepova pozivanje funkcije za rotaciju resetke i pozivanjem motora broj 1 koji rotrira resetku
            



          } else {
            //ovde cemo definisati faze rotacije. i onu poslednju fazu vracanja.
            //Serial.println(brojac);
            //Serial.println(faza[brojac]);
            
            if(i==((360 * n) / alfa) and (n>1)){ //proiverava da li se radi o poslednjoj rotaciji, ako jeste poslednja rotacija, obrne smer motora, okrene za ukupan broj stepova +20, vrati inicijalan smer i vrati u drugu stranu jos 20 stepova
              digitalWrite(dirPin2, LOW);
              steppermotor(laststep, stepPin2);
              steppermotor(20, stepPin2);
              delay(200); // pravi malu pauzu izmedju korekcije i vracanja u normalan smer... ne znam sto sam ovo stavio ali mi se cini da ce bolje da radi zbog inercije.
              digitalWrite(dirPin2, HIGH);
              steppermotor(20, stepPin2);
            }
            Serial.println(brojac);
            
            steppermotor(faza[brojac], stepPin2); //ovde se poziva funkcija za rotaciju drugog motora
            brojac+=1;
            
          }
        }
      }
      if (alfa == 45) {
        corrposition = 22.5 * pm * nstep / 360;  //nakon rotacije motora u rezimu 45 stepeni nas motor treba da se vrati u pocetno stanje tako da sledeca rotacija moze da bude pod uglom od 120 stepeni. Uvek se vraca u pocetni polozja i to uvek u isto smeru rotira da ne bi gubili stepove
        //Serial.println(corrposition);
        steppermotor(corrposition, stepPin1);
      }
      if (alfa == 60) {
        corrposition = 60 * pm * nstep / 360;  //nakon rotacije motora u rezimu 60 stepeni nas motor treba da se vrati u pocetno stanje tako da sledeca rotacija moze da bude pod uglom od 120 stepeni. Uvek se vraca u pocetni polozja i to uvek u isto smeru rotira da ne bi gubili stepove
        //Serial.println(corrposition);
        steppermotor(corrposition, stepPin1);
      }
    }

    if (s[0] == 'C') {
      s1 = s.substring(1, 6);  // setuje ekspoziciju slike na osnovu ekspozicije zadate u aplikaciji
      strcpy(Enumstep3, &s1[0]);
      expo = (atoi(Enumstep3));
      delay(1000);
      trigger(expo);
    }

    if (s[0] == 'N') {
      s1 = s.substring(1, 6);  // setuje ekspoziciju slike na osnovu ekspozicije zadate u aplikaciji
      strcpy(Enumstep3, &s1[0]);
      expo = (atoi(Enumstep3));
      delay(1000);
      digitalWrite(trigCam, LOW);
      delay(300);
      digitalWrite(trigCam, HIGH);
    }

    if (s[0] == 'R') {
      s4 = s.substring(1, 2); // biramo motor koji treba da se rotira 0 prvi motor 1 drugi motor
      strcpy(Enumstep4, &s4[0]);
      motor = atoi(Enumstep4); // vrednost 1 odnosi se na motor 1, vrednost 2 odnosi se na motor 2

      //Serial.println(motor);

      s5= s.substring(2, 3); // biramo smer u kom treba da se rotira
      strcpy(Enumstep5, &s5[0]);
      direction= atoi(Enumstep5); // 0 je normalan smer 1 je suprotan smer 
      
      //Serial.println(direction);

      s6=  s.substring(3, 8); // biramo broj stepova za koji treba da rotira izabrani motor
      strcpy(Enumstep6, &s6[0]);
      step= atoi(Enumstep6);

      //Serial.println(step);

      if(motor==1){ // proverava da li je izabran motor jedan 
        if(direction==0){ // ako jeste oroverava smeri rotira u izabranom smeru za izabran broj stepova
          steppermotor(step, stepPin1);
        }
        else{
          digitalWrite(dirPin1, LOW); // okrecemo smer motora 
          steppermotor(step, stepPin1);
          digitalWrite(dirPin1, HIGH); // cim se zavrsi vracamo inicijalan smer     
        }
      }
      else{ // isto sve ako se izabere motor 2
        if(direction==0){
          steppermotor(step, stepPin2);
        }
        else{
          digitalWrite(dirPin2, LOW); // okrecemo smer motora 
          steppermotor(step, stepPin2);
          digitalWrite(dirPin2, HIGH); // cim se zavrsi vracamo inicijalan smer     
        }
      }

      
      
    }

  }
}

void steppermotor(int x, int y) {  // funkcija koja rotira motore, biramo motor i broj stepova.
  int i = 0;
  int delaytime = 1500;  //ovim se definise brzina rotacije motora 1, ovaj motor rotira resetku
  delay(500);
  while (i < x) {
    //Serial.println(i);
    digitalWrite(y, HIGH);
    delayMicroseconds(delaytime);
    digitalWrite(y, LOW);
    delayMicroseconds(delaytime);
    i++;
    
  }
  delay(500);
}

void trigger(long x) {  // funkcija trigera kamere i laserske diode

  digitalWrite(ledPin, HIGH);
  delay(t1);
  digitalWrite(trigCam, LOW);
  delay(t2 + x);
  digitalWrite(ledPin, LOW);
  digitalWrite(trigCam, HIGH);

}
