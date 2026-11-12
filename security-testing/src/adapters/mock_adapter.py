
from src.adapters.base_adapter import BaseAdapter


class MockAdapter(BaseAdapter):
    """
    Simule les régions visibles par chaque utilisateur.
    Utilisé uniquement pour les tests du moteur.
    """

    def __init__(self, visible_regions: dict[str, set[str]]):
        self.visible_regions = visible_regions

    def get_visible_regions(self, user_principal_name: str) -> set[str]:
        return self.visible_regions.get(user_principal_name, set())
