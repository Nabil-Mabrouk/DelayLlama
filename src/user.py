class User:
    def __init__(self, username):
        """
        Initialize a User instance.

        Args:
            username (str): The username of the user.
        """
        self.username = username
        self.preferences = {}  # Dictionary to store user preferences

    def customize_preferences(self, preferences):
        """
        Customize user preferences.

        Args:
            preferences (dict): User preferences to set or update.
        """
        # Update user preferences with the provided preferences
        self.preferences.update(preferences)

    def get_preference(self, preference_name):
        """
        Get a specific user preference.

        Args:
            preference_name (str): The name of the preference to retrieve.

        Returns:
            Any: The value of the specified preference.
        """
        return self.preferences.get(preference_name)

# Example usage:
# user = User("JohnDoe")
# user_preferences = {
#     "risk_tolerance": "medium",
#     "favorite_crypto": "BTC",
#     "preferred_timeframe": "1h"
# }
# user.customize_preferences(user_preferences)
# risk_tolerance = user.get_preference("risk_tolerance")
# print(risk_tolerance)
