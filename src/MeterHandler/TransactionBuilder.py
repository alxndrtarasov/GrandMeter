import base64
from datetime import datetime, date

from iroha import Iroha, IrohaGrpc
from iroha import IrohaCrypto, primitive_pb2
import binascii
import json

agent_role = "agent"


def get_full_acc(name, domain):
    return name + "@" + domain


class TransactionBuilder(object):

    def __init__(self, admin_account, admin_private_key, port):
        self.admin_account = admin_account
        self.admin_private_key = admin_private_key
        self.port = port
        self.iroha = Iroha(self.admin_account)
        self.net = IrohaGrpc(self.port)

    def __send_transaction_and_print_status(self, transaction):
        hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
        print('Transaction hash = {}, creator = {}'.format(
            hex_hash, transaction.payload.reduced_payload.creator_account_id))
        self.net.send_tx(transaction)
        for status in self.net.tx_status_stream(transaction):
            print(status)
        for status in self.net.tx_status_stream(transaction):
            if status == ('COMMITTED', 5, 0):
                return "COMMITTED"

    def create_client(self, client_name):
        user_private_key = IrohaCrypto.private_key()
        user_public_key = IrohaCrypto.derive_public_key(user_private_key)
        commands = [
            self.iroha.command('CreateAccount', account_name=client_name, domain_id="test",
                               public_key=user_public_key),
        ]
        transaction = self.iroha.transaction(commands)
        IrohaCrypto.sign_transaction(transaction, self.admin_private_key)
        self.__send_transaction_and_print_status(transaction)
        tx = self.iroha.transaction([
            self.iroha.command('GrantPermission', account_id='admin@test',
                               permission=primitive_pb2.can_set_my_account_detail)
        ])
        IrohaCrypto.sign_transaction(tx, user_private_key)
        if self.__send_transaction_and_print_status(transaction) == "COMMITTED":
            return "Your key: " + user_private_key, 201
        else:
            return 'Internal Error', 500

    def add_coin_to_client(self, number, private_key):
        tx = self.iroha.transaction([
            self.iroha.command('AddAssetQuantity',
                               asset_id='coin#test', amount=str(number) + '.00')
        ])
        IrohaCrypto.sign_transaction(tx, private_key)
        if self.__send_transaction_and_print_status(tx) == "COMMITTED":
            return "Added " + str(number), 201
        else:
            return 'Internal Error', 500

    
