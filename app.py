import streamlit as st
from src.assistant import Assistant, Model
from src.user import User
from src.database import Database

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
        st.title("Cryptocurrency Correlation Vocal Assistant Demo")

    def handle_user_interactions(self):
        """
        Handle user interactions within the demo.
        """
        st.header("User Interaction")

        # User enters a query
        user_query = st.text_input("Ask the Assistant:")
        if st.button("Ask"):
            if user_query:
                assistant_response = self.assistant.process_user_queries(user_query)
                st.write(f"Assistant: {assistant_response}")

                # Simulate generating a recommendation based on user preferences
                user_preferences = self.get_user_preferences()
                recommendation = self.assistant.generate_recommendation(user_preferences)
                st.write(f"Recommendation: {recommendation}")

                # Save the recommendation to the database
                self.database.save_recommendation(recommendation)
            else:
                st.warning("Please enter a query before asking.")

    def present_data(self):
        """
        Present data and visualizations to the user.
        """
        st.header("Data and Visualizations")

        # Retrieve and display historical indicator data from the database
        st.subheader("Historical Indicator Data")
        indicator_name = st.selectbox(
            "Select Indicator",
            self.database.get_available_indicators()
        )

        indicator_data = self.database.retrieve_indicator_data(indicator_name)

        if not indicator_data:
            st.warning("No data available for the selected indicator.")
        else:
            st.line_chart(indicator_data)

    def get_user_preferences(self):
        """
        Get user preferences from the user interface.

        Returns:
            dict: User preferences.
        """
        user_preferences = {}

        user_preferences["risk_tolerance"] = st.selectbox(
            "Risk Tolerance",
            ("Low", "Medium", "High")
        )

        user_preferences["favorite_crypto"] = st.text_input(
            "Favorite Cryptocurrency"
        )

        return user_preferences

    def run_demo_scenario(self):
        """
        Run a scripted demo scenario for the presentation.
        """
        self.initialize_ui()
        self.handle_user_interactions()
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

