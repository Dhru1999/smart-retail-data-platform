# Custom exceptions for the ETL pipeline.
class ETLError(Exception):
    """Base class for ETL exceptions."""
    pass


class ExtractError(ETLError):
    pass


class TransformError(ETLError):
    pass


class LoadError(ETLError):
    pass