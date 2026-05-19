import pytest

pytest_plugins = [
    "fixtures.auth",
    "fixtures.character",
]


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: быстрые проверки что API отвечает")
    config.addinivalue_line("markers", "regression: детальные проверки бизнес-логики")
    config.addinivalue_line("markers", "integration: тесты с реальным API DnD Shop")
