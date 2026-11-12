
import csv
from pathlib import Path

from src.comparator import compare_regions
from src.adapters.base_adapter import BaseAdapter


class SecurityTestEngine:
    def __init__(self, matrix_path: str, adapter: BaseAdapter):
        self.matrix_path = Path(matrix_path)
        self.adapter = adapter

    @staticmethod
    def _parse_active(value: str) -> bool:
        """Valide et convertit la valeur IsActive."""

        active_value = value.strip().lower()

        if active_value not in {"true", "false"}:
            raise ValueError(
                f"Invalid IsActive value: '{value}'. "
                "Expected 'true' or 'false'."
            )

        return active_value == "true"

    def _load_matrix(self) -> list[dict]:
        """Charge et valide les données de la matrice CSV."""

        with self.matrix_path.open(
            mode="r",
            encoding="utf-8-sig",
            newline=""
        ) as file:
            reader = csv.DictReader(file)

            required = {
                "UserPrincipalName",
                "RegionCode",
                "IsActive",
            }

            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise ValueError("Invalid authorization matrix format")

            rows = []

            for row in reader:
                if any(row.get(field) is None for field in required):
                    raise ValueError("Invalid authorization matrix format")

                user = row["UserPrincipalName"].strip().lower()
                region = row["RegionCode"].strip().upper()
                active = self._parse_active(row["IsActive"])

                if not user or not region:
                    raise ValueError(
                        "Missing required value: "
                        "UserPrincipalName and RegionCode cannot be empty."
                    )

                rows.append({
                    "user": user,
                    "region": region,
                    "active": active,
                })

            return rows

    def load_authorizations(self) -> dict[str, set[str]]:
        """Charge les régions autorisées pour chaque utilisateur actif."""

        authorizations: dict[str, set[str]] = {}

        for row in self._load_matrix():
            if row["active"]:
                authorizations.setdefault(
                    row["user"], set()
                ).add(row["region"])

        return authorizations

    def load_all_users(self) -> set[str]:
        """Retourne tous les utilisateurs présents dans la matrice."""

        return {
            row["user"]
            for row in self._load_matrix()
        }

    def run_test(
        self,
        user_principal_name: str,
        target_region: str | None = None,
        scenario_type: str = "ALLOW",
    ) -> dict:
        """Exécute un scénario de sécurité pour un utilisateur."""

        user = user_principal_name.strip().lower()
        scenario = scenario_type.strip().upper()
        target = target_region.strip().upper() if target_region else None

        authorizations = self.load_authorizations()
        all_users = self.load_all_users()

        expected_regions = authorizations.get(user, set())

        # Vérification des paramètres et du scénario
        if scenario == "ALLOW":
            if not target or target not in expected_regions:
                raise ValueError(
                    "ALLOW target must be an authorized region"
                )

            expected = expected_regions

        elif scenario == "DENY":
            if not target or target in expected_regions:
                raise ValueError(
                    "DENY target must be an unauthorized region"
                )

            expected = expected_regions

        elif scenario == "UNKNOWN_USER":
            if user in all_users:
                raise ValueError(
                    "UNKNOWN_USER must not exist in the matrix"
                )

            expected = set()

        elif scenario == "INACTIVE_USER":
            if user not in all_users or user in authorizations:
                raise ValueError(
                    "INACTIVE_USER must have no active assignment"
                )

            expected = set()

        elif scenario == "MULTI_REGION":
            if len(expected_regions) < 2:
                raise ValueError(
                    "MULTI_REGION requires at least two authorized regions"
                )

            expected = expected_regions

        else:
            raise ValueError(f"Unsupported scenario: {scenario}")

        # Récupération des régions réellement visibles
        actual_regions = self.adapter.get_visible_regions(user)

        # Comparaison entre autorisations et accès réels
        comparison = compare_regions(expected, actual_regions)

        return {
            "user": user,
            "scenario": scenario,
            "target_region": target,
            "expected_regions": sorted(comparison.expected_regions),
            "actual_regions": sorted(comparison.actual_regions),
            "missing_regions": sorted(comparison.missing_regions),
            "unauthorized_regions": sorted(comparison.unauthorized_regions),
            "status": "PASS" if comparison.passed else "FAIL",
        }
