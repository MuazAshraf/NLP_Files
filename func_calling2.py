import openai
import json
import requests

openai.api_key = ''

def get_stock_price(symbol):
    """Get the current stock price for a given symbol"""
    API_KEY = 'YO52A1M2CCU746NH'
    BASE_URL = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey={}"
    response = requests.get(BASE_URL.format(symbol, API_KEY))
    data = response.json()
    return json.dumps(data)

def run_conversation():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[{"role": "user", "content": "What's the stock price for Apple?"}],
        functions=[
            {
                "name": "get_stock_price",
                "description": "Get the current stock price for a given symbol",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "The stock symbol, e.g. AAPL for Apple",
                        }
                    },
                    "required": ["symbol"],
                },
            }
        ],
        function_call="auto",
    )

    message = response["choices"][0]["message"]

    if message.get("function_call"):
        function_name = message["function_call"]["name"]

        function_response = get_stock_price(symbol=message.get("symbol"))

        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "user", "content": "What is the stock price for Apple?"},
                message,
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                },
            ],
        )
        return second_response

print(run_conversation())
