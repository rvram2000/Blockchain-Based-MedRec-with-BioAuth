import json
from web3 import Web3
# web3.py instance
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.eth.defaultAccount = w3.eth.accounts[1]
# Get stored abi and contract_address
with open("data.json", 'r') as f:
    datastore = json.load(f)
    abi = datastore["abi"]
    contract_address = datastore["contract_address"]
contract = w3.eth.contract(address=contract_address, abi=abi)
contract.functions.setUser(
    "Ram","male"
).transact()
user_data = contract.functions.getUser().call()

print(user_data)