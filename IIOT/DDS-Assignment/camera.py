from sys import path as sysPath
import rticonnextdds_connector as rti
from os import path as osPath
from time import sleep
from datetime import datetime

'''
Component: Camera.
A publisher component.
Msg: a string message with real time in it

every 0.1 seconds:
    1. sends a message
    2. prints the message to a console 
'''

filepath = osPath.dirname(osPath.realpath(__file__))
connector = rti.Connector("MyParticipantLibrary::Camera", filepath + "/DDS.xml")
outputDDS = connector.getOutput("Camera::time_writer")
component = "camera"

while True:
    current_time = datetime.now().strftime("%H:%M:%S.%f")
    outputDDS.instance.setString("camera", current_time)
    outputDDS.write()
    print(f'published: {component}, Msg: {current_time}')
    sleep(0.1)


