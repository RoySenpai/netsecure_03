# Network Security Assignment 3 (Project)
### For Computer Science B.Sc. Ariel University

**By Shahar Zaidel and Roy Simanovich**

## Description
This is a summary project of the course “Protection of Communication Protocols”, that was led by Dr. Ran Dubin.
In the project, we researched about Man in The Middle attacks that could occur on PLC, that don’t alert the HMI.
The purpose of this research is to see how cyber-security is relevant even on isolated networks such as factories,
where critical and crucial information could leak by exploiting the security vulnerabilities of the communication
protocol that PLCs use. This task was prepared by Otorio and is supervised by Dr. Ran Dubin. The project’s system
was built as a factory that uses light bulbs for its productions. The system is divided into two parts: The PLC
itself and the HMI, by using two virtual machines.

### PLC machine
This is the PLC Virtual Machine that contains the PLC logic itself (simulated), its I/O script and the MiTM proxy
channel where the attack occurs and where we focus our project on. All of those components communicate
through TCP port 2502. The main `plc.py` python script file, that changes the light bulbs status every 3 seconds
look something like this:
```python
from pymodbus.client.sync import ModbusTcpClient
from time import sleep

client = ModbusTcpClient('127.0.0.1', 2502)
even_round = False

while True:
	# b = ((even_round and ((i+1) % 2 == 0)) or (not even_round and ((i+1) % 2 != 0)))
	client.write_coil(0, even_round, unit=0x01)
	client.write_coil(1, not even_round, unit=0x01)
	client.write_coil(2, even_round, unit=0x01)
	client.write_coil(3, not even_round, unit=0x01)
	client.write_coil(4, even_round, unit=0x01)
	client.write_coil(20, even_round, unit=0x01)
	even_round = not even_round
	sleep(3)
```

To communicate with the HMI, the PLC uses the [TCP Proxy tool](https://github.com/ickerwx/tcpproxy), where the MiTM is
handled. The packets go from Modbus PLC itself to the TCP Proxy, where the malicious attack of the MiTM can be performed.
The `malicious.py` file, which is the MiTM attack module that’s used in the TCP Proxy tool, contains the following code:
```python
#!/usr/bin/env python2
import os.path as path
import struct

class Module:
	def __init__(self, incoming=False, verbose=False, options=None):
		self.name = path.splitext(path.basename(__file__))[0]
		self.description = 'Simply print the received data as text'
		self.incoming = incoming # incoming means module is on -im chain

	def execute(self, data):
		return data

	def help(self): 
		return ""

if __name__ == '__main__':
	print 'This module is not supposed to be executed alone!'
```

Currently this code does nothing, but only returns the data as is. This project contains our research, and our
malicious code.

### SCADA machine
Human Machine Interface, often known by the acronym HMI, refers to a dashboard or screen used to control machinery.
Line operators, managers and supervisors in industry rely on HMIs to translate complex data into useful information.
But the advanced capabilities of today’s HMIs enable managers and supervisors to do much more than control processes.
Using historical and trending data they offer vast new opportunities to improve product quality and make systems
more efficient. For all these reasons, HMIs play a key role in the smooth and effective running of factories and
manufacturing operations. But not all HMIs are created the same. HMIs should be easy to understand, but the reality
is they often aren’t. Frequently, they overload operators with information and make their jobs needlessly stressful
and demanding. As a result, operators with the skills and expertise to quickly process and handle vast quantities of
complex information can be hard to find. To compound this problem, many HMIs are unable to keep pace with technology
or adapt when a business grows. Some HMI software fails to support older operating systems, or only works with a small
family of hardware. This means traditional HMIs can become obsolete quickly and turn out to be expensive short-term
investments. ScadaBR is a SCADA (Supervisory Control and Data Acquisition) system with applications in Process Control
and Automation, being developed and distributed using the open-source model. For our HMI, the light should switch
every 3 seconds, and no alerts are being reported by the HMI itself.


### Communication
According to the schematics, the PLC VM and the HMI VM communicate via TCP port 502, which is used for Modbus TCP/IP
protocol. The HMI sends request packets to the PLC, to read the coils 0 to 4 (which represents the 5 light bulbs) via
function code 1, and the PLC responses with the values of the light bulbs.
