from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gimmegit")
except PackageNotFoundError:
    __version__ = "unknown"
