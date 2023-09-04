import json
from web3 import Web3
from solc import compile_standard
# web3.py instance
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
def deploy_contract(contract_interface):
    # Instantiate and deploy contract
    contract = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
    )
    # Get transaction hash from deployed contract
    tx_hash =contract.deploy(transaction={'from':w3.eth.accounts[1]})
    # Get tx receipt to get contract address
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return tx_receipt['contractAddress']

compiled_code = compile_standard({
    'language': 'Solidity',
    'sources': {'user.sol':{'urls':["/Users/ram/College/cpp/Draft2/MedRec/MedRecV1/src/user.sol"]}},
    'settings':  {
        'outputSelection': {
                               "*": {
                                   "*": [
                                       "metadata", "evm.bytecode" # Enable the metadata and bytecode outputs of every single contract.
                                       , "evm.bytecode.sourceMap" # Enable the source map output of every single contract.
                                   ],
                                   "": [
                                       "ast" #Enable the AST output of every single file.
                                   ]
                               }
        }
    }
},allow_paths="/Users/ram/College/cpp/Draft2/MedRec/MedRecV1/src")

print(compiled_code)
bytecode = compiled_code['contracts']['user.sol']['userRecords']['evm']['bytecode']['object']
abi = json.loads(compiled_code['contracts']['user.sol']['userRecords']['metadata'])['output']['abi']

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.eth.defaultAccount = w3.eth.accounts[0]
userRecords = w3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = userRecords.constructor().transact()
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

# contract = w3.eth.contract(
#      address=tx_receipt.contractAddress,
#      abi=abi
# )

# add abi(application binary interface) and transaction receipt in json file
with open('data.json', 'w') as outfile:
    data = {
        "abi": abi,
        "contract_address": tx_receipt.contractAddress
    }
    json.dump(data, outfile, indent=4, sort_keys=True)