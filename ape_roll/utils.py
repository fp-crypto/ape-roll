import eth_abi
from hexbytes import HexBytes

def eth_abi_encode_single(param: str, arg) -> HexBytes:
    start = 0
    if eth_abi.grammar.parse(param).is_dynamic:
        start = 32

    return HexBytes(eth_abi.encode([param], [arg]))[start:]
