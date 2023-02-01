import os
import argparse
import time

# descr, i2c-addr, hwmon, channel

#### Power rails for Jetpack 5.x ####

# cat /sys/bus/i2c/drivers/ina3221/1-0040/hwmon/hwmon3/in1_input --> GPU voltage
# cat /sys/bus/i2c/drivers/ina3221/1-0040/hwmon/hwmon3/curr1_input --> GPU current

# cat /sys/bus/i2c/drivers/ina3221/1-0040/hwmon/hwmon3/in2_input --> CPU coltage
# cat /sys/bus/i2c/drivers/ina3221/1-0040/hwmon/hwmon3/curr2_input --> CPU current

# cat /sys/bus/i2c/drivers/ina3221/1-0041/hwmon/hwmon4/in1_input --> CV
# cat /sys/bus/i2c/drivers/ina3221/1-0041/hwmon/hwmon4/curr1_input --> CV

# cat /sys/bus/i2c/drivers/ina3221/1-0041/hwmon/hwmon4/in2_input --> DDR
# cat /sys/bus/i2c/drivers/ina3221/1-0041/hwmon/hwmon4/curr2_input --> DDR

_nodes = [
          ('module/cv', '0041', '1', '4'),
          ('module/cpu', '0040', '2', '3'),
          ('module/ddr', '0041', '2', '4'),
          ('module/gpu', '0040', '1', '3')] 

_valTypes = ['power']
_valTypesFull = ['power [mW]']


def getNodes():
    """Returns a list of all power measurement nodes, each a tuple of format (name, i2d-addr, channel)"""
    return _nodes

def getNodesByName(nameList=['module/gpu']):
    return [_nodes[[n[0] for n in _nodes].index(name)] for name in nameList]

def getPowerMode():
    return os.popen("nvpmodel -q | grep 'Power Mode'").read()[15:-1]

def setPowerMode(power_mode='0', enable_dvfs=False):
    os.system('nvpmodel -m {}'.format(power_mode))
    if enable_dvfs == False:
        os.system('jetson_clocks')

def readValue(i2cAddr='0040', channel='1', hwmon='3', valType='power'):

    """Reads a single value from the sensor"""
    fname = '/sys/bus/i2c/drivers/ina3221/1-{}/hwmon/hwmon{}/in{}_input'.format(i2cAddr, hwmon, channel) # read voltage
    with open(fname, 'r') as f:
        voltage = float(f.read())
    fname = '/sys/bus/i2c/drivers/ina3221/1-{}/hwmon/hwmon{}/curr{}_input'.format(i2cAddr, hwmon, channel) # read current
    with open(fname, 'r') as f:
        current = float(f.read())

    return voltage*current/1000

def getModulePower():
    """Returns the current power consumption of the entire module in mW."""
    return float(readValue(i2cAddr='0041', channel='2', hwmon='4', valType='power'))


def getAllValues(nodes=_nodes):
    """Returns all values (power, voltage, current) for a specific set of nodes."""
    return [[float(readValue(i2cAddr=node[1], channel=node[2], hwmon=node[3], valType=valType))
             for valType in _valTypes]
            for node in nodes]

def printFullReport():
    """Prints a full report, i.e. (power,voltage,current) for all measurement nodes."""
    from tabulate import tabulate
    header = []
    header.append('description')
    for vt in _valTypesFull:
        header.append(vt)

    resultTable = []
    for descr, i2dAddr, channel, hwmon, in _nodes:
        row = []
        row.append(descr)
        for valType in _valTypes:
            row.append(readValue(i2cAddr=i2dAddr, channel=channel, hwmon=hwmon, valType=valType))
        resultTable.append(row)

    print(tabulate(resultTable, header))


