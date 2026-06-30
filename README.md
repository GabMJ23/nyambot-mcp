# nyambot-mcp

**L'administration française pour vos agents IA.** Un serveur [MCP](https://modelcontextprotocol.io) qui branche Claude, Cursor ou n'importe quel agent IA sur les données publiques de l'État français — communes, géocodage, **risques immobiliers** et **DPE** — avec les sources officielles.

▶ **L'agent Nyambot complet est en ligne — essayez-le : [nyambot.ai](https://nyambot.ai)**

> Pensé comme un **cockpit immobilier** : votre agent enchaîne `resolve_commune` → `risques_immobilier` → `dpe_logement` pour évaluer un bien en quelques secondes, sur de la donnée officielle.

- 🆓 **Gratuit, sans clé API** — interroge directement les API publiques de l'État.
- 🇫🇷 **Sources officielles** : geo.api.gouv.fr, Base Adresse Nationale, Géorisques, ADEME.
- ⚡ **Installation en une ligne** (via `uvx`).
- 📖 **Open-source, licence MIT.**

---

## Pourquoi Nyambot — le game changer

En France, **des milliards d'euros de droits ne sont pas réclamés** chaque année — pas par manque d'éligibilité, mais parce que l'administration est un labyrinthe. [Nyambot.ai](https://nyambot.ai) est un agent IA qui ne se contente pas d'**informer** : il **exécute les démarches**, ancré sur la donnée officielle de l'État, **chaque réponse sourcée, sans hallucination**. Là où un chatbot générique invente et où les portails publics n'accompagnent pas, **Nyambot agit**.

Il couvre **tous les cas de vie** — carte d'identité, impôts, permis de conduire, carte grise, aides & allocations, déménagement, succession, création d'entreprise, **immobilier**… `nyambot-mcp` ouvre une partie de cette capacité à votre propre agent IA.

### L'immobilier, déroulé en direct

Sur l'agent complet ([nyambot.ai](https://nyambot.ai)), une question comme *« Cette maison à Pierrelatte à 286 000 € est-elle bien placée ? »* déclenche une analyse **visible étape par étape** — l'agent va chercher le fichier **DVF**, le **déroule**, et le croise avec les risques et le DPE :

```
📊 DVF — Demandes de valeurs foncières (data.gouv.fr)
   Requête : commune = Pierrelatte (26235) · type = Maison · 2023–2024
   → 38 ventes comparables · médiane du secteur ≈ 2 053 €/m²

⚠️ Géorisques : aléa retrait-gonflement des argiles (moyen)
🏷️ DPE du bien : étiquette A
```

> **Verdict** : à ~2 750 €/m², le bien est ~34 % au-dessus de la médiane locale (source DVF, 38 ventes comparables) — justifiable par le DPE A, mais avec une marge de négociation. Point de vigilance : zone d'aléa argiles à vérifier sur le bâti.

Va chercher la donnée officielle, la déroule, la croise, et **cite ses sources** — en quelques secondes. Aucun chatbot générique ne fait ça.

**La vision (v2)** : `nyambot-mcp` ouvre l'accès à toute la donnée publique française vivante — démarches administratives, prix de l'immobilier au m² réel, textes de loi, données d'entreprises — déjà indexée, citable, prête à l'emploi.

> *L'accès programmatique à DVF, au RAG des fiches Service-Public et aux sources authentifiées fait partie de la **v2 premium** (voir plus bas). Le connecteur gratuit ci-dessous couvre déjà communes, géocodage, risques et DPE.*

---

## Outils disponibles

| Outil | Ce qu'il fait | Source officielle |
|---|---|---|
| `resolve_commune` | Nom de commune → code INSEE, département, région, coordonnées, population | geo.api.gouv.fr |
| `geocode_address` | Adresse → coordonnées, code postal, commune, code INSEE | Base Adresse Nationale |
| `risques_immobilier` | Risques naturels & technologiques d'une commune (inondation, argiles, séisme, radon…) | Géorisques |
| `dpe_logement` | DPE des logements existants (étiquette A→G, GES, surface, conso) | ADEME |

---

## En quoi est-ce différent du MCP officiel data.gouv ?

