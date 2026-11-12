
from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    """
    Interface commune pour interroger les données visibles
    par un utilisateur dans le modèle Power BI.
    """

    @abstractmethod
    def get_visible_regions(self, user_principal_name: str) -> set[str]:
        """
        Retourne les régions réellement visibles par l'utilisateur.
        """
        raise NotImplementedError
