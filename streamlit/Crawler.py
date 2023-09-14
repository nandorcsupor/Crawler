from requests import get
from web3 import Web3
from datetime import datetime
import streamlit as st
import pandas as pd

API_KEY = "WHNW7X7PNWY539JGQWI95JWYS7ARGX3UEX"
address = "0x73bceb1cd57c711feac4224d062b0f6ff338501e"
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/75f02785108d4a939c6bdaa19a6a42c2'))
ETHER_VALUE = 10 ** 18
base_url = "https://api.etherscan.io/api"

def create_api_url(module, action, address, startblock, **kwargs):
    block = w3.eth.get_block('latest')
    latest_block = block["number"]
    url = base_url + f"?module={module}&action={action}&address={address}&apikey={API_KEY}&startblock={startblock}&endblock={latest_block}"
    
    for key, value in kwargs.items():
        url += f"&{key}={value}"
    return url

def get_transactions(address, startblock):
    block = w3.eth.get_block('latest')
    latest_block = block["number"]

    transactions_url = create_api_url("account", "txlist", address, startblock, endblock=latest_block, page=1, offset=10000, sort="asc")
    data = get(transactions_url).json()["result"]

    internal_tx_url = create_api_url("account", "txlistinternal", address, startblock, endblock=latest_block, page=1, offset=10000, sort="asc")
    data_2 = get(internal_tx_url).json()["result"]

    data.extend(data_2)
    data.sort(key=lambda x: int(x['timeStamp']))

    for tx in data:
        tx["value"] = int(tx["value"]) / ETHER_VALUE  # Convert to ETH
        if "gasPrice" in tx:
            tx["gasPrice"] = int(tx["gasPrice"]) / ETHER_VALUE  # Convert to ETH

    df = pd.DataFrame(data)
    st.title(f"Here are the transactions of {address}. from block number: {startblock}")
    st.write(df)

    current_balance = 0
    balances = []
    times = []
    
    for tx in data:
        to = tx["to"]
        value = tx["value"]
        money_in = to.lower() == address.lower()
        gas = int(tx["gasUsed"]) * tx.get("gasPrice", 1)
        time = datetime.fromtimestamp(int(tx["timeStamp"]))
        
        if money_in:
            current_balance += value
        else:
            current_balance -= value + gas
        balances.append(current_balance)
        times.append(time)

    st.title("Address balance chart from specified block")
    st.line_chart(balances)

get_transactions(address, 1000000)
