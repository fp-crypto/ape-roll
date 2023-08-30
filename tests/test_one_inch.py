from ape import Contract, accounts, convert
import pytest
from ape_roll import WeirollPlanner
import requests


@pytest.mark.skip("FIXME: update 1inch api")
def test_one_inch(weiroll_vm):
    whale = accounts["0x57757E3D981446D585Af0D9Ae4d7DF6D64647806"]
    weth = Contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    crv = Contract("0xD533a949740bb3306d119CC777fa900bA034cd52")
    one_inch = Contract("0x1111111254fb6c44bAC0beD2854e76F90643097d")

    weth.transfer(weiroll_vm.address, convert("10 ether", int), sender=whale)

    swap_url = "https://api.1inch.io/v4.0/1/swap"
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
    )

    assert r.ok and r.status_code == 200
    tx = r.json()["tx"]

    weth.approve(one_inch, 2 ** 256 - 1, {"from": weiroll_vm, "gas_price": 0})

    decoded = one_inch.decode_input(tx["data"])
    func_name = decoded[0]
    params = decoded[1]

    planner = WeirollPlanner(weiroll_vm)
    planner.call(one_inch, func_name, *params)

    cmds, state = planner.plan()
    weiroll_tx = weiroll_vm.execute(cmds, state, sender=whale)

    assert crv.balanceOf(weiroll_vm) > 0
