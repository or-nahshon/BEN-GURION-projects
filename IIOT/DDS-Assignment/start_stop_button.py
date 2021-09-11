from sys import path as sysPath
import rticonnextdds_connector as rti
from os import path as osPath
from time import sleep

'''
Component: Start/Stop button
A publisher component.
Msg: a string message with button status (start/stop)

 - begins with default status - start.
 - waits 20 sec
 - then, while True:
    1. sends and prints status message - stop
    2. waits 5 sec
    3. sends and prints status message - start
    4. waits 15 sec

'''

filepath = osPath.dirname(osPath.realpath(__file__))
connector = rti.Connector("MyParticipantLibrary::StartStopButton", filepath + "/DDS.xml")
outputDDS = connector.getOutput("StartStopButton::button_writer")
component = "start_stop_button"

def send_msg(status, time_sleep):
    outputDDS.instance.setString("status", status)
    outputDDS.write()
    print(f'published: {component}, Msg: {status}')
    sleep(time_sleep)

send_msg("start", 20)
while True:
    send_msg("stop", 5)
    send_msg("start", 15)
