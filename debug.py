import json
import sys

TCP_IP = '127.0.0.1'
TCP_PORT = 5858

from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint


class Message:

    def __init__(self, type, headers, body):

        self.type = type
        self.headers = headers
        self.body = body

    def action(self):

        if self.type == "response":
            if 'Type' in self.headers and self.headers['Type'] == "connect":
                print("Connected")
            else:
                if 'event' in self.body:
                    print(self.body)


class Debugger(Protocol):

    def connectionMade(self):
        self.seq = 0
        self.raw = ''
        self.headers = {}
        self.state = 'headers'
        self.body = ''
        self.bodyStartIndex = 0
        self.contentLength = 0

    def sendMessage(self, message):
        self.seq += 1
        request = message
        request['type'] = "request"
        request['seq'] = self.seq

        data = json.dumps(request)
        headers = "Content-Length: %s\r\n\r\n" % (len(data))

        self.transport.write("".join([headers, data]))

    def dataReceived(self, data):
        self.parse(data)

    # Parses the data coming in from the node debugger
    def parse(self, data):
        self.raw += data

        if self.state == 'headers':
            endHeaderIndex = self.raw.find("\r\n\r\n")

            if endHeaderIndex < 0:
                return

            lines = self.raw[0:endHeaderIndex].split("\r\n")
            for line in lines:
                kv = line.split(": ")
                self.headers[kv[0]] = kv[1].lstrip()

            self.contentLength = int(self.headers['Content-Length'])
            self.bodyStartIndex = endHeaderIndex + 4

            self.state = 'body'
            if len(self.raw) - self.bodyStartIndex >= self.contentLength:
                self.parse('')

        elif self.state == 'body':
            if len(self.raw) - self.bodyStartIndex >= self.contentLength:
                self.body = self.raw[self.bodyStartIndex: self.bodyStartIndex + self.contentLength]
                if len(self.body) > 0:
                    self.body = json.loads(self.body)
                else:
                    self.body = {}

                Message("response", self.headers, self.body).action()

                self.reset(self.raw[self.bodyStartIndex + self.contentLength:])

        else:
            print "panic"

    def reset(self, data):
        self.raw = data
        self.headers = {}
        self.state = 'headers'
        self.body = ''

    def requestScripts(self):
        self.sendMessage({'command': 'scripts'})


class DebuggerFactory(Factory):
    def buildProtocol(self, addr):
        return Debugger()


def gotProtocol(p):
    p.sendMessage({'command': 'continue'})
    #reactor.callLater(2, p.transport.loseConnection)

if (len(sys.argv) > 1):
    point = TCP4ClientEndpoint(reactor, TCP_IP, TCP_PORT)
    d = point.connect(DebuggerFactory())
    d.addCallback(gotProtocol)
    reactor.run()
