
import csv
import json


# --------------------------------------------------
# 1. LOAD PORTFOLIO REFERENCE DATA
# --------------------------------------------------

def load_portfolio_data(filename):

    with open(filename, "r") as file:
        portfolio_data = json.load(file)

    return portfolio_data


# --------------------------------------------------
# 2. LOAD PROPOSED TRADES
# --------------------------------------------------

def load_trades(filename):

    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)
        trades = list(reader)

    # Preserve file order unless trade dates are provided.
    if trades and "trade_date" in trades[0]:

        trades = sorted(
            enumerate(trades),
            key=lambda item: (
                item[1]["trade_date"],
                item[0]
            )
        )

        trades = [trade for _, trade in trades]

    return trades


# --------------------------------------------------
# 3. INITIALIZE EMPTY PORTFOLIO HOLDINGS
# --------------------------------------------------

def initialize_portfolios(portfolio_data):

    for portfolio_id, portfolio in portfolio_data.items():

        portfolio["current_holdings"] = {}

    return portfolio_data


# --------------------------------------------------
# 4. CHECK ONE TRADE AGAINST COMPLIANCE RULES
# --------------------------------------------------

def check_trade(trade, portfolio):

    security_id = trade["security_id"]
    action = trade["action"].strip().capitalize()

    try:

        quantity = float(trade["quantity"])
        price = float(trade["price"])

    except (ValueError, TypeError):

        return "Rejected", "Invalid trade data."

    cash_balance = portfolio["cash_balance"]

    restricted_securities = portfolio["restricted_securities"]

    max_position_pct = portfolio["max_position_pct"]

    current_holdings = portfolio["current_holdings"]


    # --------------------------------------------------
    # STEP 1: VALIDATE TRADE DATA
    # --------------------------------------------------

    if (
        quantity <= 0
        or price <= 0
        or action not in ["Buy", "Sell"]
    ):

        return "Rejected", "Invalid trade data."


    # --------------------------------------------------
    # STEP 2: RESTRICTED SECURITY CHECK
    # --------------------------------------------------

    if security_id in restricted_securities:

        return (
            "Rejected",
            "Security is restricted for this portfolio."
        )


    # --------------------------------------------------
    # STEP 3: SELL CHECK
    # --------------------------------------------------

    if action == "Sell":

        existing_quantity = current_holdings.get(
            security_id, {}
        ).get("quantity", 0)

        if existing_quantity < quantity:

            return (
                "Rejected",
                "Insufficient holdings to sell."
            )


    # --------------------------------------------------
    # STEP 4: BUY AFFORDABILITY CHECK
    # --------------------------------------------------

    if action == "Buy":

        trade_cost = quantity * price

        if trade_cost > cash_balance:

            return (
                "Rejected",
                "Insufficient cash for this buy order."
            )


        # --------------------------------------------------
        # STEP 5: POSITION CONCENTRATION CHECK
        # --------------------------------------------------

        existing_quantity = current_holdings.get(
            security_id, {}
        ).get("quantity", 0)

        value_of_other_holdings = 0

        for holding_security, holding in current_holdings.items():

            if holding_security != security_id:

                value_of_other_holdings += (
                    holding["quantity"]
                    * holding["market_price"]
                )

        post_trade_cash = cash_balance - trade_cost

        post_trade_quantity = existing_quantity + quantity

        post_trade_value = post_trade_quantity * price

        total_portfolio_value = (
            post_trade_cash
            + post_trade_value
            + value_of_other_holdings
        )

        if total_portfolio_value <= 0:

            return (
                "Rejected",
                "Invalid trade data."
            )

        position_pct = (
            post_trade_value / total_portfolio_value
        )

        if position_pct > max_position_pct:

            return (
                "Needs Manual Sign-off",
                "Exceeds maximum position concentration — requires approval."
            )


    # --------------------------------------------------
    # STEP 6: APPROVE THE TRADE
    # --------------------------------------------------

    return (
        "Approved",
        "Trade passed all compliance checks."
    )


# --------------------------------------------------
# 5. UPDATE PORTFOLIO AFTER AN APPROVED TRADE
# --------------------------------------------------

