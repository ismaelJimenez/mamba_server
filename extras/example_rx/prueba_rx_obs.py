import logging
import threading
import time
import socketserver

from rx.subject import Subject
from rx import Observable


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        self.server.mi_subject.on_next(self.data)
        # just send back the same data, but upper-cased
        #self.request.sendall(self.data.upper())
        self.request.sendall(b'> OK helo tp_gpltp_test\r\n')


def thread_server(mi_subject):
    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer(("localhost", 8080), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.mi_subject = mi_subject
        logging.info("SERVER STARTED")
        server.serve_forever()
        logging.info("SERVER FINISHED")


def thread_function(mi_subject):
    #logging.info("Thread %s: starting", name)
    for i in range(0, 100):
        mi_subject.on_next(i)
        logging.info("Loop %d", i)
        time.sleep(1)

    #logging.info("Thread %s: finishing", name)


class CustomSubscriber:
    def __init__(self, subject):
        super(CustomSubscriber, self).__init__()

        subject.subscribe(
            on_next=lambda i: print("Received ASDF {0}".format(i)),
            on_error=lambda e: print("Error Occurred: {0}".format(e)),
            on_completed=lambda: print("Done!"),
        )
        print("PERICO")


def execute():
    format = "%(asctime)s: %(message)s"

    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    logging.info("Main    : before creating thread")

    #mi_subject = Subject()
    mi_subject = Observable()

    custom = CustomSubscriber(mi_subject)

    x = threading.Thread(target=thread_server, args=(mi_subject, ))

    logging.info("Main    : before running thread")

    x.start()

    logging.info("Main    : wait for the thread to finish")

    # x.join()

    logging.info("Main    : all done")


if __name__ == "__main__":
    execute()
