#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <unistd.h>
#include <stdbool.h>
#include <pigpio.h>

#define PULSE 6
#define LED 5
#define OPTO 22

#define TICKS_1 5
#define TICKS_2 7

// #define WAIT_1 20
// #define WAIT_4 100
// #define WAIT_5 130


int state;
int dur;
bool pin;
bool blinking;
bool cambio;

bool module_on;

int mod;
int ticks;

void blink() {
	blinking = true;
	//printf("dur %d state %d %d\n",dur,state,pin);
	if (pin) {
		gpioWrite(LED,0);
		pin = false;
	}
	else {
		gpioWrite(LED,1);
		pin = true;
	}
	return;
}

void reloj() {
	mod = dur % 10;
	if(mod == 0){
		ticks++;
		// printf("TICK %d: dur: %d mod: %d state: %d\n", ticks, dur, mod, state);
		if(!blinking)gpioWrite(LED,0);
	}
	if(mod == 5){
		// printf("TOCK: dur: %d mod: %d state: %d \n", dur, mod, state);
		if(!blinking)gpioWrite(LED,1);
	}
	return;
}
	

void event(int gpio, int level, uint32_t tick){
	///printf("presionado %d 0.00 %d\n", level, tick);
	cambio = false;
	if (level==0) {
		printf("In with state %d\n",state);
		ticks = 0;
		dur = 0;
	}
	else{
		//printf("debounce out with state %d\n",state);
		if (state==0 || state==2) {
			gpioWrite(LED,1);
			pin = true;
		}
		else {
			gpioWrite(LED,0);
			pin = false;
		}
	}
	
}
int main(int argc, char *argv[]) {
	int usecs = 100000;
	int debounce = 20000;

	gpioCfgClock(5, 0, 0); /* Dont use PCM!*/
   	if (gpioInitialise() < 0) {
      		fprintf(stderr, "pigpio initialisation failed\n");
      		return 1;
   	}	

   	/* Set GPIO modes */
   	gpioSetMode(PULSE, PI_INPUT);
   	gpioSetPullUpDown(PULSE, PI_PUD_UP);
   	gpioSetMode(LED, PI_OUTPUT);
   	gpioSetMode(OPTO, PI_OUTPUT);
	gpioSetAlertFunc(PULSE, event);
	gpioGlitchFilter(PULSE, debounce);	


	state = 0;
	//puts("HOLA");
	gpioWrite(LED,1);
	pin = true;
	module_on = false;
	gpioWrite(OPTO,0); // ¿hay que apagar modulo GSM en el init?
	
	/* LOOP */
	while(1) 
	{
	   	usleep(usecs);
		//if (state==2) {
		//	blink();
		//}
		if (gpioRead(PULSE)==0) {
			if(!cambio)reloj();
			if (state==0 && ticks>TICKS_1) {
				blink();
				/* check if module started */
				/* or start service module */
				if (!module_on) {
					gpioWrite(OPTO,1);
					module_on = true;
				}
				if (ticks>TICKS_2) {
					printf("*************** COMENZAMOS A GRABAR!!! ************\n");
					//int rec = system("sudo ./recording.sh &");
					system("systemctl start recording.service");
					system("systemctl show --property MainPID --value recording.service");
					state = 1;
					//setenv("ESTADO", "grabando", 1);
					cambio = true;
					gpioWrite(LED,0);
					pin = false;
					//gpioWrite(OPTO,0); // ¿hay que apagar el modulo GSM al grabar?
					dur = 0;
					ticks = 0;
					blinking = false;
				}
			}
			else if (state==1 && ticks>TICKS_1){
				blink();
				if (ticks>TICKS_2) {
					printf("*************** TERMINAMOS DE GRABAR & POWEROFF ************\n");
					//int stop = system("killall arecord");
					system("killall arecord");
					system("systemctl stop recording.service");
					gpioWrite(LED,0);
					state = 0;
					cambio = true;
					pin = true;
					dur = 0;
					ticks = 0;
					blinking = false;
					system("sleep 3");
					system("poweroff");
				}
			}
			//else if (state==2 && ticks>TICKS_1){
			//	blink();
			//	if (ticks>TICKS_2) {
			//		printf("*************** SHUTDOWN !!!!!!!!!!!! ************\n");
			//		state = 0;
			//		cambio = true;
			//		gpioWrite(LED,0);
			//		pin = false;
			//		dur = 0;
			//		ticks = 0;
			//		blinking = false;
			//		exit(0);
			//	}
			//}
			dur++;
			//printf("dur %d state %d %d\n",dur,state,pin);
		}
	}
   	gpioTerminate();
}
