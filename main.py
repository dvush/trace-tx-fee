from web3 import Web3
from tabulate import tabulate

import sys
import os

endpoint = os.getenv('ETH_RPC_URL')
w3 = Web3(Web3.HTTPProvider(endpoint))
tracer = open('balance-change-tracer.js').read()

def gp_to_gwei(gas_price):
    if gas_price < 0:
        return -Web3.fromWei(-gas_price, 'gwei')
    else:
        return Web3.fromWei(gas_price, 'gwei')


def show_eff_gas_price(block):
    block_data = w3.eth.get_block(block)
    block_number = block_data.number
    config = {"address": block_data.miner}
    r = w3.provider.make_request('debug_traceBlockByNumber',
                                 [Web3.toHex(block_number), {'tracer': tracer, 'tracerConfig': config}])
    if 'error' in r:
        raise Exception(r['error']['message'])
    balances = [int(x['result']['balance']) for x in r['result']]

    txs = block_data.transactions
    gas_used = []
    base_fee = block_data.baseFeePerGas
    tip = []
    for i in range(len(txs)):
        receipt = w3.eth.get_transaction_receipt(txs[i])
        gas_used.append(receipt.gasUsed)
        tip.append(receipt.effectiveGasPrice - base_fee)

    deltas = []
    current_balance = w3.eth.get_balance(block_data.miner, block_number - 1)
    for i in range(len(txs)):
        deltas.append(balances[i] - current_balance)
        current_balance = balances[i]

    eff_gp = []
    for i in range(len(txs)):
        eff_gp.append(deltas[i] / gas_used[i])

    table = []
    for i in range(len(txs)):
        table.append([Web3.toHex(txs[i]), gp_to_gwei(eff_gp[i]), gp_to_gwei(tip[i]), deltas[i], gas_used[i]])
    print(tabulate(table, ["tx hash", "effective gas price (gwei)", "tip (gwei)", "coinbase delta", "gas used"]))


if __name__ == '__main__':
    block = sys.argv[1]
    if block.isnumeric():
        block = int(block)
    show_eff_gas_price(block)
