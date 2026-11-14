"""Rapport et gate de securite. Bibliotheque standard uniquement."""
import argparse
import csv
import json
import sys
from pathlib import Path

FIELDS = (
    "run_id", "test_id", "user_principal_name", "target_region",
    "expected_access", "actual_access", "assertion_status",
    "model_version", "details", "timestamp_utc",
)

def read_results(path):
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
    else:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        rows = data.get("results") if isinstance(data, dict) else data
    if not isinstance(rows, list) or not rows:
        raise ValueError("Le resultat doit contenir une liste non vide de tests.")
    seen = set()
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"Ligne {index}: objet attendu.")
        missing = [key for key in FIELDS if key not in row]
        if missing:
            raise ValueError(f"Ligne {index}: champs manquants: {missing}")
        if any(not isinstance(row[key], str) or not row[key].strip() for key in FIELDS):
            raise ValueError(f"Ligne {index}: tous les champs doivent etre des chaines non vides.")
        if row["expected_access"] not in {"ALLOW", "DENY"} or row["actual_access"] not in {"ALLOW", "DENY"}:
            raise ValueError(f"Ligne {index}: acces ALLOW/DENY attendu.")
        if row["assertion_status"] not in {"PASS", "FAIL"}:
            raise ValueError(f"Ligne {index}: statut PASS/FAIL attendu.")
        computed = "PASS" if row["expected_access"] == row["actual_access"] else "FAIL"
        if row["assertion_status"] != computed:
            raise ValueError(f"Ligne {index}: statut incompatible avec attendu/observe.")
        key = tuple(row[k] for k in ("run_id", "test_id", "user_principal_name", "target_region"))
        if key in seen:
            raise ValueError(f"Ligne {index}: resultat duplique.")
        seen.add(key)
    return rows

def cell(value):
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mutation-id")
    parser.add_argument("--expected-failure", action="append", default=[])
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    try:
        rows = read_results(args.input)
        if args.mutation_id and not args.expected_failure:
            raise ValueError("Une mutation exige au moins un --expected-failure TestId.")
        if args.expected_failure and not args.mutation_id:
            raise ValueError("--expected-failure exige --mutation-id.")
        if len({(r["run_id"], r["model_version"]) for r in rows}) != 1:
            raise ValueError("Fournir un fichier par execution et par version du modele.")
    except (OSError, ValueError, TypeError) as error:
        print(f"ERREUR: {error}", file=sys.stderr)
        return 2

    failed = [r for r in rows if r["assertion_status"] == "FAIL"]
    status = "FAIL" if failed else "PASS"
    lines = [
        "# Rapport de securite Power BI",
        "",
        "**Donnees fictives : demonstration du reporting uniquement.**" if args.demo else "**Resultats fournis par le moteur de tests. Verifier la provenance et l'identite effective dans la preuve d'execution.**",
        "",
        f"- Execution : {cell(rows[0]['run_id'])}",
        f"- Version du modele : {cell(rows[0]['model_version'])}",
        f"- Date UTC : {cell(rows[0]['timestamp_utc'])}",
        f"- Assertions de securite : **{status}**",
        f"- Total : {len(rows)} ; PASS : {len(rows) - len(failed)} ; FAIL : {len(failed)}",
    ]
    if args.mutation_id:
        failed_ids = {r["test_id"] for r in failed}
        present_ids = {r["test_id"] for r in rows}
        detected = set(args.expected_failure).issubset(failed_ids)
        lines += [
            f"- Mutation : {cell(args.mutation_id)}",
            f"- Detection des echecs attendus : **{'PASS' if detected else 'FAIL'}**",
            f"- Tests detecteurs attendus : {', '.join(map(cell, args.expected_failure))}",
        ]
        missing = set(args.expected_failure) - present_ids
        if missing:
            lines.append(f"- Tests detecteurs absents : {', '.join(sorted(missing))}")
    lines += [
        "",
        "| Test | Utilisateur | Region | Attendu | Observe | Assertion | Detail |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell(row[k]) for k in (
            "test_id", "user_principal_name", "target_region",
            "expected_access", "actual_access", "assertion_status", "details",
        )) + " |")
    if args.mutation_id:
        lines += ["", "Le statut de detection est distinct du statut de securite. La verification de detection suppose un baseline sain, un catalogue gele et une mutation effectivement appliquee a la copie testee."]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Rapport: {args.output}; securite: {status}")
    # Une mutation detectee ne transforme jamais une violation en succes de securite.
    if args.mutation_id and not set(args.expected_failure).issubset({r["test_id"] for r in failed}):
        return 1
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
