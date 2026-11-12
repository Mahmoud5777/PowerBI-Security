
from collections.abc import Callable, Iterable
from typing import Any

from src.adapters.base_adapter import BaseAdapter


class PowerBIAdapter(BaseAdapter):
    """
    Adaptateur permettant de récupérer les régions visibles
    pour un utilisateur depuis un modèle Power BI.

    query_executor doit exécuter la requête dans le véritable
    contexte d'identité Power BI de l'utilisateur.
    """

    def __init__(
        self,
        query_executor: Callable[[str], Iterable[dict[str, Any]]],
    ):
        if not callable(query_executor):
            raise TypeError("query_executor must be callable")

        self.query_executor = query_executor

    def get_visible_regions(
        self,
        user_principal_name: str,
    ) -> set[str]:

        user = user_principal_name.strip().lower()

        if not user:
            raise ValueError("User principal name cannot be empty")

        rows = self.query_executor(user)

        if rows is None:
            raise ValueError("Power BI query returned no result")

        visible_regions = set()

        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("Invalid Power BI query result")

            region = row.get("RegionCode")

            if not isinstance(region, str) or not region.strip():
                raise ValueError("Invalid RegionCode in Power BI result")

            visible_regions.add(region.strip().upper())

        return visible_regions