def update_portfolio(trade, portfolio):

    security_id = trade["security_id"]

    action = trade["action"].strip().capitalize()

    quantity = float(trade["quantity"])

    price = float(trade["price"])

    current_holdings = portfolio["current_holdings"]


    # --------------------------------------------------
    # BUY: ADD OR INCREASE HOLDINGS
    # --------------------------------------------------

    if action == "Buy":

        if security_id in current_holdings:

            current_holdings[security_id]["quantity"] += quantity

            current_holdings[security_id]["market_price"] = price

        else:

            current_holdings[security_id] = {

                "quantity": quantity,

                "market_price": price
            }

        # Reduce cash balance

        portfolio["cash_balance"] -= quantity * price


    # --------------------------------------------------
    # SELL: REDUCE OR REMOVE HOLDINGS
    # --------------------------------------------------

    elif action == "Sell":

        existing_quantity = current_holdings[security_id]["quantity"]

        remaining_quantity = existing_quantity - quantity

        if remaining_quantity == 0:

            del current_holdings[security_id]

        else:

            current_holdings[security_id]["quantity"] = remaining_quantity

            current_holdings[security_id]["market_price"] = price

        # Add sale proceeds to cash balance

        portfolio["cash_balance"] += quantity * price


# --------------------------------------------------
# 6. PROCESS ALL PROPOSED TRADES SEQUENTIALLY
# --------------------------------------------------

def process_trades(trades, portfolio_data):

    results = []

    for trade in trades:

        portfolio_id = trade["portfolio_id"]

        # Find the relevant portfolio

        if portfolio_id not in portfolio_data:

            raise ValueError(
                f"Portfolio reference data not found: {portfolio_id}"
            )

        portfolio = portfolio_data[portfolio_id]

        # Check trade against current portfolio state

        decision, reason = check_trade(trade, portfolio)

        # --------------------------------------------------
        # UPDATE HOLDINGS ONLY IF APPROVED
        # --------------------------------------------------

        if decision == "Approved":

            update_portfolio(trade, portfolio)

        # --------------------------------------------------
        # STORE TRADE RESULT
        # --------------------------------------------------

        result = trade.copy()

        result["decision"] = decision

        result["reason"] = reason

        results.append(result)

    return results


# --------------------------------------------------
# 7. SAVE TRADE RESULTS
# --------------------------------------------------

def save_results(results, filename):

    if not results:

        print("No trades to process.")

        return

    fieldnames = list(results[0].keys())

    with open(filename, "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(results)




# --------------------------------------------------
# 8. DISPLAY FINAL PORTFOLIO HOLDINGS
# --------------------------------------------------

def display_portfolios(portfolio_data):

    print("\n========== FINAL PORTFOLIO HOLDINGS ==========")

    for portfolio_id, portfolio in portfolio_data.items():

        print(f"\nPortfolio: {portfolio_id}")

        print(f"Cash Balance: {portfolio['cash_balance']:.2f}")

        holdings = portfolio["current_holdings"]

        if not holdings:

            print("No current holdings.")

        else:

            for security_id, holding in holdings.items():

                print(
                    security_id,
                    "Quantity:", holding["quantity"],
                    "Market Price:", holding["market_price"]
                )


# --------------------------------------------------
# 9. MAIN APPLICATION
# --------------------------------------------------

def main():

    # Load input files

    portfolio_data = load_portfolio_data(
        "portfolio_data.json"
    )

    trades = load_trades(
        "trades.csv"
    )

    # Initialize all portfolios with empty holdings

    portfolio_data = initialize_portfolios(
        portfolio_data
    )

    # Process transactions sequentially

    results = process_trades(
        trades,
        portfolio_data
    )

    # Save trade decisions

    save_results(
        results,
        "trade_results.csv",
        
    )

    # Display individual trade results

    print("\n========== TRADE RESULTS ==========")

    for result in results:

        print(
            result["portfolio_id"],
            result["security_id"],
            result["action"],
            result["decision"],
            result["reason"]
        )

    # Display final portfolio holdings

    display_portfolios(portfolio_data)


if __name__ == "__main__":

    main()
