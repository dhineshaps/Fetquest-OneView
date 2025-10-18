import google.generativeai as genai
import streamlit as st

# 🔹 Configure Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash-lite")

@st.cache_data(show_spinner=False)
def get_ai_portfolio_recommendation(
    total_invested,
    total_current_invested_value,
    total_invested_stock,
    total_invested_mf,
    total_invested_gold,
    total_current_amount_stock,
    total_current_amount_mf,
    total_current_amount_gold,
    risk_profile,
    goal
):

    # 🧩 Basic validation
    if not total_current_invested_value or total_current_invested_value <= 0:
        return "❌ Invalid input: total current invested value cannot be zero or negative."

    # 📊 Compute current allocation
    stock_percent_current = (total_current_amount_stock / total_current_invested_value) * 100
    mf_percent_current = (total_current_amount_mf / total_current_invested_value) * 100
    gold_percent_current = (total_current_amount_gold / total_current_invested_value) * 100

    total_percent = stock_percent_current + mf_percent_current + gold_percent_current
    if abs(total_percent - 100) > 1:
        st.warning(f"⚠️ Allocation sums to {total_percent:.2f}%, not 100%. Check your inputs.")

    # 📈 Base assumptions
    stock_return = 12.0     # Equity expected return
    mf_return = 9.0         # Balanced/Hybrid MF
    gold_return = 7.0       # Historical gold return
    inflation = 6.0

    # 📉 Return calculations
    weighted_nominal_return = (
        (stock_percent_current * stock_return)
        + (mf_percent_current * mf_return)
        + (gold_percent_current * gold_return)
    ) / 100
    real_return = weighted_nominal_return - inflation

    # 🧠 AI Prompt
    prompt = f"""
You are a financial planning assistant for an Indian investor.
Evaluate and improve the investor’s asset allocation between Stocks, Gold, and Mutual Funds for a 10-year investment horizon.

### 🧾 Inputs
- Stocks: {stock_percent_current:.2f}%
- Mutual Funds: {mf_percent_current:.2f}%
- Gold: {gold_percent_current:.2f}%
- Weighted Nominal Return: {weighted_nominal_return:.2f}%
- Inflation: {inflation:.2f}%
- Real Return: {real_return:.2f}%
- Risk Profile: {risk_profile}
- Goal: {goal}

### 📊 Assumptions (India, Long-Term)
- Investment Horizon: 10 years  
- Repo Rate: 5.5%  
- Target Real Return: ≥ 4% (≈10% nominal)  
- Stocks / Equity: 11–13%  
- Gold: 6–8%  
- Mutual Funds (Balanced/Hybrid): 8–10%  

---

## 🧮 Tasks
1. Validate allocation (total = 100%, diversification, risk alignment).  
2. Evaluate if real return meets the inflation-adjusted target.  
3. If real return < 4%, recommend a revised allocation.  
4. Suggest an improved mix that fits the user's {risk_profile} profile.  
5. Briefly explain why the suggested mix is better for a 10-year horizon.  
6. Include a 10-year projected wealth estimate if relevant.  

---

## 🧱 Output Format (Use Markdown)
### ✅ Portfolio Validation
**Status:** Valid / Needs Adjustment  
**Diversification:** OK / Needs Rebalancing  

### 📊 Current Allocation
| Asset Class | Current % | Est. Return | Contribution |
|--------------|-----------|-------------|---------------|
| Stocks | {stock_percent_current:.2f}% | 12% | - |
| Mutual Funds | {mf_percent_current:.2f}% | 9% | - |
| Gold | {gold_percent_current:.2f}% | 7% | - |
| **Total** | **{total_percent:.2f}%** |   |   |

**Nominal Return:** {weighted_nominal_return:.2f}%  
**Real Return (after 6% inflation):** {real_return:.2f}%

---

### 🎯 Suggested Allocation (AI)
| Asset Class | Suggested % | Change |
|--------------|--------------|--------|
| Stocks | X% | ↑ / ↓ |
| Mutual Funds | X% | ↑ / ↓ |
| Gold | X% | ↑ / ↓ |

**Projected Nominal Return:** X%  
**Projected Real Return:** X%

---

### 💰 10-Year Growth Estimate
If ₹{total_invested:,.0f} invested at X% CAGR → **≈ ₹Y after 10 years**

---

### 🧠 AI Recommendation Summary
- Why this mix is better  
- How it fits a {risk_profile} investor  
- How it beats inflation and supports goal: *{goal}*  
- Tips: rebalance yearly, monitor inflation, SIP regularly.
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error generating recommendation: {e}"