Le [serveur MCP de data.gouv.fr](https://github.com/datagouv/datagouv-mcp) et `nyambot-mcp` ne jouent pas au même niveau — ils sont **complémentaires** :

- **datagouv-mcp** expose le **catalogue open-data** : on cherche des jeux de données, on liste des ressources, on requête du tabulaire brut. C'est un outil d'**exploration / analyste de données**.
- **nyambot-mcp** expose des **réponses métier prêtes à l'emploi** : on pose une question (risques d'une commune, DPE d'un logement…) et on reçoit un résultat exploitable, **sans savoir quel dataset ni quelle colonne**. C'est un outil de **décision**.

| | datagouv-mcp (officiel) | nyambot-mcp |
|---|---|---|
| **Niveau** | Catalogue & datasets bruts | Réponses métier curées |
| **Sources** | data.gouv.fr uniquement | Multi-sources : Géorisques, BAN, geo.api.gouv.fr, ADEME… (API natives, hors catalogue data.gouv) |
| **L'agent doit…** | trouver le dataset, deviner les colonnes, construire la requête | …juste appeler l'outil |
| **Cas d'usage type** | « trouve-moi des datasets sur X » | « ce bien est-il à risque ? quel est son DPE ? » |
| **Fiabilité** | dépend du schéma deviné | pré-câblé : 1 appel = 1 réponse |

> **Vous pouvez brancher les deux.** datagouv-mcp pour explorer n'importe quel dataset ; nyambot-mcp pour des réponses rapides sur les cas de vie à forte valeur (immobilier, droits…). La version premium (`api.nyambot.ai`, à venir) ajoutera l'**interprétation propriétaire** : RAG des fiches Service-Public, article Légifrance exact, réponses entièrement sourcées.

---

## Installation

### Prérequis
[`uv`](https://docs.astral.sh/uv/) installé (recommandé). Sinon, voir « Depuis les sources » plus bas.

### Claude Desktop
Ajoutez ceci à votre `claude_desktop_config.json` :

```json
{
  "mcpServers": {
    "nyambot": {
      "command": "uvx",
      "args": ["nyambot-mcp"]
    }
  }
}
```

Puis **redémarrez Claude Desktop**. `uvx` télécharge et lance le serveur automatiquement — rien d'autre à installer.

### Claude Code
Dans le `.mcp.json` à la racine de votre projet :

```json
{
  "mcpServers": {
    "nyambot": { "command": "uvx", "args": ["nyambot-mcp"] }
  }
}
```

Ou en une commande :

```bash
claude mcp add nyambot -- uvx nyambot-mcp
```

### Cursor / VS Code / Windsurf
Même bloc `mcpServers` que ci-dessus, dans la configuration MCP de votre éditeur.

### Depuis les sources (avant publication PyPI)
```json
{
  "mcpServers": {
    "nyambot": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/GabMJ23/nyambot-mcp", "nyambot-mcp"]
    }
  }
}
```

---

## Exemples de questions

Une fois branché, demandez à votre agent :

- « Quel est le code INSEE de Combs-la-Ville ? »
- « Quels sont les risques naturels à Pierrelatte avant d'acheter ? »
- « Donne-moi des DPE autour du 75011. »
- « J'envisage d'acheter au 8 boulevard du Port à Amiens — géocode l'adresse et liste les risques de la commune. »

**Exemple de réponse réelle** — `risques_immobilier("Pierrelatte")`, via le connecteur gratuit :

```
Risques recensés pour Pierrelatte (INSEE 26235) :
- Effet toxique
- Inondation
- Mouvement de terrain
- Nucléaire
- Risque industriel
- Séisme
- Transport de marchandises dangereuses
```

---

## Vérifier que c'est branché

- Claude Code : `claude mcp list` (statut `connected`) ou `/mcp` dans une session.
- Mode debug pour voir les appels passer : `claude --debug`.

---

## Développement

```bash
git clone https://github.com/GabMJ23/nyambot-mcp
cd nyambot-mcp
uv venv && uv pip install -e ".[dev]"

# Lancer les tests (offline, sans réseau)
pytest

# Lancer le serveur localement
nyambot-mcp
```

---

## v1 gratuit vs v2 premium (à venir)

`nyambot-mcp` est la **partie gratuite et open-source** : un connecteur qui appelle directement les API publiques de l'État, sans clé.

Mais Nyambot — l'agent complet — **fédère plus de 40 outils** sur l'administration française. La **v2 premium** (payante, via clé API sur `api.nyambot.ai`) ouvrira l'accès aux outils à forte valeur qui nécessitent des **sources authentifiées** et de l'**infrastructure hébergée** :

- 📚 **RAG des ~3 000 fiches Service-Public** (recherche sémantique)
- ⚖️ **Légifrance** — l'article de loi / la jurisprudence exacts
- 💼 **France Travail**, **SIRENE / INSEE**, **Annuaire Santé (ANS)**
- 🏠 **DVF** (transactions immobilières) et réponses **entièrement sourcées**
- ✍️ **Génération de courriers** administratifs, **simulation d'aides**

**Sous le capot (la plateforme hébergée) :**

- Construit sur **Claude (Anthropic)**, avec un **routage multi-modèles** (Haiku / Sonnet) selon la tâche — vitesse là où il faut, profondeur là où ça compte.
- Une **orchestration agentique en streaming** (double boucle, events temps réel) qui montre à l'utilisateur ce que l'agent fait, étape par étape, sur des sources officielles.
- Une architecture en **3 cercles** (démarches officielles → connaissance de la France → culture générale) qui lui permet de **répondre à n'importe quelle question**, pas seulement administrative.

Le connecteur restera **open-source et gratuit** ; seules les capacités premium passeront par le backend hébergé (clé API).

> **Vous voulez un accès anticipé à la v2 ou une clé API ?** Écrivez-moi (voir Contact ci-dessous).

---

## Contact

Questions, retours, demande de clé API v2, ou partenariat :

**Gabriel Mbenda** — AI Builder & Founder, [Nyambot.ai](https://nyambot.ai)
📧 [gabrielmbenda48@gmail.com](mailto:gabrielmbenda48@gmail.com)

---

## Licence

[MIT](./LICENSE) © 2026 Gabriel Mbenda — un projet [Nyambot.ai](https://nyambot.ai).

Les données proviennent des sources officielles du gouvernement français (licence Etalab ouverte). Nyambot est un service indépendant, non affilié à l'État.
