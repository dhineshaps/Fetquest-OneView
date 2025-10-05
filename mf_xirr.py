import pandas as pd
import numpy_financial as npf
from datetime import datetime

# 📝 Sample transaction data
data = [
    {"type": "buy",  "date": "2020-01-01", "amount": 1000, "units": 100},
    {"type": "buy",  "date": "2021-01-01", "amount": 1000, "units": 80},
    {"type": "sell", "date": "2023-01-01", "amount": 2500, "units": 180}
]

df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

print(df)

# 🧾 Build cashflows for XIRR
cashflows = []
dates = []


for _, row in df.iterrows():
    amt = -row['amount'] if row['type'] == 'buy' else row['amount']
    cashflows.append(amt)
    dates.append(row['date'])
    print(amt)

from datetime import datetime

def xnpv(rate, cashflows, dates):
    """Net present value for irregular cashflows"""
    if rate <= -1:
        return float('inf')
    d0 = dates[0]
    return sum([
        cf / (1 + rate) ** ((d - d0).days / 365)
        for cf, d in zip(cashflows, dates)
    ])

def xirr(cashflows, dates, guess=0.1):
    """XIRR using Newton's method"""
    tol = 1e-6
    max_iter = 100
    rate = guess
    for _ in range(max_iter):
        f = xnpv(rate, cashflows, dates)
        f_deriv = (xnpv(rate + tol, cashflows, dates) - f) / tol
        new_rate = rate - f / f_deriv
        if abs(new_rate - rate) < tol:
            return new_rate
        rate = new_rate
    return rate



xirr_value = xirr(cashflows, dates)
print(f"XIRR: {xirr_value*100:.2f}%")