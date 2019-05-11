import os
import unittest
from unittest import mock


class FdToSocketTestCase(unittest.TestCase):
    def test_blank(self):
        from waitress_systemd import fds_to_sockets

        with mock.patch.dict(os.environ, {"LISTEN_FDS": ""}):
            self.assertRaises(ValueError, fds_to_sockets, False)

    def test_zero(self):
        from waitress_systemd import fds_to_sockets

        with mock.patch.dict(os.environ, {"LISTEN_FDS": "0"}):
            ret = fds_to_sockets(False)
        self.assertListEqual(ret, [])
