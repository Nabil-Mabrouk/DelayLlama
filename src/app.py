import requests
import pandas as pd
import builtins  # Access to a limited set of built-in functions
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
import streamlit as st
import os, time
import json

models = {
    'Llama2-7b-chat': {
        'USER_ID': 'meta',
        'APP_ID': 'Llama-2',
        'MODEL_ID': 'Llama2-7b-chat',
        'MODEL_VERSION_ID': 'e52af5d6bc22445aa7a6761f327f7129'
    },
    'Llama2-13b-chat': {
        'USER_ID': 'meta',
        'APP_ID': 'Llama-2',
        'MODEL_ID': 'llama2-13b-chat',
        'MODEL_VERSION_ID': '79a1af31aa8249a99602fc05687e8f40'
    },
    'Llama2-70b-chat': {
        'USER_ID': 'meta',
        'APP_ID': 'Llama-2',
        'MODEL_ID': 'llama2-70b-chat',
        'MODEL_VERSION_ID': '6c27e86364ba461d98de95cddc559cb3'
    },
    'Llama2-70b-alternative': {
        'USER_ID': 'clarifai',
        'APP_ID': 'ml',
        'MODEL_ID': 'llama2-70b-alternative',
        'MODEL_VERSION_ID': '75a64576ad664768b828f1047acdae30'
    },
    'GPT-3': {
        'USER_ID': 'openai',
        'APP_ID': 'chat-completion',
        'MODEL_ID': 'GPT-3_5-turbo',
        'MODEL_VERSION_ID': '8ea3880d08a74dc0b39500b99dfaa376'
    },
    'GPT-4': {
        'USER_ID': 'openai',
        'APP_ID': 'chat-completion',
        'MODEL_ID': 'GPT-4',
        'MODEL_VERSION_ID': 'ad16eda6ac054796bf9f348ab6733c72'
    }
}


def fetch_market_data(symbol, interval, limit):
    # Define the endpoint and parameters
    endpoint = 'https://api.binance.com/api/v1/klines'
    symbol = symbol + 'USDT'

    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit,
    }

    # Make the API request
    response = requests.get(endpoint, params=params)
    data = response.json()

    # Convert the data to a Pandas DataFrame
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Select and convert columns to floats
    df = df[['timestamp', 'open', 'close', 'high', 'low', 'volume']].astype({'open': float, 'close': float, 'high': float, 'low': float, 'volume': float})

    return df

