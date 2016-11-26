'''OSC Arduino Motor
'''

import argparse
import logging
import random
import signal
import time

import serial

from pythonosc import dispatcher
from pythonosc import osc_server

from pattern import PATTERN

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('main')
SEP = ';'
TERM = '\n'
SERIAL_BAUDRATE = 9600
NUM_OF_MOTOR = 8
LEFT_ARM = 0
RIGHT_ARM = 1

def randomizer(a, b):
    seed0 = random.randint(a, b)
    seed1 = random.randint(a, b)
    print(seed0)
    print(seed1)
    if seed0 < seed1:
        return random.randint(int(seed0), int(seed1))
    else:
        return random.randint(int(seed1), int(seed0))

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
    '''

    def __init__(self, arduino_port):
        self.arduino = ArduinoDriver(arduino_port)

    def status_dispatcher(self, unused_addr, args):
        LOGGER.info('STATUS')
        self.arduino.status()

    def pong_dispatcher(self, unused_addr, args):
        print('pong')

    def pattern_dispatcher(self, unused_addr, args, val):
        try:
            self.arduino.sendPattern(val)
        except Exception as ex:
            print(ex)

    def set_dispatcher(self, unused_addr, args, a0, a1, a2, a3, a4, a5, a6, a7):
        LOGGER.debug('%d %d %d %d | %d %d %d %d', a0, a1, a2, a3, a4, a5, a6, a7)
        try:
            self.arduino.set_pos(a0, a1, a2, a3, a4, a5, a6, a7)
        except Exception as ex:
            print(ex)
            pass

    def reset_dispatcher(self, unused_addr, args):
        self.arduino.reset()

    def random_dispatcher(self, unused_addr, args):
        pattern = []
        for i in range(NUM_OF_MOTOR):
            pattern.append(int(randomizer(0, 180)))
        self.arduino.sendCommand(SEP.join(str(a) for a in pattern))

class ArduinoDriver:
    '''ArduinoDriver controlls an arduino.
    '''

    device_port = '/dev/null'

    def __init__(self, device_port):
        '''
        @device_port ex: /dev/ttyUSB0
        @num_of_motors Number of motors
        '''
        self.led = False
        self.device_port = device_port
        if not DEBUG:
            self.ser = serial.Serial(self.device_port, SERIAL_BAUDRATE)

    def status(self):
        LOGGER.info('Arduino:')
        self.set_led(not self.led)

    def set_led(self, tika):
        if tika:
            self.sendCommand('l1')
            self.led = True
        else:
            self.sendCommand('l0')
            self.led = False

    def set_pos(self, a0, a1, a2, a3, a4, a5, a6, a7):
        self.sendCommand(SEP.join(str(a) for a in [a0, a1, a2, a3, a4, a5, a6, a7]))

    def reset(self):
        self.sendPattern(-1)

    def sendPattern(self, pattern_id):
        LOGGER.debug("PATTERN %d", pattern_id)
        self.set_pos(*PATTERN[int(pattern_id)])

    def sendCommand(self, command):
        print('sendCommand: ' + command)
        if DEBUG:
            return
        try:
            self.ser.write((command + TERM).encode())
            self.ser.flush()
            time.sleep(0.100)
        except serial.portNotOpenError as ex:
            LOGGER.error(ex)
        except Exception as ex:
            LOGGER.error(ex)

def testCommand(device_port, command):
    ser = serial.Serial(device_port, SERIAL_BAUDRATE)
    try:
        ser.write(("0;0;30\n").encode())
        ser.flush()
        time.sleep(1)
    except serial.portNotOpenError as ex:
        LOGGER.error(ex)
    except Exception as ex:
        LOGGER.error(ex)


DEBUG = False

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('--ip',
                        default='127.0.0.1', help='The ip to listen on')
    PARSER.add_argument('--port',
                        type=int, default=5005, help='The port to listen on')
    PARSER.add_argument('--dev',
                        default='/dev/null', help='usb device. ex: /dev/ttyUSB0')
    PARSER.add_argument('--cmd',
                        default='', help='command')
    PARSER.add_argument('--debug',
                        type=bool, default=False)

    ARGS = PARSER.parse_args()
    DEBUG = ARGS.debug

    LOGGER.info('BAURATE: %s', SERIAL_BAUDRATE)
    LOGGER.info('device: %s', ARGS.dev)
    if ARGS.cmd != '':
        testCommand(ARGS.dev, ARGS.cmd)
        exit()

    MACHINE = MachineDriver(ARGS.dev)

    DISPATCHER = dispatcher.Dispatcher()
    DISPATCHER.map('/ping', MACHINE.pong_dispatcher, 'PONG')
    DISPATCHER.map('/status', MACHINE.status_dispatcher, 'status')
    DISPATCHER.map('/pattern', MACHINE.pattern_dispatcher, 'Pattern Type')
    DISPATCHER.map('/set', MACHINE.set_dispatcher, 'Set Arduino Motor Position')
    DISPATCHER.map('/reset', MACHINE.reset_dispatcher, 'Reset')
    DISPATCHER.map('/random', MACHINE.random_dispatcher, 'Random')

    SERVER = OSCServer(DISPATCHER, ARGS.ip, ARGS.port)

    def sigint_func(_num, _frame):
        '''sigint_func catch SIGINT and close osc server
        '''
        SERVER.close()
        exit()
    signal.signal(signal.SIGINT, sigint_func)
    SERVER.serve_forever()
