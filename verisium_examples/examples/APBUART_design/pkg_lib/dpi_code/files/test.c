#include "svdpi.h"
#include "stdio.h"
#include "veriuser.h"
#define printf io_printf   // print to the console and stdio

extern void write(int, int);    // Imported from SystemVerilog
extern void drive(int, int);    // Imported from SystemVerilog

// This function simply takes in addr and data
// and calls the drive task implemented in SV 
// Local variables are declared only to display 
// debug capabilites
void c_write(const int addr, const int data)
{  
   int temp_addr, temp_data;
   temp_addr = addr;
   temp_data = data;

   // call the drive task in SV code
   drive(addr, data);

   temp_addr += 1;
   temp_data += 2;
}

// This function simply prints out the variables passed in
void print_it(const int print_addr, const int print_data)
{  
   printf("-----------------------------------------\n");
   printf("Address:%d and Data:%d written (by C code)\n", print_addr, print_data);
   printf("-----------------------------------------\n");
}
