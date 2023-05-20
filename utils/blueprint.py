from ape import project
from ape.logging import logger
import sys

# GateSeals are deployed using Vyper's `create_from_blueprint`
# GateSeal blueprint is EIP5202-compliant bytecode
# https://eips.ethereum.org/EIPS/eip-5202

EIP_5202_EXECUTION_HALT_BYTE = bytes.fromhex("fe")
EIP_5202_BLUEPRINT_IDENTIFIER_BYTE = bytes.fromhex("71")
EIP_5202_VERSION_BYTE = bytes.fromhex("00")

# Bytecode preamble is not deployed on-chain
# To properly deploy a blueprint contract, special deploy bytecode must be used.
# The following preamble, prepended to regular deploy bytecode (output of vyper -f bytecode),
# should deploy the blueprint in an ordinary contract creation transaction.
# For more details: https://docs.vyperlang.org/en/stable/built-in-functions.html#create_from_blueprint
# To check the deploy bytecode, run vyper -f blueprint_bytecode contracts/GateSeal.vy

# OPERATIONS
# deploy_preamble = "61" + bytecode len in 2 bytes + "3d81600a3d39f3"
# 61  PUSH2 BYTECODE_LENGTH_2_BYTES: STACK 
# 3D  RETURNDATASIZE
# 81  DUP2
# 60  PUSH1 0x0a
# 3D  RETURNDATASIZE
# 39  CODECOPY 
# F3  *RETURN
DEPLOY_PREAMBLE_BYTE_LENGTH = 10
DEPLOY_PREAMBLE_INITIAL_BYTE = bytes.fromhex("61")
DEPLOY_PREABLE_POST_LENGTH_BYTES = bytes.fromhex("3d81600a3d39f3")


def construct_blueprint_deploy_bytecode(initial_gateseal_bytecode: str):
    eip_5202_bytecode = (
        EIP_5202_EXECUTION_HALT_BYTE
        + EIP_5202_BLUEPRINT_IDENTIFIER_BYTE
        + EIP_5202_VERSION_BYTE
        + bytes.fromhex(initial_gateseal_bytecode[2:])
    )

    with_deploy_preamble = (
        DEPLOY_PREAMBLE_INITIAL_BYTE
        + bytes.fromhex(len(eip_5202_bytecode).to_bytes(2, "big").hex())
        + DEPLOY_PREABLE_POST_LENGTH_BYTES
        + eip_5202_bytecode
    )

    return with_deploy_preamble


def verify_blueprint_deploy_preamble(blueprint_deploy_bytecode):
    assert blueprint_deploy_bytecode[0] == int(DEPLOY_PREAMBLE_INITIAL_BYTE.hex(), 16)
    assert int(blueprint_deploy_bytecode[1:3].hex(), 16) == int(
        len(blueprint_deploy_bytecode[DEPLOY_PREAMBLE_BYTE_LENGTH:])
        .to_bytes(2, "big")
        .hex(),
        16,
    )
    assert (
        blueprint_deploy_bytecode[3:DEPLOY_PREAMBLE_BYTE_LENGTH].hex()
        == DEPLOY_PREABLE_POST_LENGTH_BYTES.hex()
    )

    verify_eip522_blueprint(blueprint_deploy_bytecode[DEPLOY_PREAMBLE_BYTE_LENGTH:])


def verify_eip522_blueprint(bytecode):
    assert bytecode[0] == int(EIP_5202_EXECUTION_HALT_BYTE.hex(), 16)
    assert bytecode[1] == int(EIP_5202_BLUEPRINT_IDENTIFIER_BYTE.hex(), 16)
    assert bytecode[2] == int(EIP_5202_VERSION_BYTE.hex(), 16)

    n_length_bytes = bytecode[2] & 0b11
    assert n_length_bytes != 0b11, "reserved bits are set, not an EIP5202 preamble"


def deploy_blueprint(deployer, deploy_code, prompt=False):
    transaction = project.provider.network.ecosystem.create_transaction(
        chain_id=project.provider.chain_id,
        data=deploy_code,
        gas_price=project.provider.gas_price,
        nonce=deployer.nonce,
    )

    transaction.gas_limit = project.provider.estimate_gas_cost(transaction)
    signed_transaction = deployer.sign_transaction(transaction)
    if prompt:
        logger.info("Blueprint deploy transaction:")
        logger.info(signed_transaction)
        logger.info("Proceed? (yes/no)")
        proceed = input("> ")
        if proceed.lower() not in ["y", "yes"]:
            logger.error("Script stopped.")
            sys.exit()
    receipt = project.provider.send_transaction(signed_transaction)
    return receipt.contract_address
