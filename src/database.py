from deta import Deta
import streamlit as st

class Database:
    def __init__(self):
        """
        Initialize a Database instance to interact with an SQL database.

        Args:
            db_url (str): The database URL. Defaults to SQLite in-memory database.
        """
        ## connect to the Deta collection
        self.deta=Deta(st.secrets["deta_key"])

        ## create or get the references to the tables
        self.tables={}
        self.tables["data"]={}

        ## These tables keep tracks of the a list of tables on Deta as this list can not be fetched otherwise
        self.tables["assets"]=self.deta.Base("assets") #[data={"asset_name", "asset_description"}, key="symbol"]
        self.tables["indicators"]=self.deta.Base("indicators") #[data={"indicator_name", "indicator_description"}, key="symbol"]
        self.tables["timeframes"]=self.deta.Base("timeframes") #[data={"timeframe_name", "value in ms"}, key="symbol"]

        # For each asset/timeframe pair we will create a table and add it to self.tables["data"]["BTC"]["1h"]
        assets = self.deta.Base("assets").fetch().items
        timeframes=self.deta.Base("timeframes").fetch().items
        for asset in assets:
            _asset=asset["key"]
            self.tables["data"][_asset]={}
            for timeframe in timeframes:
                _timeframe=timeframe["key"]
                self.tables["data"][_asset][_timeframe]={}
                db_name=_asset+"_"+_timeframe
                self.tables["data"][_asset][_timeframe]=self.deta.Base(db_name)



    def db(self, name):
        return self.deta.Base(name)


    def get_available_indicators(self):
        """
        Retrieve the names of available indicators.

        Returns:
            list: List of indicator names.
        """
        return self.db("indicators_list_db").fetch().items


    def retrieve_indicator_data(self, asset, indicator_name):
        """
        Retrieve historical indicator data from the database.

        Args:
            indicator_name (str): Name of the indicator.

        Returns:
            list: Historical data for the specified indicator.
        """
        _data=self.db[asset].fetch({"column?equal":"indicator_name"})

        # convert to a dataframe and return
        #self.disconnect()
        data=[1, 2, 3,4,5]
        return data
    
    def save_recommendation(self, recommendation):
        pass

# Example usage:
# database = Database()  # Initialize the database instance
# available_indicators = database.get_available_indicators()
# indicator_data = database.retrieve_indicator_data(indicator_name)
