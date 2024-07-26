#!/bin/bash

# Wallet


python -m generate.get_all_balances

python -m get_query_map

python -m wallet.get_key_dict

python -m wallet.get_key_pair

python -m routes.data_table

python -m routes.total_table