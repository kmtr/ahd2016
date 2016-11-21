'''OSC Arduino Motor
'''

import argparse
import logging
import signal
import time

import serial

from pythonosc import dispatcher
from pythonosc import osc_server


logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('main')
SEP = ';'
TERM = '\n'
SERIAL_BAUDRATE = 57600

PATTERN = {
    -1: [ # reset
            [0, 0, 0, 0], # LEFT
            [0, 0, 0, 0], # RIGHT
    ],
    0: [ # T
            [90, 0, 0, 0], # LEFT
            [90, 0, 0, 0], # RIGHT
    ],
    1: [ # K
            [135, 0, 0, 0], # LEFT
            [0, 0, 0, 0], # RIGHT
    ],
}

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

    def set_dispatcher(self, unused_addr, args, side, idx, pos):
        LOGGER.debug('%d %d %d', side, idx, pos)
        try:
            self.arduino.set_pos(int(side), int(idx), int(pos))
        except Exception as ex:
            print(ex)
            pass

    def reset_dispatcher(self, unused_addr, args):
        self.arduino.reset()


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
        if self.led:
            self.sendCommand('l0')
            self.led = False
        else:
            self.sendCommand('l1')
            self.led = True

    def set_pos(self, side, idx, move):
        self.sendCommand(';'.join([str(side), str(idx), str(move)]))

    def reset(self):
        self.sendPattern(-1)

    def sendPattern(self, pattern_id):
        LOGGER.debug(PATTERN[int(pattern_id)])
        for side, positions in enumerate(PATTERN[int(pattern_id)]):
            for idx, pos in enumerate(positions):
                self.sendCommand(';'.join([
                    str(side),
                    str(idx),
                    str(pos)
                    ]))

    def sendCommand(self, command):
        print('sendCommand: ' + command)
        if DEBUG:
            return
        try:
            self.ser.write((command + TERM).encode())
            self.ser.flush()
        except serial.portNotOpenError as ex:
            LOGGER.error(ex)
        except ex:
            LOGGER.error(ex)

def testCommand(device_port, command):
    print(device_port)
    ser = serial.Serial(device_port, SERIAL_BAUDRATE)
    try:
        ser.write(("0;0;30\n").encode())
        ser.flush()
        time.sleep(5)
    except serial.portNotOpenError as ex:
        LOGGER.error(ex)
    except Exception as ex:
        LOGGER.error(ex)


DEBUG = False
WAIT_TIME = 10

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
    if DEBUG:
        WAIT_TIME = 0

    LOGGER.info('BAURATE: %s', SERIAL_BAUDRATE)
    LOGGER.info('devices: %s', ARGS.dev)
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

    SERVER = OSCServer(DISPATCHER, ARGS.ip, ARGS.port)

    def sigint_func(_num, _frame):
        '''sigint_func catch SIGINT and close osc server
        '''
        SERVER.close()
        exit()
    signal.signal(signal.SIGINT, sigint_func)
    SERVER.serve_forever()
