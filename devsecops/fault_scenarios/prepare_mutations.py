"""Prepare des copies CSV et, facultativement, des copies du projet Power BI."""
import argparse
import csv
import json
import shutil
from pathlib import Path

def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", type=Path)
    args = parser.parse_args()
    source = args.reference.resolve(strict=True)
    destination = args.output.resolve()
    if destination.exists():
        parser.error("Le dossier de sortie existe deja. Choisir un nouveau dossier.")
    if args.model:
        model = args.model.resolve(strict=True)
        if not model.is_dir():
            parser.error("--model doit viser le dossier du projet complet.")
        if destination == model or model in destination.parents:
            parser.error("La sortie doit etre en dehors du modele de reference.")
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        fields = reader.fieldnames or []
    if not {"UserPrincipalName", "RegionCode"}.issubset(fields):
        parser.error("Champs requis: UserPrincipalName, RegionCode.")
    active = lambda row: row.get("IsActive", "true").strip().lower() in {"true", "1"}
    for user, region in (("manager.fr@demo.local", "FR"), ("manager.de@demo.local", "DE")):
        if not any(r["UserPrincipalName"] == user and r["RegionCode"] == region and active(r) for r in rows):
            parser.error(f"Affectation saine manquante: {user}/{region}. Adapter les identifiants au contrat.")
    if any(r["UserPrincipalName"] == "manager.fr@demo.local" and r["RegionCode"] == "DE" and active(r) for r in rows):
        parser.error("La reference donne deja DE au manager FR.")
    if any(r["UserPrincipalName"] == "manager.de@demo.local" and r["RegionCode"] == "FR" and active(r) for r in rows):
        parser.error("La reference donne deja FR au manager DE.")
    definitions = [
        ("MUT-01", ["SEC-002"], "Ajouter DE au manager France; relier la copie Power BI a ce CSV."),
        ("MUT-02", ["SEC-003", "SEC-008"], "Remplacer DE par FR pour le manager Allemagne; relier la copie Power BI a ce CSV."),
        ("MUT-03", ["SEC-002"], "Dans la copie seulement, retirer la restriction RLS qui limite les regions. Le script ne modifie pas le DAX."),
    ]
    for mutation, detectors, note in definitions:
        folder = destination / mutation
        folder.mkdir(parents=True)
        altered = [dict(r) for r in rows]
        if mutation == "MUT-01":
            base = next(dict(r) for r in rows if r["UserPrincipalName"] == "manager.fr@demo.local" and r["RegionCode"] == "FR" and active(r))
            base["RegionCode"] = "DE"
            altered.append(base)
        if mutation == "MUT-02":
            for row in altered:
                if row["UserPrincipalName"] == "manager.de@demo.local" and row["RegionCode"] == "DE" and active(row):
                    row["RegionCode"] = "FR"
        write_csv(folder / "security_access.csv", altered, fields)
        metadata = {
            "mutation_id": mutation, "expected_failing_tests": detectors,
            "reference": str(source), "procedure": note,
            "model_change_applied_by_script": False,
        }
        (folder / "mutation.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
        if args.model:
            shutil.copytree(model, folder / "model")
        print(f"{mutation}: {folder}")
    print("Copies preparees. Le modele doit etre raccorde puis teste par le moteur du membre 2.")

if __name__ == "__main__":
    main()
