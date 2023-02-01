#include <iostream>
#include <string>
#include <stdio.h>
#include <stdint.h>
#include <cstring>
#include <sstream>
#include <vector>
#include <fstream>
using namespace std;

#define CPU_ONLINE "/sys/devices/system/cpu/cpu%d/online"
#define CPU_MIN_FREQ "/sys/devices/system/cpu/cpu%d/cpufreq/scaling_min_freq"
#define CPU_MAX_FREQ "/sys/devices/system/cpu/cpu%d/cpufreq/scaling_max_freq"

#define GPU_MIN_FREQ "/sys/devices/17000000.gv11b/devfreq/17000000.gv11b/min_freq"
#define GPU_MAX_FREQ "/sys/devices/17000000.gv11b/devfreq/17000000.gv11b/max_freq"
#define GPU_ONLINE "/sys/devices/gpu.0/force_idle"

#define DLA_CORE_FREQ_0 "/sys/devices/13e10000.host1x/15880000.nvdla0/acm/clk_cap/dla0_core"
#define DLA_FALCON_FREQ_0 "/sys/devices/13e10000.host1x/15880000.nvdla0/acm/clk_cap/dla0_falcon"

#define DLA_CORE_FREQ_1 "/sys/devices/13e10000.host1x/158c0000.nvdla1/acm/clk_cap/dla1_core"
#define DLA_FALCON_FREQ_1 "/sys/devices/13e10000.host1x/158c0000.nvdla1/acm/clk_cap/dla1_falcon"

#define EMC_FREQ "/sys/kernel/debug/bpmp/debug/clk/emc/rate"
#define EMC_MIN "/sys/kernel/debug/bpmp/debug/clk/emc/min_rate"
#define EMC_MAX "/sys/kernel/debug/bpmp/debug/clk/emc/max_rate"
#define EMC_NV "/sys/kernel/nvpmodel_emc_cap/emc_iso_cap"


int setCoreOnline(int core, int flag){
	char coreFile[256];
	sprintf(coreFile,CPU_ONLINE, core);
	FILE* f_core = fopen(coreFile,"w");
	if(f_core == NULL){
		cerr << "File open failure"  << endl;
		return -1;
	}
	const char* tmp = to_string(flag).c_str();
	fputs(tmp, f_core);
	return 0;
}

int setAllCoresOnline(int flags[], int len){

	for(int i =0;i<len;i++){
		char coreFile[256];
		sprintf(coreFile, CPU_ONLINE, i+1);
		FILE* f_core = fopen(coreFile, "w");
		if(f_core == NULL){
			cerr << "File open failure"  << endl;
			return -1;
		}
		const char* tmp = to_string(flags[i]).c_str();
		fputs(tmp, f_core);
		fclose(f_core);
	}
	return 0;
}

int setCpuFreq(int core, uint64_t cFreq){

	char coreFile_MIN[256];
	char coreFile_MAX[256];

	const char* tmp = to_string(cFreq).c_str();
	//cout << "CPU freq: " << tmp <<  endl;

	sprintf(coreFile_MIN, CPU_MIN_FREQ, core);
	FILE* f_freq_min = fopen(coreFile_MIN,"w");

	if(f_freq_min == NULL){
		cerr << "CPU File open failure"  << endl;
		return -1;
	}

	fputs(tmp, f_freq_min);
	fclose(f_freq_min);

	sprintf(coreFile_MAX, CPU_MAX_FREQ, core);
	FILE* f_freq_max = fopen(coreFile_MAX,"w");

	if(f_freq_max == NULL){
		cerr << "CPU File open failure"  << endl;
		return -1;
	}

	fputs(tmp, f_freq_max);
	fclose(f_freq_max);

	return 0;
}

