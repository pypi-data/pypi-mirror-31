import socket, ssl, time, event
LQUEUE_SIZE = 5
BUFFER_SIZE = 131072
SSL_HANDSHAKE_TICK = 0.1
SSL_HANDSHAKE_TIMEOUT = 1

def ssl_handshake(sock, cb):
    deadline = time.time() + SSL_HANDSHAKE_TIMEOUT
    def shaker():
        try:
            sock.settimeout(SSL_HANDSHAKE_TICK)
            sock.do_handshake()
            sock.settimeout(0)
        except Exception, e:
            if time.time() > deadline:
                sock.close()
            else:
                return True
        else:
            cb()
    event.timeout(SSL_HANDSHAKE_TICK, shaker)

def server_socket(port, certfile=None, keyfile=None, cacerts=None):
    ''' Return a listening socket bound to the given interface and port. '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind(('', port))
    sock.listen(LQUEUE_SIZE)
    if certfile:
        if hasattr(ssl, "SSLContext"):
            ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ctx.load_cert_chain(certfile, keyfile)
            ctx.load_default_certs()
            if cacerts:
                ctx.verify_mode = ssl.CERT_OPTIONAL
                ctx.load_verify_locations(cacerts)
            return ctx.wrap_socket(sock, server_side=True, do_handshake_on_connect=False)
        return ssl.wrap_socket(sock, certfile=certfile,
            keyfile=keyfile, server_side=True, do_handshake_on_connect=False)
    return sock

def client_socket(addr, port, certfile=None, keyfile=None):
    sock = socket.socket()
    sock.setblocking(False)
    try:
        sock.connect_ex((addr, port))
    except socket.error:
        # this seems to happen when there are
        # > 1016 connections, for some reason.
        # we need to get to the bottom of this
        raise SocketError, "the python socket cannot open another connection"
    if certfile:
        return ssl.wrap_socket(sock, certfile=certfile, keyfile=keyfile)
    return sock

class SocketError(Exception):
    pass
