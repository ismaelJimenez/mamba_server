import socketserver
import os
import subprocess
import sys


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        while True:
            command = self.rfile.readline()
            if not command:  # EOF
                break
            self.wfile.write("your command was: %s" % (command, ))


def main(args):
    server = ThreadedTCPServer(("0.0.0.0", 8080), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    sys.exit(main(sys.argv))
