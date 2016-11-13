import signal
import argparse

import serial

from pythonosc import dispatcher
from pythonosc import osc_server

class OSCServer:

    def __init__(self, dispatcher, ip='127.0.0.1', port=5005):
        self._server = osc_server.ThreadingOSCUDPServer(
            (ip, port), dispatcher)

    def serve_forever(self):
        print("Start serving on {}".format(self._server.server_address))
        self._server.serve_forever()

    def close(self):
        print("Stop serving on {}".format(self._server.server_address))
        self._server.server_close()

def figureTypeDispatcher(unused_addr, args, val):
    try:
        print(int(val))
    except ValueError:
        pass

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('--ip',
                        default='127.0.0.1', help='The ip to listen on')
    PARSER.add_argument('--port',
                        type=int, default=5005, help='The port to listen on')
    ARGS = PARSER.parse_args()

    DISPATCHER = dispatcher.Dispatcher()
    DISPATCHER.map('/filter', print)
    DISPATCHER.map('/figure', figureTypeDispatcher, 'Figure Type')

    SERVER = OSCServer(DISPATCHER, ARGS.ip, ARGS.port)

    def sigint_func(num, frame):
        SERVER.close()
        exit()
    signal.signal(signal.SIGINT, sigint_func)
    SERVER.serve_forever()
