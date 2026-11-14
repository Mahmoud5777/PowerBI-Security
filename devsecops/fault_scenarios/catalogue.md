# Catalogue des mutations

Ces identifiants et utilisateurs reprennent les exemples du cahier des charges. Les adapter avec les membres 1 et 2 avant l'integration. Les copies vulnerables restent des artefacts de test.

| Mutation | Modification sur la copie | Risque | Test detecteur | Assertion attendue |
|---|---|---|---|---|
| MUT-01 | Ajouter l'affectation active manager.fr@demo.local / DE | Exposition des donnees allemandes au manager France | SEC-002 : France vers DE, attendu DENY | FAIL, observe ALLOW |
| MUT-02 | Remplacer l'affectation active manager.de@demo.local / DE par FR | Perte de DE et exposition de FR | SEC-003 : Allemagne vers DE, attendu ALLOW ; SEC-008 : Allemagne vers FR, attendu DENY | Les deux FAIL |
| MUT-03 | Retirer la restriction du role RLS qui limite les regions dans une copie du modele | Acces trop large | SEC-002 au minimum et autres tests DENY selon la regle retiree | FAIL, observe ALLOW |

SEC-008 est une proposition de test supplementaire a faire ajouter par le membre 2.

## Procedure MUT-01 et MUT-02

1. Generer les CSV modifies a partir de la table de securite saine.
2. Ouvrir exclusivement la copie du projet Power BI.
3. Dans Power Query, remplacer la source de la table de securite par le CSV de cette mutation et verifier le chemin.
4. Actualiser et enregistrer la copie.
5. Interroger cette copie avec le moteur du membre 2, sous les identites controlees.
6. Conserver la matrice attendue saine : seuls le modele teste et ses affectations changent.

Le script ne raccorde pas automatiquement le modele au nouveau CSV. Si le modele n'utilise pas ce fichier comme source, adapter la mutation avec le membre 1.

## Procedure MUT-03

1. Ouvrir le projet copie dans generated/MUT-03/model.
2. Dans Modelisation > Gerer les roles, modifier uniquement le role de la copie.
3. Avec le membre 1, identifier l'expression qui limite le perimetre regional et la remplacer par TRUE(), ou retirer sa condition utilisateur selon le modele.
4. Verifier les autres filtres et les relations : une restriction restante peut masquer l'effet attendu.
5. Enregistrer et executer les tests sur cette copie. Noter l'expression avant/apres et la version.
6. Ne jamais appliquer ce changement au modele sain partage.

Le script prepare une copie mais ne modifie pas le DAX.

## Interpretation

Baseline : toutes les assertions PASS.
Mutation : les assertions des tests detecteurs FAIL.
Detection de mutation : PASS uniquement quand les echecs attendus sont presents, apres un baseline sain et une mutation effectivement appliquee.
La gate de securite reste FAIL sur une violation, meme si la detection de mutation est PASS.
