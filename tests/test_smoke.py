import helpdesk


def test_package_imports_and_has_version() -> None:
    assert isinstance(helpdesk.__version__, str)
    assert helpdesk.__version__ == "0.1.0"
