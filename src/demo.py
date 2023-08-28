import streamlit as st
from assistant import Assistant, Model
from user import User
from database import Database
import requests, time
import pandas as pd

class DemoApp:
    def __init__(self, assistant, database):
        """
        Initialize the DemoApp instance.

        Args:
            assistant (Assistant): The assistant instance.
            database (Database): The database instance.
        """
        self.assistant = assistant
        self.database = database
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
            st.info("Examples:\n - How is the market today?\n - Did you notice any double-bottom pattern?")
            #st.image("https://static.streamlit.io/examples/cat.jpg", width=200)

        with self.tab2:
            st.header("Docs")

            doc="""
            #### Market Data collection storage:
            These operations are performed periodically (using celery-beat)
            - Crypto currencies prices scrapped an stored in a Deta Base
            - Indicator calculated at each new value
            - News scrapped from the web and stored 
            - Financial annoucement scrapped and stored
            
            #### User request processing:
            - User enters a question
            - Large language model has the following prompt:\n
            <sys>You are an expert in technical analysis with deep knowledge of cryptocurrencies market. I will ask you questions
             about the crypto market, price dynamics prediction. In order to help you answer my question with up to date data i 
             will provide you with a pandas dataframe containing the klines at different timestamps of different crypto asets.
             Here is a description of the dataframe:\n
             = DATAFRAME DESCRIPTION =

             Here is the metadata of the dataframe:\n
             = METADATA =

             When i ask you a question you must follow a step by step thinking process as follows:
             - Do i need any data to answer the question
             - if yes, can this data be calculated from the dataframe
             - if yes write a python code to extract or calculate the data that you require.
            You answer should be exclusively a python code.\n
            </sys>
            <instruct> USER_QUESTION </instruct>

            <OUTPUT: python code>

            #### Code execution

            The python code is executed and the result is passed to the language model along with the user question.
            """
            st.write(doc)


            #st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

        with self.tab3:
            st.header("About")
            st.info("- Contact: Nabil MABROUK\n - Email: nabil.mabrouk.ai@gmail.com\n - Twitter: @ai-qube")
            #st.image("https://static.streamlit.io/examples/owl.jpg", width=200)

        with self.tab4:
            st.header("log")
            
    
    def update_market_date(self):
        # Define the endpoint and parameters
        endpoint = 'https://api.binance.com/api/v1/klines'
        currency="USDT"

        # list of assets
        self.tab4.write("Supported assets: BTC, ETH, XRP")
        self.database.tables["assets"].put(data={"asset_name": "bitcoin", "asset_description":"First cryptocurrency"}, key="BTC") 
        self.database.tables["assets"].put(data={"asset_name": "etherum", "asset_description":"Second cryptocurrency"}, key="ETH") 
        self.database.tables["assets"].put(data={"asset_name": "ripple", "asset_description":"Third cryptocurrency"}, key="XRP") 

        # list of timeFrames
        self.tab4.write("Suported timeframe:1h, 4h, 1d")
        self.database.tables["timeframes"].put(data={"timeframe_name":"1h", "value in min":60}, key="1h")
        self.database.tables["timeframes"].put(data={"timeframe_name":"4h", "value in min":240}, key="4h")
        self.database.tables["timeframes"].put(data={"timeframe_name":"1d", "value in min":1440}, key="1d")

        # list of indicators
        self.tab4.write("Suported technical indicators: None")
        #self.tables["indicators"]=self.database.deta.Base("indicators") #[data={"indicator_name", "indicator_description"}, key="symbol"]

        self.tab4.write(f"... Connecting to endpoint : {endpoint}")

        #loop over assets and timeframe
        assets = self.database.tables["assets"].fetch().items
        timeframes=self.database.tables["timeframes"].fetch().items
        for asset in assets:
            for timeframe in timeframes:
                _asset=asset["key"]
                _timeframe=timeframe["key"]
                db_name=_asset+"_"+_timeframe
                self.database.tables["data"][_asset][_timeframe]=self.database.deta.Base(db_name)

                # scrap market data
                symbol = _asset+currency
                interval = _timeframe  # 1-hour candles
                limit = 100  # Number of data points to retrieve

                params = {
                    'symbol': symbol,
                    'interval': interval,
                    'limit': limit,
                }
                self.tab4.write(f".... Scrapping market data for : {symbol} and timeframe : {interval}")
                # Make the API request
                response = requests.get(endpoint, params=params)
                data = response.json()

                # Convert the data to a Pandas DataFrame
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                time.sleep(0.5)
                for index, row in df.iterrows():
                    entry={"open":float(row["open"]), 
                           "high":float(row["high"]), 
                           "low":float(row["low"]), 
                           "close":float(row["close"]), 
                           "volume":float(row["volume"])}
                    key=str(row["timestamp"])
                    try:
                        self.database.tables["data"][_asset][_timeframe].put(data=entry, key=key)
                    except Exception as e:
                        self.tab4.error(str(e))

                self.tab4.write(f".... Data added to table {db_name}")


    def handle_user_interactions(self):
        """
        Handle user interactions within the demo.
        """
        # User enters a query
        user_query = self.tab1.text_input("Enter your question below:")
        if self.tab1.button("Ask"):
            if user_query:
                assistant_response = self.assistant.process_user_queries(user_query)
                self.tab1.write(f"Assistant: {assistant_response}")
            else:
                self.tab1.warning("Please enter a query before asking.")

    def present_data(self):
        """
        Present data and visualizations to the user.
        """
        st.header("Data and Visualizations")

        # Retrieve and display the scrapped data
        st.subheader("Market data")
        asset_symbol = st.selectbox(
            "Select an asset",
            self.database.tables["assets"].fetch().items
        )


        if not asset_symbol:
            st.warning("No data available for the selected asset")
        else:
            data=self.database.tables["data"][asset_symbol["key"]]['1h'].fetch("close")
            st.line_chart(data)

    def get_user_preferences(self):
        """
        Get user preferences from the user interface.

        Returns:
            dict: User preferences.
        """
        user_preferences = {}

        user_preferences["risk_tolerance"] = st.sidebar.selectbox(
            "Risk Tolerance",
            ("Low", "Medium", "High")
        )

        user_preferences["favorite_crypto"] = st.sidebar.text_input(
            "Favorite Cryptocurrency"
        )

        return user_preferences

    def run_demo_scenario(self):
        """
        Run a scripted demo scenario for the presentation.
        """
        self.initialize_ui()
        self.handle_user_interactions()
        self.update_market_date()
        self.present_data()
    

if __name__=="__main__":
    model = Model("llama")
    assistant = Assistant(model)
    database = Database()
    user = User(username="Trader")
    demo_app = DemoApp(assistant, database)
    demo_app.run_demo_scenario()




# Example usage:
# demo_app = DemoApp()
# demo_app.initialize_ui()
# demo_app.handle_user_interactions(user, assistant, database)
# demo_app.present_data(database)

