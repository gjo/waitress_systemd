import os
import socket
import sys
import waitress
from waitress.adjustments import asbool

try:
    from . import raw_socket
except ImportError:
    raw_socket = None


__version__ = "0.1.dev0"

SD_LISTEN_FDS_START = 3
PY37 = sys.version_info[:2] >= (3, 7)
ALLOW_FD_ONLY = PY37 and hasattr(socket, "SO_TYPE")
VAILD_FAMILIES = {socket.AF_INET, socket.AF_INET6}
if hasattr(socket, "AF_UNIX"):
    VAILD_FAMILIES.add(socket.AF_UNIX)


def sd_listen_fds(unset_environment):
    # type: (bool) -> int

    # TODO: check LISTEN_PID
    # TODO: unset envvars
    return int(os.environ["LISTEN_FDS"])


def fd_to_socket(fd, preserve_fd):
    # type: (int, bool) -> socket.socket
    if preserve_fd and ALLOW_FD_ONLY:
        return socket.socket(fileno=fd)

    if raw_socket is None:
        raise Exception("this platform is not supported")

    family = raw_socket.fd_to_family(fd)
    if family not in VAILD_FAMILIES:
        raise ValueError("fd=%d's family is not valid: %d" % (fd, family))

    socktype = raw_socket.fd_to_socktype(fd)
    if socktype != socket.SOCK_STREAM:
        raise ValueError("fd=%d's socktype is not valid: %d" % (fd, socktype))

    ipproto = raw_socket.fd_to_ipproto(fd)

    if preserve_fd:
        sock = socket.socket(family, socktype, ipproto, fd)
    else:
        sock = socket.fromfd(fd, family, socktype, ipproto)
    return sock


def fds_to_sockets(preserve_fd):
    nfds = sd_listen_fds(False)
    sockets = []
    for i in range(nfds):
        fd = i + SD_LISTEN_FDS_START
        sock = fd_to_socket(fd, preserve_fd)
        sock.setblocking(0)
        sockets.append(sock)
    return sockets


def serve(app, **kwargs):
    if asbool(kwargs.pop("use_systemd_socket")):
        preserve_fd = asbool(kwargs.pop("systemd_socket_preserve_fd"))
        sockets = fds_to_sockets(preserve_fd)
        if not sockets:
            raise ValueError("systemd sockets are not passed")
        kwargs["sockets"] = sockets
    waitress.serve(app, **kwargs)


def serve_paste(app, global_config, **kwargs):
    serve(app, **kwargs)
    return 0


def run():
    waitress.runner.run(_serve=serve)
