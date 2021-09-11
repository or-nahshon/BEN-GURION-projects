import random
from sys import path as sysPath
import rticonnextdds_connector as rti
from os import path as osPath
from time import sleep

'''
Component: Temp sensor 2
A publisher component.
Msg: include 2 messages: 1. sensor ID 2. temp

every 0.1 second:
    1. lottery a random temp between 0 to 50
    2. send message included sensor ID and the random temp (from step 1)
    3. prints the message to a console 

'''

filepath = osPath.dirname(osPath.realpath(__file__))
connector = rti.Connector("MyParticipantLibrary::TempSensor2", filepath + "/DDS.xml")
outputDDS = connector.getOutput("TempSensor2::temp_writer")
component = "temp_sensor_2"

while True:
    randNum = random.randint(0, 50)
    outputDDS.instance.setNumber("sensorID", 2)
    outputDDS.instance.setNumber("temp", randNum)
    outputDDS.write()
    print(f'published: {component}, Msg: {randNum}')
    sleep(0.1)

