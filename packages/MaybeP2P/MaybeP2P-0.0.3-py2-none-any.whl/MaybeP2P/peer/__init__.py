import logging, socket, threading, traceback, copy
from uuid import uuid4

from ..protocol.classicv1 import ClassicV1
from .peerinfo import PeerInfo
from .connection import PeerConnection

class Peer(threading.Thread):

    def __init__(self, pid=uuid4(), serverAddr='0.0.0.0', serverPort=25565, protocol=ClassicV1):
        threading.Thread.__init__(self)
        self.stopped = False
        self.lock = threading.RLock()

        self.id = pid
        self.listenHost = (serverAddr, int(serverPort))
        logging.debug('Listening at %s:%d' % (self.listenHost))

        self.peerInfo = PeerInfo(pid, (self._initServerAddr(), serverPort), 'Active')
        logging.debug('Link IP: %s' % self.peerInfo.addr)

        self.protocol = self._initPeerProtocol(protocol)
        logging.debug('Protocol loaded.')

        logging.info('Inited Peer %s' % self.id)

    def _initServerAddr(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('www.google.com', 80))
        host = s.getsockname()[0]
        s.close()
        return host

    def _initServerSock(self):
        try:
            self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.serverSock.bind(self.listenHost)
            self.serverSock.listen(5)
            logging.info('Inited server socket')
        except:
            return False
        return True

    def _initPeerProtocol(self, protocol):
        setattr(self, protocol.__name__, protocol(self))
        return self.ClassicV1

    def start(self):
        self._initServerSock()
        super(Peer, self).start()

    def run(self):
        while not self.stopped:
            try:
                clientSock, clientAddr = self.serverSock.accept()
                peerConn = PeerConnection(None, self, sock=clientSock)
                peerConn.start()
            except KeyboardInterrupt:
                self.stopped = True
                continue
        self.serverSock.close()

    def exit(self):
        self.stopped = True
        self.protocol.exit()

    def sendToPeer(self, message, host, pid=None, waitReply=True, timeout=None):
        msgReply = []
        try:
            peerConn = PeerConnection(pid, self, host=host)
            peerConn.sendData(message)

            if waitReply:
                oneReply = peerConn.recvData()
                while (oneReply != (None, None, None)):
                    msgReply.append( oneReply )
                    oneReply = peerConn.recvData()

                for (protoType, msgType, msgData) in msgReply:
                    peerConn.protocol.handler(peerConn, msgType, msgData)
            peerConn.exit()
        except Exception as e:
            traceback.print_exc()
        return msgReply

