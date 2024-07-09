import os
import json
from collections import defaultdict
from web3 import Web3

# Directly define BASE_RPC_URL
BASE_RPC_URL = '<ENTER_YOUR_RPC_URL_HERE>'

# Initialize Web3 client
w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))

# Define the contract address and ABI (Application Binary Interface)
contract_address = "0x56b10bf5e47c8262569f3119dfb4be457795c8a2"
checksum_address = w3.to_checksum_address(contract_address)

# Convert the emoji to hex
def to_hex(value):
    return value.encode('utf-8').hex()

# Compute the event signature
event_signature = w3.keccak(text="Spend(address,address,bytes,uint256)").hex()

# Convert the emoji to its hexadecimal representation
emoji_hex = to_hex("🐈")

# Function to convert HexBytes to int
def hex_to_int(hex_bytes):
    return int(hex_bytes.hex(), 16)

# Addresses to exclude from the summary
excluded_addresses = {
    "0x819080e280cf8e3aadf4270e0ca88bd9f7c26f7c": "possible farming bot",
    "0x454685dec7796c2c747294f7aa7a30b2c5ab05f7": "virtual alaska"
}

async def run():
    try:
        print(f"Connecting to {BASE_RPC_URL}")
        if w3.is_connected():
            print("Connected to Ethereum node.")
        else:
            print("Failed to connect to Ethereum node.")
            return

        print(f"Fetching logs for contract: {checksum_address}")
        print(f"Using event signature: {event_signature}")
        print(f"Using emoji hex: {emoji_hex}")

        logs = w3.eth.get_logs({
            'address': checksum_address,
            'fromBlock': 'earliest',
            'toBlock': 'latest',
            'topics': [
                event_signature,
                None,
                None,
                w3.keccak(hexstr=emoji_hex).hex()
            ]
        })

        if logs:
            print(f"Fetched {len(logs)} logs.")
            
            detailed_logs = []
            summary = defaultdict(int)

            for log in logs:
                log_data = {
                    'address': log['address'],
                    'blockHash': log['blockHash'].hex(),
                    'blockNumber': log['blockNumber'],
                    'data': hex_to_int(log['data']),
                    'logIndex': log['logIndex'],
                    'removed': log['removed'],
                    'topics': [topic.hex() for topic in log['topics']],
                    'transactionHash': log['transactionHash'].hex(),
                    'transactionIndex': log['transactionIndex']
                }

                # Extract the relevant parts from the topics
                from_address = '0x' + log_data['topics'][1][26:]
                amount = log_data['data']  # Assuming 'data' field contains the amount

                # Label excluded addresses
                if from_address in excluded_addresses:
                    log_data['label'] = excluded_addresses[from_address]
                else:
                    # Aggregate the amount for each from address
                    summary[from_address] += amount

                detailed_logs.append(log_data)

            # Save the detailed logs to a new JSON file
            with open('./detailed_purr.json', 'w') as f:
                json.dump(detailed_logs, f, indent=4)

            # Save the summary to a new JSON file
            summary_list = [{'from': address, 'floaties_sent': amount} for address, amount in summary.items()]
            with open('./summary_purr.json', 'w') as f:
                json.dump(summary_list, f, indent=4)

            print("Detailed logs have been written to detailed_purr.json")
            print("Summary has been written to summary_purr.json")
        else:
            print("No logs found for the given criteria.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(run())