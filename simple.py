import socket, select


def init():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _connect(sock)
    return sock

def _connect(sock):
    sock.connect(('csc.nmu.edu', 6667))
    sock.send('NICK PyBot\n')
    sock.send('USER PyBot linux.org server.com :PyBot\n')
    mainloop(sock)

def mainloop(sock):
    sockdata = ''
    while True:
        socklist = [sock]
        read_sock, write_sock, error_sock = select.select(socklist, socklist, socklist)
        for sock in read_sock:
            sockdata = sockdata + sock.recv(4096)
            # We might not get all our shit on one chunk
            chunks = sockdata.split('\n')
            sockdata = chunks.pop()
            for chunk in chunks:
                chunk = chunk.rstrip()
                parse_msg(chunk, sock)
                print chunk

def parse_msg(line, sock):
    line = line.split(' ')
    if line[0] == 'PING':
        sock.send('PONG ' + line[1] + '\n')
    elif line[1] == '376':
        sock.send('JOIN #Sarten-X\n')

#mysock = init()