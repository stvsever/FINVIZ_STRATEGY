import csv
import os

def calculate_rec_score(
        pe_ratio, price_free_cash_flow, eps_growth_this_year, eps_growth_next_year, debt_equity_ratio,
        operating_margin, net_profit_margin, analyst_recommendations, insider_transactions, institutional_transactions):

    weights = {
        'pe_ratio': 0.25,
        'price_free_cash_flow': 0.05,
        'eps_growth_this_year': 0.05,
        'eps_growth_next_year': 0.1,
        'debt_equity_ratio': 0.125,
        'operating_margin': 0.10,
        'net_profit_margin': 0.10,
        'analyst_recommendations': 0.125,
        'insider_transactions': 0.05,
        'institutional_transactions': 0.05
    }

    # Assert that the weights sum up to 1
    sum_weights = sum(weights.values())
    assert sum_weights == 1, f"The weights do not sum up to 1 ; sum_weights = {sum_weights}"

    rec_score = (
            weights['pe_ratio'] * pe_ratio + weights['price_free_cash_flow'] * price_free_cash_flow +
            weights['eps_growth_this_year'] * eps_growth_this_year + weights[
                'eps_growth_next_year'] * eps_growth_next_year +
            weights['debt_equity_ratio'] * debt_equity_ratio + weights['operating_margin'] * operating_margin +
            weights['net_profit_margin'] * net_profit_margin + weights[
                'analyst_recommendations'] * analyst_recommendations +
            weights['insider_transactions'] * insider_transactions + weights[
                'institutional_transactions'] * institutional_transactions
    )
    return rec_score

def update_csv(date, ticker, rec_score, filename='recommendation_scores.csv'):
    # Check if the file exists
    file_exists = os.path.isfile(filename)

    # Read the existing data if the file exists
    if file_exists:
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            rows = list(reader)
    else:
        rows = [['Date', 'Ticker', 'Recommendation Score']]  # Initialize with header if file doesn't exist

    # Update the existing data or add new data
    updated = False
    for row in rows:
        if row[0] == 'Date':  # Skip header
            continue
        if row[0] == date and row[1] == ticker:
            row[2] = rec_score
            updated = True
            break

    if not updated:
        rows.append([date, ticker, rec_score])

    # Write the data back to the CSV file
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

#---------- IMPLEMENTATION ----------#

DATE = '3/06/2024'
TICKER = 'TSLA'
STOCK_VALUES = {
        'pe_ratio': 5,
        'price_free_cash_flow': 2,
        'eps_growth_this_year': 1,
        'eps_growth_next_year': 1,
        'debt_equity_ratio': 5,
        'operating_margin': 2,
        'net_profit_margin': 2,
        'analyst_recommendations': 6,
        'insider_transactions': 2,
        'institutional_transactions': 4
    } # manueel invoeren voor elke stock ; ZIE USER-STEPS ; kopieer dus die GPT-prompt en voeg voor elke stock een foto toe met de respectievelijk finviz informatie.

COPYTHIS_PROMPT = ("Your task is to generate one python dictionary with following structure: {'pe_ratio' : X, 'price_free_cash_flow' : X, 'eps_growth_this_year' : X, 'eps_growth_next_year' : X, 'debt_equity_ratio' : X, 'operating_margin' : X, 'net_profit_margin' : X, 'analyst_recommendations' : X, 'insider_transactions' : X, 'institutional_transactions' : X}."
                   "I will upload an image with raw stock information. Extract the information that is needed to complete the dictionary.") # voeg hier de foto (screenshot) aan toe


# Calculate recommendation score
rec_score = round(calculate_rec_score(
    STOCK_VALUES['pe_ratio'], STOCK_VALUES['price_free_cash_flow'], STOCK_VALUES['eps_growth_this_year'],
    STOCK_VALUES['eps_growth_next_year'], STOCK_VALUES['debt_equity_ratio'], STOCK_VALUES['operating_margin'],
    STOCK_VALUES['net_profit_margin'], STOCK_VALUES['analyst_recommendations'], STOCK_VALUES['insider_transactions'],
    STOCK_VALUES['institutional_transactions']
),3)

# Update the CSV file with the new data
update_csv(DATE, TICKER, rec_score)

print(f"Recommendation score for {TICKER} on {DATE} saved to recommendation_scores.csv")
print(f"rec_score is '{rec_score}'")
