
import unittest
import logging
import creaturecast_rigging.biped.biped as bpd
import creaturecast_handlers as hdr


class TestNodes(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestNodes, self).__init__(*args, **kwargs)
        self.log = logging.getLogger(self.__class__.__name__)

    def test_node_handler(self):

        self.log.debug('node_test finished')

        def print_it(it):
            print it

        hdr.node_handler.created.connect(print_it)

        node = bpd.BipedTemplate()
        node.create()
