from ape import Contract, accounts, convert
from ape_roll.client import WeirollContract, WeirollPlanner


def test_curve_add_liquidity(weiroll_vm):
    whale = accounts["0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643"]
    dai = Contract("0x6B175474E89094C44Da98b954EedeAC495271d0F")
    curve_pool = Contract("0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7")
    three_crv = Contract("0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490")

    # regular way
    assert three_crv.balanceOf(whale) == 0
    dai.approve(curve_pool.address, 2**256 - 1, sender=whale)
    curve_pool.add_liquidity([convert("10 ether", int), 0, 0], 0, sender=whale)
    assert three_crv.balanceOf(whale) > 0

    dai.transfer(weiroll_vm.address, convert("10 ether", int), sender=whale)

    # Weiroll version
    planner = WeirollPlanner(weiroll_vm)

    w_dai = WeirollContract.createContract(dai)
    w_curve_pool = WeirollContract.createContract(curve_pool)

    planner.add(w_dai.approve(w_curve_pool.address, 2**256 - 1))
    w_dai_balance = planner.add(w_dai.balanceOf(weiroll_vm.address))
    planner.add(w_curve_pool.add_liquidity([w_dai_balance, 0, 0], 0))

    cmds, state = planner.plan()
    weiroll_tx = weiroll_vm.execute(cmds, state, sender=whale)

    assert three_crv.balanceOf(weiroll_vm.address) > 0


def test_curve_add_liquidity_with_call(weiroll_vm):
    whale = accounts["0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643"]
    dai = Contract("0x6B175474E89094C44Da98b954EedeAC495271d0F")
    curve_pool = Contract("0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7")
    three_crv = Contract("0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490")

    dai.transfer(weiroll_vm.address, convert("10 ether", int), sender=whale)

    planner = WeirollPlanner(weiroll_vm)
    w_dai = WeirollContract.createContract(dai)
    w_curve_pool = WeirollContract.createContract(curve_pool)
    dai_balance = dai.balanceOf(weiroll_vm.address)

    planner.add(w_dai.approve(w_curve_pool.address, 2**256 - 1))
    planner.call(curve_pool, "add_liquidity", [dai_balance, 0, 0], 0)

    cmds, state = planner.plan()
    weiroll_tx = weiroll_vm.execute(cmds, state, sender=whale)

    assert three_crv.balanceOf(weiroll_vm.address) > 0