int setGpuFreq(uint64_t gFreq){

	const char* tmp = to_string(gFreq).c_str();
	//cout << "GPU freq: " << tmp <<  endl;

	FILE* f_freq_min = fopen(GPU_MIN_FREQ,"w");

	if(f_freq_min == NULL){
		cerr << "GPU File open failure"  << endl;
		return -1;
	}

	fputs(tmp, f_freq_min);
	fclose(f_freq_min);

	FILE* f_freq_max = fopen(GPU_MAX_FREQ,"w");

	if(f_freq_max == NULL){
		cerr << "GPU File open failure"  << endl;
		return -1;
	}

	fputs(tmp, f_freq_max);
	fclose(f_freq_max);

	return 0;
}

int setEmcFreq(uint64_t emcFreq){
	const char* tmp = to_string(emcFreq).c_str();
	//cout << "EMC freq: " << tmp <<  endl;

	FILE* f_freq = fopen(EMC_FREQ,"w");
	if(f_freq == NULL){
		cerr << "EMC File open failure"  << endl;
		return -1;
	}
	fputs(tmp, f_freq);
	fclose(f_freq);

	FILE* f_min = fopen(EMC_MIN,"w");
	if(f_min == NULL){
		cerr << "EMC File open failure"  << endl;
		return -1;
	}
	fputs(tmp, f_min);
	fclose(f_min);

	FILE* f_max = fopen(EMC_MAX,"w");
	if(f_max == NULL){
		cerr << "EMC File open failure"  << endl;
		return -1;
	}
	fputs(tmp, f_max);
	fclose(f_max);

	FILE* f_nv = fopen(EMC_NV,"w");
	if(f_nv == NULL){
		cerr << "EMC File open failure"  << endl;
		return -1;
	}
	fputs(tmp, f_nv);
	fclose(f_nv);

	return 0;
}

int setDlaFreq(int core, uint64_t dFreq){

	char coreFile_c[256];
	char coreFile_f[256];

	const char* tmp = to_string(dFreq).c_str();

	FILE* f_freq_dla_c;

	if(core == 0)
	{f_freq_dla_c = fopen(DLA_CORE_FREQ_0,"w");}
	else
	{f_freq_dla_c = fopen(DLA_CORE_FREQ_1,"w");}	

	if(f_freq_dla_c == NULL){
		cerr << "DLA_c File open failure"  << endl;
		return -1;
	}

	fputs(tmp, f_freq_dla_c);
	fclose(f_freq_dla_c);

	FILE* f_freq_dla_f;

	if(core == 0) 
        {f_freq_dla_f = fopen(DLA_FALCON_FREQ_0,"w");}
        else
        {f_freq_dla_f = fopen(DLA_FALCON_FREQ_1,"w");}

	if(f_freq_dla_f == NULL){
		cerr << "DLA_f File open failure"  << endl;
		return -1;
	}

	fputs(tmp, f_freq_dla_f);
	fclose(f_freq_dla_f);

	return 0;
}

int setConfig(string strConfig){
	stringstream stream(strConfig);
	vector<uint64_t> freq;
	uint64_t n;
	while(stream >> n){
		freq.push_back(n);
	}

	int cpu_core[8]={(int)freq[1],(int)freq[2], (int)freq[3], (int)freq[4], (int)freq[5], (int)freq[6], (int)freq[7], (int)freq[8]};
	int cpuFreq = freq[9];
	int gpuFreq = freq[10];
	int emcFreq = freq[11];
	int dla_core[2] = {freq[12], freq[13]};
	int dlaFreq = freq[14];

	//setAllCoresOnline(core, 8);
	for (int i=0; i<8; i++)
	{
		setCoreOnline(i, cpu_core[i]);
		setCpuFreq(i, cpuFreq);
	}

	setGpuFreq(gpuFreq);
	setEmcFreq(emcFreq);

	for (int i=0; i<2; i++)
	{
		if(dla_core[i] == 0)
		{
			setDlaFreq(i, 0);
		}
		else
		{
			setDlaFreq(i, dlaFreq);
		}

	}

	return 0;
}
