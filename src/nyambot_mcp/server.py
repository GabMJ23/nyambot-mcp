"""nyambot-mcp — l'administration française pour vos agents IA (serveur MCP).

v1 (gratuit, sans clé API) : interroge DIRECTEMENT les API publiques de l'État,
sans authentification :
  - geo.api.gouv.fr            → résolution de commune
  - Base Adresse Nationale     → géocodage d'adresse
  - Géorisques (gaspar)        → risques naturels & technologiques
  - ADEME / data.ademe.fr      → DPE des logements existants

Conçu comme un « cockpit immobilier » : un agent peut enchaîner
resolve_commune → risques_immobilier → dpe_logement pour évaluer un bien.

Roadmap v2 : routage OPTIONNEL vers api.nyambot.ai (clé API) pour les
fonctionnalités premium (fédération étendue, RAG fiches Service-Public,
réponses sourcées). La couche d'accès aux données est volontairement isolée
dans `_get_json` pour rendre ce basculement trivial et réversible.

Transport : stdio (MCP). Lancement : `nyambot-mcp` (ou `python -m nyambot_mcp`).
"""
from __future__ import annotations

import httpx
from mcp.server.fastmcp import FastMCP

USER_AGENT = "nyambot-mcp/0.1 (+https://nyambot.ai)"
TIMEOUT_SECONDS = 20.0

mcp = FastMCP("nyambot")


async def _get_json(url: str, params: dict | None = None) -> tuple[object | None, str | None]:
    """GET JSON avec gestion d'erreur explicite.

    Renvoie un tuple ``(data, error)`` : exactement l'un des deux est ``None``.
    On NE lève jamais — l'agent reçoit un message d'erreur clair et décide quoi
    faire (réessayer, autre outil…), plutôt qu'un crash opaque.
    """
    try:
        async with httpx.AsyncClient(
            timeout=TIMEOUT_SECONDS,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        ) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPStatusError as exc:
        return None, f"HTTP {exc.response.status_code} (source : {url})"
    except httpx.TimeoutException:
        return None, f"Timeout après {TIMEOUT_SECONDS}s (source : {url})"
    except httpx.RequestError as exc:
        return None, f"Erreur réseau : {type(exc).__name__}"
    except ValueError:
        return None, "Réponse non-JSON inattendue de la source."


@mcp.tool()
async def resolve_commune(nom: str) -> str:
    """Résout une commune française par son nom.

    Renvoie code INSEE, département, région, coordonnées et population. À utiliser
    en PREMIER, comme ancre géographique, avant les autres outils (le code INSEE
    sert ensuite à interroger les risques, par exemple).

    Args:
        nom: nom de la commune (ex. « Lyon », « Combs-la-Ville »).
    """
    data, error = await _get_json(
        "https://geo.api.gouv.fr/communes",
        {
            "nom": nom,
            "fields": "nom,code,codeDepartement,codeRegion,centre,population",
            "boost": "population",
            "limit": 5,
        },
    )
    if error:
        return f"Erreur : {error}"
    if not data:
        return f"Aucune commune trouvée pour « {nom} »."

    lines = []
    for commune in data:
        coords = (commune.get("centre") or {}).get("coordinates", [None, None])
        lines.append(
            f"- {commune.get('nom')} — INSEE {commune.get('code')}, "
            f"dépt {commune.get('codeDepartement')}, région {commune.get('codeRegion')} "
            f"— pop. {commune.get('population', '?')} "
            f"— lat/lon {coords[1]},{coords[0]}"
        )
    return "Communes trouvées (la plus peuplée en tête) :\n" + "\n".join(lines)


@mcp.tool()
async def geocode_address(adresse: str) -> str:
    """Géocode une adresse française via la Base Adresse Nationale (BAN).

    Renvoie l'adresse normalisée, les coordonnées, le code postal, la commune et
    le code INSEE — utile pour cibler ensuite risques/DPE à l'adresse exacte.

    Args:
        adresse: adresse libre (ex. « 8 boulevard du Port, Amiens »).
    """
    data, error = await _get_json(
        "https://api-adresse.data.gouv.fr/search/", {"q": adresse, "limit": 1}
    )
    if error:
        return f"Erreur : {error}"
    features = (data or {}).get("features", [])
    if not features:
        return f"Adresse introuvable : « {adresse} »."

    props = features[0]["properties"]
    lon, lat = features[0]["geometry"]["coordinates"]
    return (
        f"{props.get('label')}\n"
        f"- code INSEE : {props.get('citycode')}\n"
        f"- code postal : {props.get('postcode')}\n"
        f"- commune : {props.get('city')}\n"
        f"- coordonnées : {lat}, {lon}\n"
        f"- score de confiance : {props.get('score')}"
    )


