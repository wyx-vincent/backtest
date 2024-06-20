from functools import wraps
import inspect


class AssetClassValidator:
    """
    AssetClassValidator is a utility class for validating asset classes defined by users.
    It provides methods to ensure that asset classes used in the functions are valid and predefined.
    
    Methods:
    --------
    - check_asset_class(asset_class): Static method that raises a ValueError if the asset_class is not predefined.
    - validate_asset_class(func): Static method that acts as a decorator to automatically validate the 'asset_class'
        parameter of any function it decorates.
        This decorator checks both positional and keyword arguments.

    Usage:
    1. Direct validation:
        AssetClassValidator.check_asset_class('equity')  # No error
        AssetClassValidator.check_asset_class('real_estate')  # Raises ValueError

    2. Using as a decorator:
        @AssetClassValidator.validate_asset_class
        def some_method(asset_class):
            pass

        some_method('equity')  # No error
        some_method('real_estate')  # Raises ValueError

    This class helps ensure consistency and correctness for asset classes input.
    """

    allowed_asset_classes = {'cash', 'mmf', 'equity', 'bond', 'option'}

    @staticmethod
    def is_valid_asset_class(asset_class):
        if asset_class not in AssetClassValidator.allowed_asset_classes:
            raise ValueError(f'Asset class {asset_class} is not allowed, please check utils.asset_class_validator.AssetClassValidator')

    @staticmethod
    def validate_asset_class(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'asset_class' in kwargs:
                AssetClassValidator.is_valid_asset_class(kwargs['asset_class'])
            else:
                # If asset_class is a positional argument, find its position
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if 'asset_class' in params:
                    index = params.index('asset_class')
                    asset_class = args[index]
                    AssetClassValidator.is_valid_asset_class(asset_class)
                else:
                    raise ValueError("The function does not have an 'asset_class' parameter.")
            return func(*args, **kwargs)
        return wrapper


def check_date(self, date):
    if self.dates is None:
        raise Exception("dates have not been recorded by record_date function")
    if date not in self.dates:
        raise ValueError(f"The given date {date} does not exist in the backtest period")
    

@staticmethod
def check_positive_quantity(quantity):
    if quantity <= 0:
        raise ValueError('The quantity must be positive')