import threading
import time
class PowerLogger:
    """This is an asynchronous power logger. 
    Logging can be controlled using start(), stop(). 
    Special events can be marked using recordEvent(). 
    Results can be accessed through 
    """
    def __init__(self, interval=0.001, nodes=_nodes):
        """Constructs the power logger and sets a sampling interval (default: 0.01s) 
        and fixes which nodes are sampled (default: all of them)"""
        self.interval = interval
        self._startTime = -1
        self.eventLog = []
        self.dataLog = []
        self._nodes = nodes
 
    def start(self):
        "Starts the logging activity"""
        #define the inner function called regularly by the thread to log the data
        def threadFun():
            #start next timer
            self.start()
            #log data
            t = self._getTime() - self._startTime
            self.dataLog.append((t, getAllValues(self._nodes)))
            #ensure long enough sampling interval
            t2 = self._getTime() - self._startTime
            #assert(t2-t < self.interval)
             
        #setup the timer and launch it
        self._tmr = threading.Timer(self.interval, threadFun)
        self._tmr.start()
        if self._startTime < 0:
            self._startTime = self._getTime()
 
    def _getTime(self):
        return time.clock_gettime(time.CLOCK_REALTIME)
 
    def recordEvent(self, name):
        """Records a marker a specific event (with name)"""
        t = self._getTime() - self._startTime
        self.eventLog.append((t, name))
 
    def stop(self):
        """Stops the logging activity"""
        self._tmr.cancel()
 
    def getDataTrace(self, nodeName='module/main', valType='power'):
        """Return a list of sample values and time stamps for a specific measurement node and type"""
        pwrVals = [itm[1][[n[0] for n in self._nodes].index(nodeName)][_valTypes.index(valType)] 
                    for itm in self.dataLog]
        timeVals = [itm[0] for itm in self.dataLog]
        return timeVals, pwrVals
 
    def showDataTraces(self, names=None, valType='power', showEvents=True):
        """creates a PyPlot figure showing all the measured power traces and event markers"""
        if names == None:
            names = [name for name, _, _ , _ in self._nodes]
             
        #prepare data to display
        TPs = [self.getDataTrace(nodeName=name, valType=valType) for name in names]
        Ts, _ = TPs[0]
        Ps = [p for _, p in TPs]
        energies = [self.getTotalEnergy(nodeName=nodeName) for nodeName in names]
        Ps = list(map(list, zip(*Ps))) # transpose list of lists

        # draw figure
        import matplotlib.pyplot as plt
        plt.plot(Ts, Ps)
        plt.xlabel('time [s]')
        plt.ylabel(_valTypesFull[_valTypes.index(valType)])
        plt.grid(True)
        plt.legend(['%s (%.2f J)' % (name, enrgy / 1e3) for name, enrgy in zip(names, energies)])
        plt.title('power trace (NVPModel: %s)' % (os.popen("nvpmodel -q | grep 'Power Mode'").read()[15:-1],))
        if showEvents:
            for t, _ in self.eventLog:
                plt.axvline(x=t, color='black')

        plt.ioff()
        plt.savefig('fig.png', dpi=100)
         
    def showMostCommonPowerValue(self, nodeName='module/main', valType='power', numBins=100):
        """computes a histogram of power values and print most frequent bin"""
        import numpy as np
        _, pwrData = np.array(self.getDataTrace(nodeName=nodeName, valType=valType))
        count, center = np.histogram(pwrData, bins=numBins)
        #import matplotlib.pyplot as plt
        #plt.bar((center[:-1]+center[1:])/2.0, count, align='center')
        maxProbVal = center[np.argmax(count)]#0.5*(center[np.argmax(count)] + center[np.argmax(count)+1])
        print('max frequent power bin value [mW]: %f' % (maxProbVal,))
 
    def getTotalEnergy(self, nodeName='module/main', valType='power'):
        """Integrate the power consumption over time."""
        timeVals, dataVals = self.getDataTrace(nodeName=nodeName, valType=valType)
        assert(len(timeVals) == len(dataVals))
        tPrev, wgtdSum = 0.0, 0.0
        for t, d in zip(timeVals, dataVals):
            wgtdSum += d*(t-tPrev)
            tPrev = t
        return wgtdSum
     
    def getAveragePower(self, nodeName='module/main', valType='power'):
        energy = self.getTotalEnergy(nodeName=nodeName, valType=valType)
        timeVals, _ = self.getDataTrace(nodeName=nodeName, valType=valType)
        return energy/timeVals[-1]

if __name__ == "__main__" :

    parser = argparse.ArgumentParser()
    parser.add_argument("--power-mode", default="0", type=str, help="Set your power mode")
    parser.add_argument("--dvfs-enable", default=False, type=bool, help="Enable/Disable the automotatic dynamic frequency scaling")
    args = parser.parse_args()

    pl = PowerLogger(interval=0.005, nodes=list(filter(lambda n: n[0].startswith('module/'), getNodes())))        
    
    time.sleep(10)

    pl.start()   
    
    time.sleep(5)

    pl.stop()

    pl.showDataTraces()
    
    names = ['module/cpu', 'module/ddr', 'module/gpu', 'module/cv']
    powers = [pl.getAveragePower(nodeName=nodeName) for nodeName in names]

    for idx, name in enumerate(names, start=0):
        print('Power consumption of {} is {:.2f} mW'.format(name, powers[idx]))

