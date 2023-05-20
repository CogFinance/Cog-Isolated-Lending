# @version 0.3.7

# @author tinkermaster-overspark

event PairCreated:
    asset: indexed(address)
    collateral: indexed(address)
    pair: indexed(address)


medium_blueprint: immutable(address)


@external
def __init__(_medium_blueprint: address):
    """
    Initialize the contract
    """
    medium_blueprint = _medium_blueprint


@external
def deploy_medium_risk_pair(
    asset: address, collateral: address, oracle: address
) -> address:
    """
    Deploy a medium risk pair
    """
    pair: address = create_from_blueprint(
        medium_blueprint, asset, collateral, oracle, code_offset=3
    )
    log PairCreated(asset, collateral, pair)
    return pair
