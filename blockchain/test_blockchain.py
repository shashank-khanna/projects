import unittest

from blockchain import BlockChain


class TestBlockChain(unittest.TestCase):

    def setUp(self):
        self.blockchain = BlockChain()

    def test_get_size(self):
        self.assertEquals(1, self.blockchain.get_size())
        self.blockchain.create_block()
        self.assertEquals(2, self.blockchain.get_size())
