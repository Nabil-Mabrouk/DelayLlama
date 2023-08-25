class Indicator:
    def __init__(self, name):
        """
        Initialize an Indicator instance.

        Args:
            name (str): Name of the indicator (e.g., SMA for Simple Moving Average).
        """
        self.name = name

    def calculate_sma(self, data, period):
        """
        Calculate the Simple Moving Average (SMA) indicator.

        Args:
            data (list): Historical data for which to calculate the SMA.
            period (int): The period for calculating the SMA (e.g., 10 for a 10-day SMA).

        Returns:
            list: List of SMA values for the given data.
        """
        sma_values = []
        for i in range(len(data)):
            if i < period - 1:
                sma_values.append(None)  # Not enough data for the initial periods
            else:
                sma = sum(data[i - period + 1:i + 1]) / period
                sma_values.append(sma)
        return sma_values

# Example usage:
# indicator = Indicator("SMA")
# historical_data = [1.23, 1.45, 1.32, 1.55, 1.47, 1.63, 1.75, 1.84, 1.92, 2.05]
# sma_values = indicator.calculate_sma(historical_data, period=5)
# print(sma_values)
