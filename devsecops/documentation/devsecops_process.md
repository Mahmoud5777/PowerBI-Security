# Processus DevSecOps du membre 3

## Mission

Préparer au moins trois mutations isolées, consommer les résultats du moteur du membre 2, produire un rapport de sécurité et démontrer une chaîne reproductible.

## État du prototype

Les fichiers devsecops/examples sont fictifs. Aucun test de ce kit n'interroge Power BI.
Le workflow devsecops-demo vérifie les scripts de reporting avec ces exemples.
Le workflow réel reste un gabarit inactif dans devsecops/workflows jusqu'au raccordement au moteur.

## Interface à confirmer avec les membres 1 et 2

- Dossier complet du projet PBIP ou du modèle PBIX de référence.
- Table de sécurité saine et matrice métier attendue, conservée pendant toutes les mutations.
- Identifiants des utilisateurs, régions et rôle RLS.
- Commande exacte du moteur et méthode de sélection de la copie testée.
- Identité effective utilisée pour chaque requête et preuve d'application du RLS.
- Résultats : JSON liste ou objet results, ou CSV, avec les champs du cahier des charges.
- Un résultat par couple scénario, utilisateur et région ; un fichier par exécution/version.
- Tests supplémentaires pour la mutation MUT-02, notamment SEC-008.
- Couverture complète du catalogue, même en présence de violations.
- Codes du moteur à convenir : 0 conforme, 1 violation, 2 erreur technique.

Le générateur accepte les champs textuels non vides run_id, test_id, user_principal_name, target_region, expected_access, actual_access, assertion_status, model_version, details, timestamp_utc. Les accès sont ALLOW/DENY et les assertions PASS/FAIL.

## Exécution réelle

1. Identifier le commit et le modèle sain ; exécuter tout le catalogue sous les identités contrôlées.
2. Arrêter la campagne et résoudre le problème si le baseline n'est pas sain.
3. Préparer les copies à partir de la table de sécurité réelle.
4. Raccorder chaque copie à son CSV ; pour MUT-03 modifier la règle RLS de la copie.
5. Vérifier que les copies n'utilisent plus les sources de sécurité saines.
6. Exécuter le même moteur et la même matrice attendue sur chaque copie.
7. Générer un rapport par fichier de résultats. Indiquer la mutation et tous les tests détecteurs attendus.
8. Archiver les résultats bruts, la version, la procédure et une preuve de la modification.
9. Revenir au modèle sain et relancer le baseline.

Le reporting ne vérifie pas lui-même que Power BI a été interrogé ni que tout le catalogue a été exécuté. Ces preuves et la couverture relèvent du moteur et de la validation d'intégration.

## Codes du générateur

- 0 : assertions conformes, sans échec de détection demandé.
- 1 : violation de sécurité, ou mutation non détectée par les tests attendus.
- 2 : fichier absent, résultat vide ou contrat incohérent.

Un rapport de mutation peut afficher sécurité FAIL et détection PASS. Le code reste 1 pour empêcher une validation de sécurité d'une version vulnérable.

## Pipeline

Le workflow demo se déclenche sur la branche pole-3-devsecops, sur les PR portant sur ce pôle et manuellement.
Les erreurs attendues des fixtures sont vérifiées explicitement : sa réussite valide la démonstration du reporting.
Pour la CI réelle, remplir le gabarit avec la commande du moteur, les dépendances, le runner et les variables réellement nécessaires. Ne pas utiliser continue-on-error pour masquer une violation.
La publication des rapports utilise always() afin de conserver les preuves même en cas d'échec.

## Variables et secrets

Le prototype local et le workflow de démonstration n'utilisent aucun secret.
Après choix de l'adaptateur réel, documenter les variables et secrets qu'il exige, puis configurer les secrets GitHub dans Settings > Secrets and variables > Actions. Ne pas inventer une authentification avant cette décision.
Prévoir un .env.example sans valeur confidentielle si l'adaptateur utilise un .env local.
Confirmer que le compte ou mécanisme de test applique réellement RLS ; une identité privilégiée peut contourner le rôle attendu.

## Retour à la référence et livrables

Les mutations générées et les rapports sont ignorés par Git. Les scripts, exemples, catalogue, documentation et workflows sont versionnés.
Les copies de modèles sont locales ; elles ne remplacent pas la référence saine.
Pour la soutenance : montrer baseline PASS, mutation appliquée, assertions FAIL, détection PASS, rapport détaillé, puis retour au baseline.
