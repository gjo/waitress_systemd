import ctypes
import os
import socket
from ctypes.util import find_library


dll_path = find_library("c")
dll = ctypes.CDLL(dll_path, use_errno=True)


sa_family_t = ctypes.c_ubyte
socklen_t = ctypes.c_uint32


class sockaddr(ctypes.Structure):
    _fields_ = (
        ("sa_len", ctypes.c_ubyte),
        ("sa_family", sa_family_t),
        ("sa_data", ctypes.c_char * 8),
    )


def nonzero_to_raise_errno(result, func, arguments):
    if result:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))


getsockname = dll.getsockname
getsockname.argtypes = (
    ctypes.c_int,  # sockfd
    ctypes.POINTER(sockaddr),  # addr
    ctypes.POINTER(socklen_t),  # addrlen
)
getsockname.restype = ctypes.c_int
getsockname.errcheck = nonzero_to_raise_errno

getsockopt = dll.getsockopt
getsockopt.argtypes = (
    ctypes.c_int,  # sockfd
    ctypes.c_int,  # level
    ctypes.c_int,  # optname
    ctypes.c_void_p,  # optval
    ctypes.POINTER(socklen_t),  # optlen
)
getsockopt.restype = ctypes.c_int
getsockopt.errcheck = nonzero_to_raise_errno


def fd_to_family(fd):
    # type: (int) -> int
    addr = sockaddr(0, 0)
    addrlen = socklen_t(4)
    getsockname(fd, ctypes.byref(addr), ctypes.byref(addrlen))
    family = addr.sa_family.value
    return family


def fd_to_socktype(fd):
    # type: (int) -> int
    optval = ctypes.c_int(0)
    optlen = socklen_t(4)
    getsockopt(
        fd,
        socket.SOL_SOCKET,
        socket.SO_TYPE,
        ctypes.byref(optval),
        ctypes.byref(optlen),
    )
    socktype = optval.value
    return socktype


if hasattr(socket, "SO_PROTOCOL"):

    def fd_to_ipproto(fd):
        # type: (int) -> int
        optval = ctypes.c_int(0)
        optlen = socklen_t(4)
        getsockopt(
            fd,
            socket.SOL_SOCKET,
            socket.SO_PROTOCOL,
            ctypes.byref(optval),
            ctypes.byref(optlen),
        )
        ipproto = optval.value
        return ipproto


else:

    def fd_to_ipproto(fd):
        # type: (int) -> int
        return 0
