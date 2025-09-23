import numpy as np
from pandas import to_datetime
from scipy.interpolate import CubicHermiteSpline


class InterestRateCurve:
    def __init__(self, name, date, rates):
        """
        Initialize the InterestRate object.

        Parameters:
        - name: Name of the interest rate curve (string).
        - date: Date of the curve (string or datetime).
        - rates: Dictionary of rates with keys as periods (e.g., "3M", "6M") and values as rates.
        """
        self.name = name
        self.date = to_datetime(date)
        self.rates = rates
        self.periods = {
            "3M": 0.25, "6M": 0.5, "1Y": 1,
            "3Y": 3, "5Y": 5, "7Y": 7, "10Y": 10, "30Y": 30
        }

    def get_rate(self, period):
        """
        Get the interest rate for a specific period.

        Parameters:
        - period: The period to retrieve (e.g., "3M", "1Y").

        Returns:
        - The interest rate for the period.
        """
        return self.rates.get(period, None)

    def interpolate_rate(self, target_year):
        """
        Interpolate the rate for a specific year using Hermite interpolation.

        Parameters:
        - target_year: The year for which to interpolate the rate.

        Returns:
        - Interpolated rate for the target year.
        """
        years = np.array([self.periods[key] for key in self.rates.keys()])
        rates = np.array(list(self.rates.values()))
        derivatives = np.gradient(rates, years)

        interpolator = CubicHermiteSpline(years, rates, derivatives)
        return interpolator(target_year)/100

    def get_spot_rate(self, days):
        """
        Get the spot rate for a specific number of days.

        Parameters:
        - days: Number of days to calculate the spot rate for.

        Returns:
        - Spot rate (annualized) for the given days.
        """

        days = min(180,days)
        target_year = days / 365.0
        return self.interpolate_rate(target_year)


if __name__ == "__main__":
    # Example usage
    curve_name = "Example Curve"
    date = "2024-11-14"
    rates = {
        "3M": 2.1413,
        "6M": 2.3566,
        "1Y": 2.9027,
        "3Y": 3.1902,
        "5Y": 3.3600,
        "7Y": 3.5500,
        "10Y": 3.5508,
        "30Y": 4.1402,
    }

    interest_rate_curve = InterestRateCurve(curve_name, date, rates)
    print("439-day spot rate:", interest_rate_curve.get_spot_rate(439))
    print("653-day spot rate:", interest_rate_curve.get_spot_rate(653))
    print("801-day spot rate:", interest_rate_curve.get_spot_rate(801))
    print("1171-day spot rate:", interest_rate_curve.get_spot_rate(1171))
