import pytest
from ape import networks

@pytest.fixture(scope="module", autouse=True)
def mainnet_fork():
    with networks.ethereum.mainnet_fork.use_provider("foundry"):
        yield
