import rticonnextdds_connector as rti
from os import path as osPath
from time import sleep
filepath = osPath.dirname(osPath.realpath(__file__))

connector = rti.Connector("MyParticipantLibrary::Actuator1",  filepath + "/DDS.xml")
input_temp = connector.getInput("subActuator1::temp_reader")
input_button = connector.getInput("subActuator1::button_reader")
output_status = connector.getOutput("pubActuator1::status_writer")

'''
Component: Actuator 1. ID-311124564
publisher&subscriber component.
Msg: include 2 messages: 1. Actuator ID 2. current status

 - begins with default status - Working.
 - then, while True:
    1. check sensor1's status with checkingTemp() function
    2. check startStop button status with checkIfStop() function
    2. check new actuator's status with status_selctor() function
    3. if there is change between new status and current status:
        3.1 update current status to be new status
        3.2 send message included actuator ID and the current status
        3.3 prints the message to a console 

'''

componentID = 311124564
currentStatus = 'Working'
sleep(0.5)
output_status.instance.setNumber("actuatorID", componentID)
output_status.instance.setString("status", currentStatus)
output_status.write()
print(f'published: actuator_{componentID}, Msg: {currentStatus}')


def checkingTemp():
    """
    read sensor1 temp, and checks if received temp is normal
    Normal temp is in rang 0-40
    :return:
        None- there is no temp received from sensor
        False- temp isn't normal
        True- temp is normal
    """
    input_temp.read()
    numOfSamples = input_temp.samples.getLength()
    lastTemp = None
    if numOfSamples > 0:
        for j in range(0, numOfSamples):
            if input_temp.samples[j].get_number('sensorID') == 2:
                lastTemp = input_temp.samples.getNumber(j, "temp")
        if lastTemp is None:
            return None    # there is no temp received from sensor2
        elif lastTemp > 40:
            return False   # not normal temp
        else:
            return True   # normal temp
    return None # there is no temp received from sensor1 or sensor2

def checkIfStop():
    """
    read button status, and checks if status is 'stop'
    :return:
        true - status is 'stop'
        false- status isn't
    """
    input_button.read()
    if input_button.samples.getLength() > 0:
        return input_button.samples[0].get_string('status') == 'stop'
    return False

def status_selctor(status, tempStatus, buttonStatus):
    '''
    Getting current status, tempStatus buttonStatus and checking what is the next status
    :param status: current actuator1's status - {Working,Degraded,Stopped}
    :param tempStatus: boolean variable or None - received from checkingTemp() function
    :param buttonStatus: boolean variable - received from checkIfStop() function

    :return: update status - {Working,Degraded,Stopped}
    '''

    if buttonStatus is True: #button currentStatus is stop
        return 'Stopped'

    if tempStatus is None:  # if there is no input of temp, status return will be the same
        print('Inactive sensor2 temp')
        return status

    if status == 'Working' or status == 'Degraded':
        if tempStatus is True:  #normal temp
            return 'Working'
        else:
            return 'Degraded'

    if status == 'Stopped':
        return 'Working'


while True:

    tempStatus = checkingTemp()
    buttonStatus = checkIfStop()
    newStatus = status_selctor(currentStatus, tempStatus, buttonStatus)
    if newStatus != currentStatus:
        currentStatus = newStatus
        output_status.instance.setNumber("actuatorID", componentID)
        output_status.instance.setString("status", currentStatus)
        output_status.write()
        print(f'published: actuator_{componentID}, Msg: {currentStatus}')
