# JetsonPower
Python framework for power consumption monitoring and scaling on NVIDIA Jetson boards

## Requirements
- You need to set your Jetson board with a JetPack version >= 5.0.1

- We'll add support for older JetPack versions (4.x.y) soon.

## Usage 
### - Power consumption measurements

``` sh
python3 {board}_power.py --power-mode {mode} --dvfs-enable {True|False}
```

### - Frequency scaling (DVFS) and hardware re-configuration
``` sh
g++ change_config.cpp -o change_config
sudo ./change_config 0_{online_cpu_cores}_{cpu_freq}_{gpu_freq}_{memory_freq}_{online_dla_cores}_{dla_freq}
```
