# -*- coding: utf-8 -*-
"""
Proves automàtiques (OPCIONALS): comproven que les funcions fan el que han de fer.
S'executen amb:  python -m pytest -v
Fan servir dades inventades: no cal Internet ni descarregar res.
"""

import matplotlib
matplotlib.use("Agg")  # no obre finestres de gràfics
import numpy as np
import pytest

import clustering_marti as cm


@pytest.fixture(autouse=True)
def carpeta_temporal(tmp_path, monkeypatch):
    """Cada prova treballa en una carpeta temporal perquè els PDF no embrutin el projecte."""
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def dades():
    """300 gens x 40 pacients inventats, amb dues classes ben separades (25 + 15)."""
    rng = np.random.default_rng(0)
    y = np.array([0] * 25 + [1] * 15)
    X = rng.normal(size=(300, 40))
    X[:60, y == 1] += 3.0
    return X, y


# ---------- casos normals ----------
def test_preprocess_log_no_dona_nan_ni_negatius():
    """Amb valors negatius i enormes, el resultat ha de quedar dins [log2(101), log2(16001)]."""
    X_log = cm.preprocess_log(np.array([[-500.0, 50.0, 200.0, 99999.0]]))
    assert not np.isnan(X_log).any()
    assert X_log.min() >= np.log2(101) - 1e-9 and X_log.max() <= np.log2(16001) + 1e-9


def test_filtre_i_estandar_dona_500_x_72_amb_mitjana_0_i_std_1(dades):
    """Cada gen filtrat ha de tenir mitjana 0 i desviació 1."""
    X, _ = dades
    X_clean, idx = cm.filtre_i_estandar(X, n_genes=50)
    assert X_clean.shape == (50, 40) and len(idx) == 50
    assert np.allclose(X_clean.mean(axis=1), 0) and np.allclose(X_clean.std(axis=1), 1)


def test_pacients_ben_separats_donen_ari_alt(dades):
    """Si les dues classes són clares, el clustering les ha de recuperar (ARI > 0.9)."""
    X, y = dades
    X_clean, _ = cm.filtre_i_estandar(X, n_genes=100)
    Zs, aris = cm.jerarquic_pacients(X_clean, y)
    assert aris["complete"] > 0.9 and aris["average"] > 0.9
    assert Zs["average"].shape == (39, 4)  # 40 pacients -> 39 fusions


# ---------- casos erronis (han de donar error) ----------
def test_demanar_mes_gens_dels_que_hi_ha_dona_error(dades):
    X, _ = dades
    with pytest.raises(AssertionError):
        cm.filtre_i_estandar(X[:10], n_genes=20)


def test_kmeans_sense_k2_dona_error(dades):
    X, y = dades
    X_clean, _ = cm.filtre_i_estandar(X, n_genes=50)
    with pytest.raises(AssertionError):
        cm.kmeans_pacients(X_clean, y, k_range=range(3, 5))


def test_moduls_gens_una_etiqueta_per_gen(dades):
    """Cada gen ha de rebre exactament un mòdul, entre 1 i k_max."""
    X, _ = dades
    X_clean, _ = cm.filtre_i_estandar(X, n_genes=100)
    Z, best_k, labels = cm.moduls_gens(X_clean, k_range=range(2, 6))
    assert Z.shape == (99, 4) and len(labels) == 100 and 2 <= best_k <= 5
