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


commands = {
    0: [
        [12, 24, 36, 24, 12, 0],
        [12, 12, 12, 12, 10, 0],
    ],
}

class MachineDriver:
    '''MachineDriver controlls all devices.
    One machine has some Arduinos
    '''

    arduinos = []
    busy = False

    def __init__(self, arduino_ports):
        self.arduinos = []
        for i, port in enumerate(arduino_ports):
            # set arudino which has N motors
            self.arduinos.append(ArduinoDriver(i, port, 5))
        MachineDriver.busy = False

    def status(self):
        LOGGER.info('STATUS:')
        for arduino in self.arduinos:
            arduino.status()

    def save(self, filename='pos.sav'):
        with open(filename, 'w') as f:
            for arduino in self.arduinos:
                data = []
                data.append(str(arduino.index))
                for motor in arduino.motors:
                    data.append(str(motor.pos))
                data.append('\n')
                f.writelines(';'.join(data))
        LOGGER.info('saved')

    def load(self, filename='pos.sav'):
        with open(filename) as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                arduino = self.arduinos[int(line[0])]
                positions = line[2:len(line)-2].split(';')
                for i, pos in enumerate(positions):
                    arduino.motors[i].reset(int(pos))

    def status_dispatcher(self, unused_addr, args):
        self.status()

    def save_dispatcher(self, unused_addr, args):
        self.save()

    def load_dispatcher(self, unused_addr, args):
        self.load()

    def pong_dispatcher(self, unused_addr, args):
        if MachineDriver.busy:
            return
        print('pong')

        MachineDriver.busy = True
        time.sleep(1)
        MachineDriver.busy = False

    def figure_type_dispatcher(self, unused_addr, args, val):
        if MachineDriver.busy:
            return
        try:
            cmds = commands[int(val)]
            LOGGER.debug(cmds)
            for i, cmd in enumerate(cmds):
                self.arduinos[i].set_pos(cmd)

            MachineDriver.busy = True
            time.sleep(10)
            MachineDriver.busy = False
        except ValueError:
            pass

    def set_dispatcher(self, unused_addr, args, arduino, motor, pos):
        if MachineDriver.busy:
            return
        target = self.arduinos[arduino]
        cmd = [m.pos for m in target.motors]
        if len(cmd) - 1 < motor:
            return
        cmd[motor] = pos
        self.arduinos[arduino].set_pos(cmd)

        MachineDriver.busy = True
        time.sleep(10)
        MachineDriver.busy = False

    def rot_dispatcher(self, unused_addr, args, arduino, motor, step):
        if MachineDriver.busy:
            return
        target = self.arduinos[arduino]
        cmd = [m.pos for m in target.motors]
        if len(cmd) - 1 < motor:
            return
        cmd[motor] += step
        self.arduinos[arduino].set_pos(cmd)

        MachineDriver.busy = True
        time.sleep(10)
        MachineDriver.busy = False

    def reset_dispatcher(self, unused_addr, args, arduino, motor, pos):
        if MachineDriver.busy:
            return
        target = self.arduinos[arduino]
        if len(target.motors) - 1 < motor:
            return
        target.motors[motor].reset(pos)

        MachineDriver.busy = True
        time.sleep(0.01)
        MachineDriver.busy = False


class ArduinoDriver:
    '''ArduinoDriver controlls an arduino.
    '''

    SEP = ';'
    TERM = '\n'

    device_port = '/dev/null'

    def __init__(self, index, device_port, num_of_motors=5):
        '''
        @device_port ex: /dev/ttyUSB0
        @num_of_motors Number of motors
        '''
        self.index = index
        self.device_port = device_port
        self.motors = []
        for i in range(0, num_of_motors):
            self.motors.append(MotorDriver(i))

    def status(self):
        LOGGER.info('Arduino %s:', self.index)
        for m in self.motors:
            LOGGER.info('Motor %s: position %d', m.index, m.pos)

    def set_pos(self, positions = []):
        steps = []
        for i, pos in enumerate(positions[:len(self.motors)]):
            steps.append(self.motors[i].set_pos(pos))
        self.buildCommand(0, steps)

    def buildCommand(self, led = 0, steps = None):
        if steps is None:
            return 'x\n'
        command = ArduinoDriver.SEP.join(map(str, steps))
        command += ArduinoDriver.SEP + str(led)
        command += ArduinoDriver.TERM
        LOGGER.info('Arduino %s: command %s', self.index, command)
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

    def __init__(self, index=0):
        self.index = index
        self.pos = 0

    def status(self):
        LOGGER.info('Motor %s: position %d', self.index, self.pos)

    def reset(self, pos):
        LOGGER.info('Motor %s: reset position %d (on memory)', format(self.index), pos)
        self.pos = pos

    def set_pos(self, pos):
        _pos = pos % MotorDriver.MAX_STEP
        step = - (self.pos - _pos)
        self.pos = _pos
        self.status()
        return step


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('--ip',
                        default='127.0.0.1', help='The ip to listen on')
    PARSER.add_argument('--port',
                        type=int, default=5005, help='The port to listen on')
    PARSER.add_argument('--devs',
                        default=['/dev/null'], nargs='+', help='usb devices. ex: /dev/null')
    ARGS = PARSER.parse_args()
    LOGGER.info('devices: %s', ARGS.devs)
    DRIVER = MachineDriver(ARGS.devs)

    DISPATCHER = dispatcher.Dispatcher()

    DISPATCHER.map('/ping', DRIVER.pong_dispatcher, 'PONG')
    DISPATCHER.map('/status', DRIVER.status_dispatcher, 'status')
    DISPATCHER.map('/save', DRIVER.save_dispatcher, 'save')
    DISPATCHER.map('/load', DRIVER.load_dispatcher, 'load')

    DISPATCHER.map('/figure', DRIVER.figure_type_dispatcher, 'Figure Type')
    DISPATCHER.map('/set', DRIVER.set_dispatcher, 'Set Arduino Motor Position')
    DISPATCHER.map('/rot', DRIVER.rot_dispatcher, 'Rotate Arduino Motor step')
    DISPATCHER.map('/reset', DRIVER.reset_dispatcher, 'Reset Arduino Motor')

    SERVER = OSCServer(DISPATCHER, ARGS.ip, ARGS.port)

    def sigint_func(_num, _frame):
        '''sigint_func catch SIGINT and close osc server
        '''
        SERVER.close()
        exit()
    signal.signal(signal.SIGINT, sigint_func)
    SERVER.serve_forever()