def add_technical_indicators(df, config=None):
    if config is None:
        config = {
            'short_window': 50,
            'long_window': 200,
            'rsi_window': 14,
            'pivot_points': False,
            'bollinger_bands': False
        }

    # Calculate Short-term Simple Moving Average (SMA)
    df['SMA_short'] = df['close'].rolling(window=config['short_window'], min_periods=1).mean()

    # Calculate Long-term Simple Moving Average (SMA)
    df['SMA_long'] = df['close'].rolling(window=config['long_window'], min_periods=1).mean()

    # Calculate Short-term Exponential Moving Average (EMA)
    df['EMA_short'] = df['close'].ewm(span=config['short_window'], adjust=False).mean()

    # Calculate Long-term Exponential Moving Average (EMA)
    df['EMA_long'] = df['close'].ewm(span=config['long_window'], adjust=False).mean()

    # Calculate Relative Strength Index (RSI)
    delta = df['close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=config['rsi_window'], min_periods=1).mean()
    avg_loss = loss.rolling(window=config['rsi_window'], min_periods=1).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Calculate variations in percent
    df['Close_Variation'] = df['close'].pct_change() * 100
    df['Volume_Variation'] = df['volume'].pct_change() * 100

    # Calculate volatility as the standard deviation of close price returns
    df['Volatility'] = df['Close_Variation'].rolling(window=config['short_window'], min_periods=1).std()

    # Calculate Pivot Points
    if config['pivot_points']:
        df['Pivot_Points'] = (df['high'] + df['low'] + df['close']) / 3

    # Calculate Bollinger Bands
    if config['bollinger_bands']:
        std_dev = df['close'].rolling(window=config['short_window'], min_periods=1).std()
        df['Bollinger_Bands_Upper'] = df['SMA_short'] + (std_dev * 2)
        df['Bollinger_Bands_Lower'] = df['SMA_short'] - (std_dev * 2)

    return df

def fetch_crypto_news(auth_token, currencies):
    """
    Fetch cryptocurrency news from the CryptoPanic API.

    Parameters:
    - auth_token (str): Your CryptoPanic API authentication token.
    - currencies (str): Comma-separated list of currencies to filter news by (e.g., 'BTC,ETH').

    Returns:
    - news_data (dict): A dictionary containing the JSON response from the API.

    Example:
    ```
    auth_token = '69ea4fb639103ff45e9121adab53df3afbad1439'  # Your CryptoPanic API token
    currencies = 'BTC,ETH'  # Example: Fetch news for Bitcoin and Ethereum
    news_data = fetch_crypto_news(auth_token, currencies)
    ```
    """
    time.sleep(30)
    # Construct the API URL
    api_url = f'https://cryptopanic.com/api/v1/posts/?auth_token={auth_token}&currencies={currencies}'

    try:
        # Make the API request
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception if there's an error

        # Parse the JSON response
        news_data = response.json()
        return news_data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def fetch_news(news_data):

    # Initialize lists to store extracted information
    titles = []
    published_dates = []
    currency_codes = []

    # Extract information from the 'results' list
    results = news_data.get('results', [])  # Get the list of news items
    for news_item in results:
        title = news_item.get('title', '')  # Get the 'title' field
        published_at = news_item.get('published_at', '')  # Get the 'published_at' field
        currencies = news_item.get('currencies', [])  # Get the list of currencies

        # Extract currency codes from the list of currencies
        currency_codes_list = [currency.get('code', '') for currency in currencies]

        # Append the extracted information to the respective lists
        titles.append(title)
        published_dates.append(published_at)
        currency_codes.append(currency_codes_list)

    # Now, 'titles', 'published_dates', and 'currency_codes' lists contain the extracted information.

    # Create a dictionary to store DataFrames for each currency
    currency_dataframes = {}

    # Iterate through the extracted data and create DataFrames
    for currency_code_list, title, published_date in zip(currency_codes, titles, published_dates):
        for currency_code in currency_code_list:
            # Check if a DataFrame already exists for this currency
            if currency_code not in currency_dataframes:
                # Create a new DataFrame for the currency
                currency_dataframes[currency_code] = pd.DataFrame(columns=['timestamp', 'news title', 'sentiment'])

            # Append a new row to the DataFrame for the currency
            new_record = pd.DataFrame([{'timestamp': published_date, 'news title': title, 'sentiment': None}])

            currency_dataframes[currency_code] = pd.concat([currency_dataframes[currency_code], new_record], ignore_index=True)

    # Now, 'currency_dataframes' is a dictionary where each key represents a currency code, and each value is a DataFrame
    # with columns 'timestamp', 'news title', and 'sentiment'.            
    return currency_dataframes

def describe_dataframe(df):
    # Get basic statistics using the 'describe()' method
    stats = df.describe()

    # Get column data types
    data_types = df.dtypes

    # Get the number of missing values per column
    missing_values = df.isnull().sum()

    # Get the number of unique values per column
    unique_values = df.nunique()

    # Create a description string
    description = "DataFrame Description:\n"
    description += f"Number of Rows: {len(df)}\n"
    description += f"Number of Columns: {len(df.columns)}\n\n"

    # Append column-specific information
    for column in df.columns:
        description += f"Column: {column}\n"
        description += f"  Data Type: {data_types[column]}\n"
        #description += f"  Missing Values: {missing_values[column]}\n"
        #description += f"  Unique Values: {unique_values[column]}\n"
        #description += f"  {stats.loc['mean', column]:.2f} (mean)\n"
        #description += f"  {stats.loc['std', column]:.2f} (std)\n"
        description += f"  {stats.loc['min', column]:.2f} (min)\n"
        #description += f"  {stats.loc['25%', column]:.2f} (25%)\n"
        #description += f"  {stats.loc['50%', column]:.2f} (50% - median)\n"
        #description += f"  {stats.loc['75%', column]:.2f} (75%)\n"
        description += f"  {stats.loc['max', column]:.2f} (max)\n\n"

    return description

def describe_dataframe_2(df):
    stats = df.describe()
    answer = f"\nThe dataframe name is df.\n" 
    answer += f"It contains BTC-USDT open/close/high/low/volume from \n"
    answer += f"{stats.loc['min', 'timestamp']} to {stats.loc['max', 'timestamp']} with and interval of '1h' \n"
    answer += f"It also a number technical indicator\n"
    answer += f"len(df) = {len(df)}\n"
    answer += f"len(df.columns) = {len(df.columns)}\n"
    answer += f"df.columns = {df.columns}\n\n"
    return answer

def generatePrompt(question, description):
    prompt=f" You are a helpful market analyst and an excellent python programmer.\n"
    prompt+=f"You will be provided with the description of a pandas dataset containing cryptocurrencies market data.\n"
    prompt+=f"I will ask you a question about the crypto market. You must proceed step by step by applying the following thinking process:\n"
    prompt+=f"1- Do you need any data to answer my question\n"
    prompt+=f"2- Can this data be calculated or extracted from the cryptocurrrencies market dataframe\n"
    prompt+=f"3- If yes, write the python code that allow the extraction and calculation of the data that you need.\n"
    prompt+=f"4- Answer only with the python code. Do not add anything to your answer. Only python code.\n\n"

    prompt+=f"Following the pandas dataset description: {description}\n"

    prompt+=f"Following my question: {question}\n"

    prompt+=f"Your answer (python code only): "
   
    return prompt

def execute(method_code, df):
    # Create a restricted namespace (dictionary) with limited built-in functions
    restricted_namespace = {
        'dataframe': df,
        'pd': pd,
        'builtins': builtins  # Provide limited access to built-in functions
    }
    try:
        # Execute the method using the exec() function within the restricted namespace
        exec(method_code, restricted_namespace)
    
        # Call the method and store the result
        method_result = restricted_namespace['sample_method'](restricted_namespace['dataframe'])

        # Print the result
        print(method_result)
    except Exception as e:
        print(f"Error: {e}")

class Model():
    '''
        <s> - the beginning of the entire sequence.
        <<SYS>> - the beginning of the system message.
        <</SYS>> - the end of the system message.
        [INST] - the beginning of some instructions
        [/INST] - the end of the instructions
    '''
    def __init__(self, model):
        self.model=model
    
    def run(self, query):
        # Your PAT (Personal Access Token) can be found in the portal under Authentification
        PAT = os.environ.get('CLARIFAI_PAT') 

        if not PAT:  # If PAT is not set via environment variable
            try:
                PAT = st.secrets['CLARIFAI_PAT']
                #PAT= os.environ.get("CLARIFAI_PAT")
            except KeyError:
                st.error("Failed to retrieve the Clarifai Personal Access Token!")
                PAT = None
        # Specify the correct user_id/app_id pairings
        # Since you're making inferences outside your app's scope
        USER_ID = self.model['USER_ID']
        APP_ID = self.model['APP_ID']
        # Change these to whatever model and text URL you want to use
        MODEL_ID = self.model['MODEL_ID']
        MODEL_VERSION_ID = self.model['MODEL_VERSION_ID']


        channel = ClarifaiChannel.get_grpc_channel()
        stub = service_pb2_grpc.V2Stub(channel)

        metadata = (('authorization', 'Key ' + PAT),)

        userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

        post_model_outputs_response = stub.PostModelOutputs(
            service_pb2.PostModelOutputsRequest(
                user_app_id=userDataObject,  # The userDataObject is created in the overview and is required when using a PAT
                model_id=MODEL_ID,
                version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(
                            text=resources_pb2.Text(
                                raw=query
                            )
                        )
                    )
                ]
            ),
            metadata=metadata
        )
        if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
            print(post_model_outputs_response.status)
            raise Exception(f"Post model outputs failed, status: {post_model_outputs_response.status.description}")

        # Since we have one input, one output will exist here
        output = post_model_outputs_response.outputs[0]
        return output.data.text.raw

