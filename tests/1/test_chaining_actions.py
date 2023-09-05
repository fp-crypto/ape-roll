from ape import Contract, accounts, convert
import pytest
from hexbytes import HexBytes
from ape_roll.client import WeirollContract, WeirollPlanner, ReturnValue
import requests
import os

ONE_INCH_API_KEY = (
    os.environ["ONE_INCH_API_KEY"] if "ONE_INCH_API_KEY" in os.environ else None
)


@pytest.mark.skipif(ONE_INCH_API_KEY is None, reason="Need 1inch api key")
def test_chaining_action(weiroll_vm, tuple_helper):
    whale = accounts["0x57757E3D981446D585Af0D9Ae4d7DF6D64647806"]
    weth = Contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    yfi = Contract("0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e")
    crv_yfi_weth = Contract("0x29059568bB40344487d62f7450E78b8E6C74e0e5")
    curve_swap = Contract("0xC26b89A667578ec7b3f11b2F98d6Fd15C07C54ba")

    # Check initial setup and send 10 eth to start the process
    assert weth.balanceOf(weiroll_vm.address) == 0
    assert yfi.balanceOf(weiroll_vm.address) == 0
    assert crv_yfi_weth.balanceOf(weiroll_vm.address) == 0
    weth.transfer(weiroll_vm.address, convert("10 ether", int), sender=whale)

    # Planner and all weiroll contracts
    planner = WeirollPlanner(weiroll_vm)
    w_weth = WeirollContract.createContract(weth)
    w_yfi = WeirollContract.createContract(yfi)
    w_tuple_helper = WeirollContract.createContract(tuple_helper)
    w_curve_swap = WeirollContract.createContract(curve_swap)
    w_crv_yfi_weth = WeirollContract.createContract(crv_yfi_weth)

    # One inch section, eth->yfi
    swap_url = f"https://api.1inch.dev/swap/v5.2/1/swap"
    headers = {"Authorization": f"Bearer {ONE_INCH_API_KEY}"}
    r = requests.get(
        swap_url,
        params={
            "fromTokenAddress": weth.address,
            "toTokenAddress": yfi.address,
            "amount": convert("5 ether", int),
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
    w_one_inch = WeirollContract.createContract(one_inch)

    decoded = one_inch.decode_input(HexBytes(tx["data"]))
    func_name = decoded[0]
    params = decoded[1]

    planner.add(w_weth.approve(one_inch.address, 2 ** 256 - 1))
    one_inch_ret = planner.add(w_one_inch.swap(*params.values()).rawValue())

    # Since one inch's swap returns a tuple, we need to do an additional
    # action with the tuple helper contract to extract the amount value
    # in index 0.
    one_inch_amount = planner.add(w_tuple_helper.getElement(one_inch_ret, 0))
    yfi_int_amount = ReturnValue("uint256", one_inch_amount.command)

    # Now that we have the yfi amount, let's do curve logic
    planner.add(w_weth.approve(w_curve_swap.address, 2 ** 256 - 1))
    planner.add(w_yfi.approve(w_curve_swap.address, 2 ** 256 - 1))

    curve_ret = planner.add(
        w_curve_swap.add_liquidity([convert("5 ether", int), yfi_int_amount], 0)
    )

    planner.add(w_crv_yfi_weth.transfer(w_tuple_helper.address, curve_ret))

    cmds, state = planner.plan()
    weiroll_tx = weiroll_vm.execute(cmds, state, sender=whale)

    assert crv_yfi_weth.balanceOf(w_tuple_helper.address) > 0
