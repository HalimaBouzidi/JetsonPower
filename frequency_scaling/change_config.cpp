// System Includes
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>
#include "set_config.h"

int main(int argc, char** argv){

	//ifstream infile("bounds.config");	
	//string line = "0_1_1_1_1_0_0_0_0_2188800_670000000_1331200000_0_0_1050000000";
	std::stringstream line(argv[1]);
	std::string line_="";
	std::string s;

	while (getline(line, s, '_')) {
		line_.append(std::string(s).append(" "));
	}

	setConfig(line_);

	return 0;
}
