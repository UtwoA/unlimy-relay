from dataclasses import dataclass


@dataclass
class ProviderActionResult:
    ok: bool
    message: str


class ProviderAdapter:
    name = "base"

    def restart_node(self, node_name: str) -> ProviderActionResult:
        return ProviderActionResult(ok=True, message=f"Restart accepted for {node_name} via {self.name} stub")


class HetznerAdapter(ProviderAdapter):
    name = "hetzner"


class VultrAdapter(ProviderAdapter):
    name = "vultr"


class AezaAdapter(ProviderAdapter):
    name = "aeza"


class OvhAdapter(ProviderAdapter):
    name = "ovh"


class NetcupAdapter(ProviderAdapter):
    name = "netcup"


def get_provider_adapter(provider: str) -> ProviderAdapter:
    providers = {
        "hetzner": HetznerAdapter(),
        "vultr": VultrAdapter(),
        "aeza": AezaAdapter(),
        "ovh": OvhAdapter(),
        "netcup": NetcupAdapter(),
    }
    return providers.get(provider.lower(), ProviderAdapter())
