# Algorand Monthly Volumes
Calculate an approximation of the total volume transferred on Algorand during a specific Month

There are 4 steps to calculate the Volume Transferred on Algorand:

1. **Algorand Movements**: Calculate the total ALGO volume transferred in a month and convert it to USD with Coingecko's price feed.
2. **Stablescoins**: Get the volumes in stables currencies. Convert the amounts to ALGO through Vestige API, then convert all to USD with Coingecko's price feed.
3. **HAFN**: Get the HAFN volumes, convert it to USD with yfinance price feed (assuming it is pegged 1:1 with the AFN) and then convert it to ALGO.
4. **Top 10 ASAs**: Get the volumes in their own currency and convert them to ALGO with Vestige API. Then convert to USD with Coingecko's price feed.

With all this steps an overview of the major volumes transferred can be achieved.