class Demo():
    def __init__(self, df):
        self.df = df
        self.model = None
        self.user_interface = None

    def initialize_ui(self):
        """
        Initialize the user interface for the demo.
        """
        st.title("D-Llama")
        presentation='''Chat with the cryptocurrencies market. Ask for market summary, 
        news about you favorite asset, trading recomandations as if you have a professional 
        technical analyst working for you'''
        st.info(presentation)
        self.tab1, self.tab2, self.tab3, self.tab4= st.tabs(["Home", "Docs", "About", "log"])

        with self.tab1:
            st.header("Chat with the market")
            st.info("Examples:\n - What's the outlook for Bitcoin in the coming week?\n - Did you notice any double-bottom pattern?")
            #st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
            # Add the model selection dropdown
            selected_model_name = st.selectbox("Select Model:", list(models.keys()))
            self.model = models[selected_model_name]

        with self.tab2:
            st.header("Docs")

            doc="""
            #### Market Data collection storage:
            These operations are performed periodically (Market data is fetched at the initialisation for the demo)
            - Crypto currencies prices scrapped an stored in a dataframe (or in Deta Base)
            - Indicator calculated 
            - News scrapped from the web and stored for each crypto in a separate dataframe

            #### User request processing:
            - User enters a question
            - The app will proceed following these steps:
            
            1- ask llm: What data do i need to answer this question
            2- ask llm: to Write a python code for a method that takes a dataframe of open/close/high/low/volume and return the required data
            3- extract and run the code
            4- ask llm, using the calculated data as context to answer the user question
            """
            st.write(doc)


            #st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

        with self.tab3:
            st.header("About")
            st.info("- Contact: Nabil MABROUK\n - Email: nabil.mabrouk.ai@gmail.com\n - Twitter: @ai-qube")
            #st.image("https://static.streamlit.io/examples/owl.jpg", width=200)

        with self.tab4:
            st.header("log")

    def handle_user_interactions(self):

        # User enters a query
        user_query = self.tab1.text_input("Enter your question below:")

        # generation a description of the market data dataframe
        #description = describe_dataframe_2(self.df)

        # generate the prompt
        #prompt= generatePrompt(user_query, description)



        if self.tab1.button("Ask"):
            if user_query:
                prompt1=f"I will ask you a question about the cryptocurrencies market. Suppose you have access to up to date market data last 1000 candles (open, close, high, loaw and volume) at timeframe (1h, 4h, 1d)\n"
                prompt1+=f"Can you tell me what is the minimal list of data that you require to answer my question.\n"
                prompt1+=f"Keep you answer short and in bullet format. no disclaimer. no introductory sentence. Bullet list only. My question is: {user_query}"
                self.tab1.info(f"Prompt: {prompt1}")
                model = Model(self.model)
                llama_response = model.run(prompt1)
                self.tab1.write(f"D-Llama: {llama_response}")
                prompt2=f"I have a dataframe with 1000 row of 1h timeframe bitcoin open, low, high, close, and volume. You must provide a python code for a method that takes the dataframe as sole arguments and returns the following data: {llama_response}. Do not explain your answer. do not give example of usage. Provide your answer in markdwon code. You must answer with the python code only"
                self.tab1.info(f"Prompt: {prompt2}")
                model = Model(self.model)
                llama_response = model.run(prompt2)
                self.tab1.write(f"D-Llama: {llama_response}")
            else:
                self.tab1.warning("Please enter a query before asking.")

    def run_demo_scenario(self):
        self.initialize_ui()
        self.handle_user_interactions()


if __name__=="__main__":

    # get market data
    df = fetch_market_data(symbol="BTC", interval='1h', limit=1000)

    # calculate technical indicators
    df= add_technical_indicators(df, config=None)

    # fectch market news and save them to dataframes
    #auth_token = '69ea4fb639103ff45e9121adab53df3afbad1439'
    #raw=fetch_crypto_news(auth_token, 'BTC')
    #print(raw)
    #news=fetch_news(raw)


    demo=Demo(df)
    demo.run_demo_scenario()

