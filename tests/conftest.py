import pytest
from ape_roll.client import WeirollContract
from ape import project, networks


@pytest.fixture(scope="session")
def alice(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def weiroll_vm(alice):
    vm = alice.deploy(project.TestableVM)
    yield vm


@pytest.fixture(scope="module")
def math(alice):
    math = alice.deploy(project.Math)
    yield WeirollContract.createLibrary(math)


@pytest.fixture(scope="module")
def testContract(alice):
    brownie_contract = alice.deploy(project.TestContract)
    yield WeirollContract.createLibrary(brownie_contract)


@pytest.fixture(scope="module")
def strings(alice):
    strings_brownie = alice.deploy(project.Strings)
    yield WeirollContract.createLibrary(strings_brownie)


@pytest.fixture(scope="module")
def subplanContract(alice):
    brownie_contract = alice.deploy(project.TestSubplan)
    yield WeirollContract.createLibrary(brownie_contract)


@pytest.fixture(scope="module")
def multiSubplanContract(alice):
    brownie_contract = alice.deploy(project.TestMultiSubplan)
    yield WeirollContract.createLibrary(brownie_contract)


@pytest.fixture(scope="module")
def badSubplanContract(alice):
    brownie_contract = alice.deploy(project.TestBadSubplan)
    yield WeirollContract.createLibrary(brownie_contract)


@pytest.fixture(scope="module")
def multiStateSubplanContract(alice):
    brownie_contract = alice.deploy(project.TestMultiStateSubplan)
    yield WeirollContract.createLibrary(brownie_contract)


@pytest.fixture(scope="module")
def readonlySubplanContract(alice):
    brownie_contract = alice.deploy(project.TestReadonlySubplan)
    yield WeirollContract.createLibrary(brownie_contract)


@pytest.fixture(scope="module")
def tuple_helper(alice):
    yield alice.deploy(project.TupleHelper)


@pytest.fixture(scope="module")
def tuple_helper_yul(alice):
    yield alice.deploy(project.TupleHelperYul)


@pytest.fixture(scope="module")
def tuple_helper_vy(alice):
    yield alice.deploy(project.TupleHelperVy)

@pytest.fixture(scope="module")
def mainnet_fork():
    with networks.ethereum.mainnet_fork.use_provider("foundry"):
        yield
