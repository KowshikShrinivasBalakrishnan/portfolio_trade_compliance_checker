# Portfolio Trade Compliance Checker

## Description

The **Portfolio Trade Compliance Checker** is a Python application that checks proposed buy and sell orders against portfolio-specific compliance rules. It produces a clear decision—**Approved**, **Rejected**, or **Needs Manual Sign-off**—and stores the results in a CSV file.

## Features

- Validates trade quantity, price, and action.
- Rejects trades involving restricted securities.
- Checks whether sufficient cash or holdings are available.
- Calculates post-trade position concentration.
- Updates portfolio balances and holdings for approved trades.
- Generates a detailed trade decision report.

## Project Files

| File | Purpose |
|---|---|
| `main.py` | Main application logic |
| `portfolio_data.json` | Portfolio balances and compliance rules |
| `trades.csv` | Proposed trade orders |
| `trade_results.csv` | Trade decisions and reasons |


## Compliance Workflow

1. Load portfolio and trade data.
2. Validate quantity, price, and trade action.
3. Check restricted securities.
4. Verify sell quantities and buy affordability.
5. Calculate position concentration for buy orders.
6. Approve, reject, or request manual sign-off.
7. Update portfolio holdings and save results.

## Decision Rules

| Condition | Decision |
|---|---|
| Invalid quantity, price, or action | Rejected |
| Restricted security | Rejected |
| Insufficient holdings for a sell | Rejected |
| Insufficient cash for a buy | Rejected |
| Position exceeds portfolio limit | Needs Manual Sign-off |
| All checks passed | Approved |

## Technologies Used

- Python 3
- CSV module
- JSON module
- No external libraries required

## How to Run

```bash
python main.py
```

The application reads `trades.csv` and `portfolio_data.json`, then writes the decisions to `trade_results.csv`.

## Output

The output includes:

- Trade decision
- Reason for approval or rejection
- Final portfolio cash balance
- Final security holdings

## Conclusion

This project provides a simple, automated trade compliance and execution workflow for managing multiple portfolios. It helps ensure that proposed trades satisfy basic financial controls before execution.
