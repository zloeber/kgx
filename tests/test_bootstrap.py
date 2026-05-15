import importlib.metadata


def test_package_version_defined():
    import kgx

    assert hasattr(kgx, "__version__")
    assert isinstance(kgx.__version__, str)
    assert importlib.metadata.version("kgx") == kgx.__version__
