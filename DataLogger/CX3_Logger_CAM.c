/*
	Daniel Velazquez
	Feb 2017
	Smart ForTwo Tachometer-mod now with data from the CAN Bus
	
	Dec 2018
	Retaken this project for Mazda CX3, to read and log Speed and Steering Wheel position
*/

#include <time.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <libgen.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>		// For File Operations
#include <errno.h>
#include <sys/uio.h>
#include <linux/can.h>
#include <net/if.h>

#include <opencv/cv.h>
#include <opencv/highgui.h>

extern int optind, opterr, optopt;
#define PF_CAN 29
static int skt = -1;
static int running = 1;

int Log;
char FileName[70];
char temp[70];
char tempPicName[70];
char PictureName[70];		//Same as Log File Name + consecutive numbers
IplImage * Picture;


void print_usage(char *prg){
	fprintf(stderr, "Usage: %s [can-interface]\n", prg);
}

void sigterm(int signo){
	printf("got signal %d\n", signo);
	running = 0;
}

int main (int argc, char **argv){
	FILE * fp;
	strcat(FileName,"logs/CX3_");
		
	time_t t;
	time(&t);
	strcat(FileName,ctime(&t));		// This appends a new line at the end
	
	int k=0; int l=0;
	
	for(k=0;k<strlen(FileName)-1;k++){
      temp[l++]=FileName[k];		// this removes the extra line
	}
	strcat(temp, ".csv");
	
	/* open the file for writing*/
	Log = open(temp, O_RDWR | O_CREAT, -1);  // This is the file name I want
	close(Log);
	
	/* the CAN Part first */
	int family = PF_CAN, type = SOCK_RAW, proto = CAN_RAW;
	int opt;
	struct sockaddr_can addr;
	struct ifreq ifr;
	struct can_frame frame;
	int nbytes, i;
	int verbose = 0;

	signal(SIGTERM, sigterm);
	signal(SIGHUP, sigterm);
	if (optind == argc) {
		print_usage(basename(argv[0]));
		exit(0);
	}
	//printf("interface = %s, family = PF_CAN, type = SOCK_RAW, proto = CAN_RAW\n", argv[optind]);

	if ((skt = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0) {
		perror("socket");
		return 1;
	}

	addr.can_family = family;
	strcpy(ifr.ifr_name, argv[optind]);
	ioctl(skt, SIOCGIFINDEX, &ifr);
	addr.can_ifindex = ifr.ifr_ifindex;

	if (bind(skt, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
		perror("bind");
		return 1;
	}

	float Speed;
	float SteeringWheel;
	

	int j=0;
	int m=0;
	char PicSequence;

	fp = fopen (temp,"w");
	/* The camera capture */
	CvCapture * capture =0;
	capture = cvCaptureFromCAM(0); // the parameter for a cam

	while (running) {
		for(j=0;j<=100;j=j+1){
			if ((nbytes = read(skt, &frame, sizeof(frame))) < 0) {
				perror("read");
				return 1;
			}
			/* Speed */
			if(frame.can_id==0x202){	// 23A for Smart, 202 for CX3
				Speed=((frame.data[2]<<8)|frame.data[3]);
				Speed=Speed;
			}
			/* Steering Wheel */
			if(frame.can_id==0x86){
				SteeringWheel=((frame.data[0]<<8)|frame.data[1]);
				SteeringWheel=SteeringWheel;
			}
			Picture = cvQueryFrame( capture );
			m++;
			l=0;
			strcpy(PictureName,FileName);

			for(k=0;k<strlen(PictureName)-5;k++){
				tempPicName[l++]=PictureName[k];		// this removes the extra line
			}
			sprintf(PictureName,"%s_%d%s",tempPicName,m,".jpg");

			cvSaveImage(PictureName, Picture,0);

			printf("Speed: %f\t\t",Speed);
			printf("SteeringWheel: %f\t",SteeringWheel);
			printf("PicName: %s\n",PictureName);

			fprintf(fp,"%f,", Speed);
			fprintf(fp,"%f,", SteeringWheel);
			fprintf(fp,"%s\n", PictureName);
		//	sleep(1);

		}
	}
   
   //readkey();
   fclose(fp);
   return 0;
}

	
