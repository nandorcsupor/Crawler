from ast import Lambda
from urllib import response
from requests import get
from matplotlib import pyplot as plt
from web3 import Web3
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np


API_KEY = "WHNW7X7PNWY539JGQWI95JWYS7ARGX3UEX"

#address = "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae"
address = "0x73bceb1cd57c711feac4224d062b0f6ff338501e"

w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/75f02785108d4a939c6bdaa19a6a42c2'))

# 1 ETH = 10 **18 Wei
ETHER_VALUE = 10 **18


#https://api.etherscan.io/api
   #?module=account
   #&action=balance
   #&address=0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae
   #&tag=latest
   #&apikey=YourApiKeyToken

base_url = "https://api.etherscan.io/api"

def create_api_url(module, action, address, startblock, **kwargs):

    # Get latest block number
    block = w3.eth.get_block('latest')
    latest_block = block["number"]

    url = base_url + f"?module={module}&action={action}&address={address}&apikey={API_KEY}&startblock={startblock}&endblock={latest_block}"
    
    for key, value in kwargs.items():
        url += f"&{key}={value}"

    return url

def get_account_balance(address):
    balance_url = create_api_url("account", "balance", address, tag="latest")
    #print(balance_url)
    response = get(balance_url)
    data = response.json()

    value = int(data["result"]) / ETHER_VALUE
    return value

#eth_balance = get_account_balance(address)
#print(eth_balance)


#https://api.etherscan.io/api
   #?module=account
   #&action=txlist
   #&address=0xddbd2b932c763ba5b1b7ae3b362eac3e8d40121a
   #&startblock=0
   #&endblock=99999999

   #&page=1
   #&offset=10
   #&sort=asc
   #&apikey=YourApiKeyToken'''


#put startblock here too next to address
def get_transactions(address, startblock):

    # Get latest block number
    block = w3.eth.get_block('latest')
    latest_block = block["number"]

    transactions_url = create_api_url("account", "txlist", address, startblock, endblock=latest_block, page=1, offset=10000, sort="asc")
    response = get(transactions_url)

    #List!
    data = response.json()["result"]

    internal_tx_url = create_api_url("account", "txlistinternal", address, startblock, endblock=latest_block, page=1, offset=10000, sort="asc")
    response_2 = get(internal_tx_url)
    data_2 = response_2.json()["result"]

    data.extend(data_2)
    data.sort(key=lambda x: int(x['timeStamp']))

    df = pd.DataFrame(data)
    #print(df)

    st.title(f"Here are the transactions of {address}. from block number: {startblock}")
    st.write(df)

    current_balance = 0
    balances = []
    times = []
    
    for tx in data:
        to = tx["to"]
        from_address = tx["from"]
        value = int(tx["value"]) / ETHER_VALUE
        block_number = tx["blockNumber"]
        #print("-------------------------")
        #print(f"To: {to}")
        #print(f"From: {from_address}")
        #print(f"Value: {value} ETH")
        #print(f"Block Number: {block_number}")


        #Internal transactions do NOT have "gasPrice" key
        if "gasPrice" in tx:
            gas = int(tx["gasUsed"]) * int(tx["gasPrice"]) / ETHER_VALUE
        else:
            gas = int(tx["gasUsed"]) / ETHER_VALUE

        time = datetime.fromtimestamp(int(tx["timeStamp"]))
        
        money_in = to.lower() == address.lower()

        if money_in:
            current_balance += value
        else:
            current_balance -= value + gas

        balances.append(current_balance)
        times.append(time)


    #print(f"Current ETH balance: {current_balance}")

    #plt.plot(times, balances)
    #plt.show()

    st.title("Address balance chart from specified block")
    st.line_chart(balances)

get_transactions(address, 11000000)

# Get last price of ETH - Convert it to USD!!

