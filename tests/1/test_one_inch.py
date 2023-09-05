from ape import Contract, accounts, convert
from hexbytes import HexBytes
from ape_roll import WeirollPlanner
import pytest
import os
import requests

ONE_INCH_API_KEY = (
    os.environ["ONE_INCH_API_KEY"] if "ONE_INCH_API_KEY" in os.environ else None
)


@pytest.mark.skipif(ONE_INCH_API_KEY is None, reason="Need 1inch api key")
def test_one_inch(weiroll_vm):
    whale = accounts["0x57757E3D981446D585Af0D9Ae4d7DF6D64647806"]
    weth = Contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    crv = Contract("0xD533a949740bb3306d119CC777fa900bA034cd52")

    weth.transfer(weiroll_vm.address, convert("10 ether", int), sender=whale)

    swap_url = f"https://api.1inch.dev/swap/v5.2/1/swap"
    headers = {"Authorization": f"Bearer {ONE_INCH_API_KEY}"}
    r = requests.get(
        swap_url,
        params={
            "fromTokenAddress": weth.address,
            "toTokenAddress": crv.address,
            "amount": convert("10 ether", int),
            "fromAddress": weiroll_vm.address,
            "slippage": 5,
            "disableEstimate": "true",
            "allowPartialFill": "false",
        },
        headers=headers,
    )

    assert r.ok and r.status_code == 200
    tx = r.json()["tx"]
    one_inch = Contract(tx["to"])

    weth.approve(one_inch, 2 ** 256 - 1, sender=weiroll_vm)

    decoded = one_inch.decode_input(HexBytes(tx["data"]))
    func_name = decoded[0]
    params = decoded[1]

    planner = WeirollPlanner(weiroll_vm)
    planner.call(one_inch, func_name, *params.values())

    cmds, state = planner.plan()
    weiroll_tx = weiroll_vm.execute(cmds, state, sender=whale)

    assert crv.balanceOf(weiroll_vm) > 0