@mcp.tool()
async def risques_immobilier(adresse_ou_code_insee: str) -> str:
    """Risques naturels & technologiques d'une commune (Géorisques / Gaspar).

    Couvre inondation, retrait-gonflement des argiles, séisme, radon, mouvements
    de terrain, sites industriels (ICPE)… À consulter AVANT un achat immobilier.

    Accepte un code INSEE (5 chiffres) OU une adresse libre — dans ce dernier cas
    l'adresse est géocodée automatiquement pour retrouver la commune.

    Args:
        adresse_ou_code_insee: ex. « 69123 » ou « 12 rue de la Paris, Pierrelatte ».
    """
    value = adresse_ou_code_insee.strip()
    commune_label = value
    code_insee = value

    if not (len(value) == 5 and value.isdigit()):
        geo_data, geo_error = await _get_json(
            "https://api-adresse.data.gouv.fr/search/", {"q": value, "limit": 1}
        )
        if geo_error:
            return f"Erreur géocodage : {geo_error}"
        features = (geo_data or {}).get("features", [])
        if not features:
            return f"Adresse introuvable : « {adresse_ou_code_insee} »."
        code_insee = features[0]["properties"].get("citycode")
        commune_label = features[0]["properties"].get("city", code_insee)

    data, error = await _get_json(
        "https://www.georisques.gouv.fr/api/v1/gaspar/risques",
        {"code_insee": code_insee},
    )
    if error:
        return f"Erreur : {error}"
    rows = (data or {}).get("data", [])
    if not rows:
        return f"Aucun risque recensé pour le code INSEE {code_insee}."

    details = rows[0].get("risques_detail", [])
    libelles = sorted(
        {d.get("libelle_risque_long") for d in details if d.get("libelle_risque_long")}
    )
    if not libelles:
        return f"Aucun risque détaillé pour {commune_label} (INSEE {code_insee})."
    return (
        f"Risques recensés pour {commune_label} (INSEE {code_insee}) :\n"
        + "\n".join(f"- {libelle}" for libelle in libelles)
    )


@mcp.tool()
async def dpe_logement(code_postal: str, adresse: str = "") -> str:
    """Diagnostics de Performance Énergétique (DPE) de logements existants (ADEME).

    Renvoie étiquette énergie (A→G), étiquette GES, surface, consommation et date
    du diagnostic. Filtre par code postal, affinable par une adresse.

    Args:
        code_postal: code postal sur 5 chiffres (ex. « 75011 »).
        adresse: optionnel — texte d'adresse pour affiner (ex. « 48 rue de Montreuil »).
    """
    if adresse:
        params = {"size": 5, "q": f"{adresse} {code_postal}", "q_fields": "adresse_ban,code_postal_ban"}
    else:
        params = {"size": 5, "q": code_postal, "q_fields": "code_postal_ban"}

    data, error = await _get_json(
        "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines", params
    )
    if error:
        return f"Erreur : {error}"
    rows = (data or {}).get("results", [])
    if not rows:
        return f"Aucun DPE trouvé pour {code_postal} {adresse}".strip() + "."

    lines = []
    for row in rows:
        surface = row.get("surface_habitable_logement") or row.get("surface_habitable_immeuble", "?")
        lines.append(
            f"- {row.get('adresse_ban', '?')} ({row.get('nom_commune_ban', '')}) : "
            f"DPE {row.get('etiquette_dpe', '?')} / GES {row.get('etiquette_ges', '?')} "
            f"— {surface} m² "
            f"— {row.get('conso_5_usages_par_m2_ep', '?')} kWh/m²/an "
            f"— diagnostic {row.get('date_etablissement_dpe', '?')}"
        )
    return f"DPE trouvés pour {code_postal} :\n" + "\n".join(lines)


def main() -> None:
    """Point d'entrée console : lance le serveur MCP en transport stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
