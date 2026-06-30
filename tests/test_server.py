"""Tests offline (sans réseau) — on monkeypatche `_get_json` avec des réponses
canoniques pour valider le parsing et le formatage de chaque outil.

Lancer : pytest
"""
from __future__ import annotations

import pytest

from nyambot_mcp import server


async def _fake(data, error=None):
    return data, error


@pytest.mark.asyncio
async def test_resolve_commune_ok(monkeypatch):
    payload = [
        {
            "nom": "Lyon",
            "code": "69123",
            "codeDepartement": "69",
            "codeRegion": "84",
            "centre": {"type": "Point", "coordinates": [4.8351, 45.758]},
            "population": 519127,
        }
    ]
    monkeypatch.setattr(server, "_get_json", lambda url, params=None: _fake(payload))
    out = await server.resolve_commune("Lyon")
    assert "Lyon" in out
    assert "69123" in out
    assert "519127" in out


@pytest.mark.asyncio
async def test_resolve_commune_empty(monkeypatch):
    monkeypatch.setattr(server, "_get_json", lambda url, params=None: _fake([]))
    out = await server.resolve_commune("Zzz")
    assert "Aucune commune" in out


@pytest.mark.asyncio
async def test_resolve_commune_error(monkeypatch):
    monkeypatch.setattr(server, "_get_json", lambda url, params=None: _fake(None, "Timeout après 20.0s"))
    out = await server.resolve_commune("Lyon")
    assert "Erreur" in out


@pytest.mark.asyncio
async def test_risques_with_insee(monkeypatch):
    payload = {
        "data": [
            {
                "risques_detail": [
                    {"libelle_risque_long": "Inondation"},
                    {"libelle_risque_long": "Séisme"},
                    {"libelle_risque_long": "Inondation"},  # doublon -> dédupliqué
                ]
            }
        ]
    }
    monkeypatch.setattr(server, "_get_json", lambda url, params=None: _fake(payload))
    out = await server.risques_immobilier("69123")
    assert "Inondation" in out
    assert "Séisme" in out
    # déduplication : "Inondation" n'apparaît qu'une fois
    assert out.count("Inondation") == 1


@pytest.mark.asyncio
async def test_dpe_ok(monkeypatch):
    payload = {
        "results": [
            {
                "adresse_ban": "48 Rue de Montreuil",
                "nom_commune_ban": "Paris",
                "etiquette_dpe": "D",
                "etiquette_ges": "E",
                "surface_habitable_logement": 62,
                "conso_5_usages_par_m2_ep": 210,
                "date_etablissement_dpe": "2023-06-01",
            }
        ]
    }
    monkeypatch.setattr(server, "_get_json", lambda url, params=None: _fake(payload))
    out = await server.dpe_logement("75011")
    assert "DPE D" in out
    assert "GES E" in out
    assert "62 m²" in out
