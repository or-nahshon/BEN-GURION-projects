import rticonnextdds_connector as rti
from os import path as osPath
from time import sleep


filepath = osPath.dirname(osPath.realpath(__file__))

connector = rti.Connector("MyParticipantLibrary::Dashboard",  filepath + "/DDS.xml")
input_time = connector.getInput("Dashboard::time_reader")
input_temp = connector.getInput("Dashboard::temp_reader")
input_actuators = connector.getInput("Dashboard::status_reader")

'''
Component: Dashboard
Subscriber component.

every 5 seconds print to console:
    - camera status
    - Actuator 1
    - Actuator 2
    - Extreme Temp. 1
    - Extreme Temp. 2
    with helper functions outputCamera(), outputActuators(), outputTempSensors()
'''

def outputCamera():
    '''
    print the last message received from the camera
    if there is not message - print '--'
    '''
    input_time.read()
    if input_time.samples.getLength() > 0:  # and input_time.samples[input_time.samples.length-1].valid_data:
        last_camera_msg = input_time.samples[input_time.samples.length - 1].get_string('camera')
    else:
        last_camera_msg = '--'
    print(f'Camera: {last_camera_msg}')

def outputActuators():
    '''
    for each actuator:
        print a list of last 10 published statuses
        if there is not message - print empty arr
    '''
    arrActuator1 = []
    arrActuator2 = []
    input_actuators.read()
    numOfSamples = input_actuators.samples.getLength()
    for j in range(0, numOfSamples):
        if input_actuators.infos.isValid(j):
            actuatorID = input_actuators.samples.getNumber(j, "actuatorID")
            status = input_actuators.samples.getString(j, "status")
            if actuatorID == 311330500:
                arrActuator1.append(status)
            if actuatorID == 311124564:
                arrActuator2.append(status)
    print(f'Actuator 1: {arrActuator1}')
    print(f'Actuator 2: {arrActuator2}')




def outputTempSensors():
    '''
    for each actuator:
        print a list of last 10 extreme temperatures
        if there is not message - print empty arr
    '''
    arrTemp1 = []
    arrTemp2 = []
    input_temp.read()
    numOfSamples = input_temp.samples.getLength()
    for j in range(0, numOfSamples):
        if input_temp.infos.isValid(numOfSamples-j-1):
            sensorID = input_temp.samples.getNumber(numOfSamples-j-1, "sensorID")
            temp = input_temp.samples.getNumber(numOfSamples-j-1, "temp")
            if sensorID == 1 and (temp < 20 or temp > 40) and len(arrTemp1) <= 10:
                arrTemp1.append(temp)
            if sensorID == 2 and temp > 40 and len(arrTemp2) <= 10:
                arrTemp2.append(temp)
        if len(arrTemp1)==10 and len(arrTemp2)==10:
            break
    print(f'Extreme Temp. 1: {arrTemp1}')
    print(f'Extreme Temp. 2: {arrTemp2}')


while True:
    sleep(5)
    outputCamera()
    outputActuators()
    outputTempSensors()
    print('\n')






