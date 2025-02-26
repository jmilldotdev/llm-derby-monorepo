from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    CdpWalletProvider,
    CdpWalletProviderConfig,
    EthAccountWalletProvider,
    EthAccountWalletProviderConfig,
)
from eth_account import Account

from textarena import config


def create_cdp_wallet_provider():
    return CdpWalletProvider(
        CdpWalletProviderConfig(
            api_key_name=config.CDP_API_KEY,
            api_key_private=config.CDP_API_PRIVATE_KEY,
            network_id=config.ACTIVE_NETWORK,
        )
    )


def create_eth_account_wallet_provider():
    account = Account.from_key(config.ETH_ACCOUNT_PRIVATE_KEY)
    return EthAccountWalletProvider(
        EthAccountWalletProviderConfig(
            account=account,
            chain_id=config.CHAIN_ID,
        )
    )


def create_agent_kit(provider_fn):
    return AgentKit(AgentKitConfig(wallet_provider=provider_fn()))
