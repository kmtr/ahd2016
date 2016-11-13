'''OSC Arduino Motor
'''

import signal
import argparse
import logging

import serial

from pythonosc import dispatcher
from pythonosc import osc_server


logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('main')

class OSCServer:

    def __init__(self, dispatcher, ip='127.0.0.1', port=5005):
        self._server = osc_server.ThreadingOSCUDPServer(
            (ip, port), dispatcher)

    def serve_forever(self):
        '''server start and listen client'''
        LOGGER.info("Start serving on %s", self._server.server_address)
        self._server.serve_forever()

    def close(self):
        '''close server'''
        LOGGER.info("Stop serving on %s", self._server.server_address)
        self._server.server_close()


class MachineDriver:
    '''MachineDriver controlls all devices.
    One machine has some Arduinos
    '''

    arduinos = []

    def __init(self, arduino_ports):
        self.arduinos = []
        for i, port in enumerate(arduino_ports):
            self.arduinos[i] = ArduinoDriver(port, 3)

    def figure_type_dispatcher(self, unused_addr, args, val):
        try:
            LOGGER.debug(int(val))
        except ValueError:
            pass

class ArduinoDriver:
    '''ArduinoDriver controlls an arduino.
    '''

    SEP = ';'
    TERM = '\n'

    device_port = '/dev/null'

    '''
    @device ex: /dev/ttyUSB0
    '''
    def __init__(self, device_port, num_of_motors=3):
        self.device_port = device_port
        self.motors = []
        for i in range(0, num_of_motors):
            self.motors[i] = MotorDriver()

    def rotate(self):
        deltas = []
        for i in range(0, len(self.motors)):
            deltas[i] = self.motors[i]
        self.buildCommand(0, deltas)

    def buildCommand(self, led = 0, deltas = None):
        if deltas is None:
            deltas = [0, 0, 0]
        command = str(led)
        command += ArduinoDriver.SEP + ArduinoDriver.SEP.join(map(str, deltas))
        command += ArduinoDriver.TERM
        return command

    def sendCommand(self, command):
        with serial.Serial(self.device_port, 9600) as ser:
            try:
                ser.write(command.encode())
            except serial.portNotOpenError as ex:
                LOGGER.error(ex)


class MotorDriver:

    STEP_UNIT = 7.5
    MAX_STEP = 48

    def __init__(self):
        self.angle = 0

    def reset(self):
        self.angle = 0

    def rotate(self, step=0):
        step = step % MotorDriver.MAX_STEP
        delta = MotorDriver.STEP_UNIT * step
        delta = round(delta, 1)
        return delta


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('--ip',
                        default='127.0.0.1', help='The ip to listen on')
    PARSER.add_argument('--port',
                        type=int, default=5005, help='The port to listen on')
    ARGS = PARSER.parse_args()
    DRIVER = MachineDriver()

    DISPATCHER = dispatcher.Dispatcher()
    DISPATCHER.map('/filter', print)
    DISPATCHER.map('/figure', DRIVER.figure_type_dispatcher, 'Figure Type')

    SERVER = OSCServer(DISPATCHER, ARGS.ip, ARGS.port)

    def sigint_func(num, frame):
        '''sigint_func catch SIGINT and close osc server
        '''
        SERVER.close()
        exit()
    signal.signal(signal.SIGINT, sigint_func)
    SERVER.serve_forever()
