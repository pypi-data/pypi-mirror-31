# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
import os

import yaml
from google.protobuf.json_format import Parse

from qrl.core import config
from qrl.core.Block import Block
from qrl.core.Singleton import Singleton
from qrl.generated import qrl_pb2


class GenesisBlock(Block, metaclass=Singleton):
    def __init__(self):
        package_directory = os.path.dirname(os.path.abspath(__file__))
        genesis_data_path = os.path.join(package_directory, 'genesis.json')

        with open(genesis_data_path) as f:
            genesisBlock_json = f.read()
            tmp_block = qrl_pb2.Block()
            Parse(genesisBlock_json, tmp_block)
            super(GenesisBlock, self).__init__(tmp_block)

        # Override genesis if yaml is available (integration testing, etc)
        genesis_config_path = os.path.join(config.user.qrl_dir, 'genesis.yml')
        if os.path.isfile(genesis_config_path):
            with open(genesis_config_path) as f:
                additional_balances = yaml.safe_load(f)
                if additional_balances is not None:
                    new_items = [qrl_pb2.GenesisBalance(address=k, balance=v)
                                 for k, v in additional_balances['genesis_info'].items()]
                    self._data.genesis_balance.extend(new_items)
        self.blockheader._data.timestamp_seconds = config.dev.genesis_timestamp

    @property
    def transactions(self):
        return self._data.transactions

    @property
    def genesis_balance(self):
        return self._data.genesis_balance
