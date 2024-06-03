from openai import OpenAI
import csv
import os
import re
import yfinance as yf


def calculate_total_score(
        rec,sen,bus):

    weights = {
        'rec_score' : 0.5,
        'sentiment_score' : 0.25,
        #'technical_score' : 0.2, # already in pre-screen (1. 'price below 20-50-200'SMA and 2. 'RSI < 40')
        'business_score' : 0.25
    }

    # Assert that the weights sum up to 1
    sum_weights = sum(weights.values())
    assert sum_weights == 1, f"The weights do not sum up to 1 ; sum_weights = {sum_weights}"

    total_score = (
            weights['rec_score'] * rec
            + weights['sentiment_score'] * sen
            #+ weights['technical_score'] * technical
            + weights['business_score'] * bus
    )
    return total_score

key = ''
client = OpenAI(
    # This is the default and can be omitted
    api_key=key,
)

def call_GPT(GPT_prompt, model=""):
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": GPT_prompt}],
        stream=True,
    )

    result_text = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            result_text += chunk.choices[0].delta.content

    return result_text.strip()

def extract_sen_bus(string):
    pattern = r"\[([0-9.]+),([0-9.]+)\]"
    match = re.search(pattern, string)

    if match:
        value1, value2 = match.groups()
        value1 = float(value1)
        value2 = float(value2)
        extracted_values = (value1, value2)
    else:
        extracted_values = None

    return extracted_values

def get_company_name(ticker):
    stock = yf.Ticker(ticker)
    company_info = stock.info
    return company_info['longName']

def update_csv(date, ticker, rec_score, filename='total_scores.csv'):
    file_exists = os.path.isfile(filename)

    if file_exists:
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            rows = list(reader)
    else:
        rows = [['Date', 'Ticker', 'Recommendation Score']]  # Initialize with header if file doesn't exist

    updated = False
    for row in rows:
        if row[0] == 'Date':
            continue
        if row[0] == date and row[1] == ticker:
            row[2] = rec_score
            updated = True
            break

    if not updated:
        rows.append([date, ticker, rec_score])

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def extract_ticker_and_scores(filename="recommendation_scores.csv"):
    tickers_and_scores = {}

    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            date, ticker, rec_score = row
            tickers_and_scores[ticker] = float(rec_score)  # Convert rec_score to float

    return tickers_and_scores

#---------- IMPLEMENTATION ----------#

file_name = os.path.join('/Users/stijnvanseveren/PycharmProjects/Stock_Prediction/.venv','recommendation_scores.csv')

tickers = extract_ticker_and_scores(file_name).keys()
rec_scores = extract_ticker_and_scores(file_name).values()

sen_bus_dict = {}
for ticker in tickers:
    company_name = get_company_name(ticker)
    GPT_PROMPT = (
        f"Your task is to analyse two aspects of the company '{company_name}': 1. a general sentiment analysis and 2. a general business analyis."
        "This is how:"
        "Sentiment analysis: Browse the internet to find two very recent articles about the stock. Compute one general sentiment score based on the articles from 1 (negative) to 9 (positive)."
        "Business analysis: As a LLM you have lots of information of standard business plans. Quantify how good the general business plan of this company is from 1 (bad) to 9 (good)."
        "Your only output is in the following format: [X1,X2]"
        "Make sure that is your only output. Just the [] with the two scores inside, seperated by a comma."
        "X1 is the score for the sentiment analysis and X2 is the score for the business analysis.")

    sen_bus_dict[f'{ticker}'] = extract_sen_bus(call_GPT(GPT_prompt=GPT_PROMPT,model='gpt-4o')) # sentiment_score,business_score

sentiment_scores = [scores[0] for scores in sen_bus_dict.values()]
business_scores = [scores[1] for scores in sen_bus_dict.values()]

DATE = '3/06/2024'

for ticker,rec,sen,bus in zip(tickers,rec_scores,sentiment_scores,business_scores):
    total_score = calculate_total_score(rec,sen,bus)
    update_csv(DATE, ticker, total_score)
