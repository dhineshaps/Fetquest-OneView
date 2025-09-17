import requests
import pandas as pd
import datetime as dt

class MutualFund:
    def __init__(self, scheme_code: str):
        self.scheme_code = scheme_code
        self._data = None  # cache NAV history

    def history(self) -> pd.DataFrame:
        """
        Fetch full NAV history from MFAPI and return as DataFrame
        """
        if self._data is None:
            url = f"https://api.mfapi.in/mf/{self.scheme_code}"
            resp = requests.get(url)
            json_data = resp.json()
            
            # Extract NAV history
            navs = []
            for d in json_data["data"]:
                navs.append({
                    "Date": pd.to_datetime(d["date"], format="%d-%m-%Y"),
                    "NAV": float(d["nav"])
                })
            
            df = pd.DataFrame(navs).sort_values("Date").reset_index(drop=True)
            self._data = df
        
        return self._data

    def latest_nav(self) -> float:
        """
        Get the most recent NAV
        """
        df = self.history()
        return df.iloc[-1]["NAV"]

    def cagr(self, years: int = None) -> float:
        """
        Calculate CAGR using full history or a given number of years
        """
        df = self.history()
        start_nav = df.iloc[0]["NAV"] if years is None else df[df["Date"] >= (df["Date"].max() - pd.DateOffset(years=years))].iloc[0]["NAV"]
        end_nav = df.iloc[-1]["NAV"]
        duration_years = (df.iloc[-1]["Date"] - df.iloc[0]["Date"]).days / 365 if years is None else years

        return (end_nav / start_nav) ** (1/duration_years) - 1

    def xirr(self, cashflows: list, dates: list) -> float:
        """
        Compute XIRR given list of cashflows (negative for investment, positive for redemption/value)
        and their corresponding dates (datetime.date)
        """
        days = [(d - dates[0]).days/365 for d in dates]

        def f(rate):
            return sum([cf / (1+rate)**t for cf, t in zip(cashflows, days)])

        rate = 0.1
        for _ in range(100):  # Newton-Raphson method
            f_val = f(rate)
            f_der = sum([-t*cf / (1+rate)**(t+1) for cf, t in zip(cashflows, days)])
            if f_der == 0:
                break
            rate -= f_val/f_der
        return rate
