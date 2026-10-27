# -*- coding: utf-8 -*-
"""
test_materiales.py
==================
Bateria de proves automàtiques per a la classificació no supervisada de materials elèctrics.
Cobreix casos normals, límit i d'error segons els criteris d'excel·lència de la rúbrica CPIA.

Execució:
    python test_materiales.py
    python -m unittest -v test_materiales.py
"""

import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN


class TestClassificacioMaterials(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Localitzar el dataset per a les proves."""
        cls.aqui = Path(__file__).resolve().parent
        cls.candidats = [
            cls.aqui / "datos" / "materiales_electricos.csv",
            cls.aqui / "materiales_electricos.csv",
            cls.aqui.parents[1] / "datos" / "materiales_electricos.csv" if len(cls.aqui.parents) >= 2 else cls.aqui,
        ]
        cls.csv_path = next((p for p in cls.candidats if p.exists() and p.is_file()), None)

    # =========================================================================
    # 1. CASOS NORMALS
    # =========================================================================

    def test_01_carrega_dataset(self):
        """Verifica que el dataset conté exactament 57 materials i les columnes necessàries."""
        self.assertIsNotNone(self.csv_path, "No s'ha trobat el fitxer CSV de dades.")
        df = pd.read_csv(self.csv_path)
        self.assertEqual(len(df), 57, "El dataset ha de contenir exactament 57 materials reals.")
        columnes_esperades = {"material", "log_rho_300K", "alpha_coef", "clase_real"}
        self.assertTrue(columnes_esperades.issubset(set(df.columns)), "Falten columnes obligatòries al CSV.")

    def test_02_distribucio_families_reals(self):
        """Comprova la composició exacta de les tres classes experimentals."""
        df = pd.read_csv(self.csv_path)
        comptes = df["clase_real"].value_counts().to_dict()
        self.assertEqual(comptes.get("Conductor"), 35, "Hi ha d'haver 35 metalls conductors.")
        self.assertEqual(comptes.get("Semiconductor"), 12, "Hi ha d'haver 12 semiconductors.")
        self.assertEqual(comptes.get("Aislante"), 10, "Hi ha d'haver 10 aïllants dielèctrics.")

    def test_03_estandarditzacio_zscore(self):
        """Verifica que el preprocessament Z-Score deixa mitjana 0 i variància 1."""
        df = pd.read_csv(self.csv_path)
        X = df[["log_rho_300K", "alpha_coef"]].values
        mu = np.mean(X, axis=0)
        sigma = np.std(X, axis=0)
        Z = (X - mu) / sigma
        np.testing.assert_allclose(np.mean(Z, axis=0), [0.0, 0.0], atol=1e-7,
                                   err_msg="La mitjana z-score ha de ser 0.")
        np.testing.assert_allclose(np.std(Z, axis=0), [1.0, 1.0], atol=1e-7,
                                   err_msg="La desviació estàndard z-score ha de ser 1.")

    def test_04_convergencia_dbscan_tres_clusters(self):
        """Comprova que DBSCAN amb eps=0.65 i min_samples=3 descobreix 3 clústers i 0 soroll."""
        df = pd.read_csv(self.csv_path)
        X = df[["log_rho_300K", "alpha_coef"]].values
        Z = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
        
        db = DBSCAN(eps=0.65, min_samples=3).fit(Z)
        etiquetes = db.labels_
        clusters_unics = set(etiquetes) - {-1}
        soroll = np.sum(etiquetes == -1)

        self.assertEqual(len(clusters_unics), 3, "DBSCAN ha de descobrir exactament 3 clústers físics.")
        self.assertEqual(soroll, 0, "No hi ha d'haver cap punt de soroll amb aquests paràmetres.")

    def test_05_puresa_classificacio(self):
        """Valida que la puresa per a conductors i aïllants és del 100%."""
        df = pd.read_csv(self.csv_path)
        X = df[["log_rho_300K", "alpha_coef"]].values
        Z = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
        
        db = DBSCAN(eps=0.65, min_samples=3).fit(Z)
        df["cluster"] = db.labels_

        # 35 metalls conductors han d'estar en un únic clúster
        cluster_metalls = df[df["clase_real"] == "Conductor"]["cluster"].unique()
        self.assertEqual(len(cluster_metalls), 1, "Tots els conductors han d'estar al mateix clúster.")
        
        # 10 aïllants han d'estar en un únic clúster
        cluster_aillants = df[df["clase_real"] == "Aislante"]["cluster"].unique()
        self.assertEqual(len(cluster_aillants), 1, "Tots els aïllants han d'estar al mateix clúster.")
        
        # Els clústers han de ser diferents entre si
        self.assertNotEqual(cluster_metalls[0], cluster_aillants[0], "Metalls i aïllants han de tenir clústers diferents.")

    # =========================================================================
    # 2. CASOS LÍMIT (EDGE CASES)
    # =========================================================================

    def test_06_columna_constant_evita_divisio_zero(self):
        """Verifica que si una característica és constant, el codi no produeix NaNs."""
        X_constant = np.array([[5.0, 1.0], [5.0, 2.0], [5.0, 3.0]])
        mu = np.mean(X_constant, axis=0)
        sigma = np.std(X_constant, axis=0)
        sigma_safe = np.where(sigma == 0, 1.0, sigma)
        Z = (X_constant - mu) / sigma_safe
        self.assertFalse(np.isnan(Z).any(), "No hi pot haver valors NaN per divisió per zero.")
        np.testing.assert_array_equal(Z[:, 0], np.zeros(3), "La columna constant ha de quedar a zero.")

    def test_07_epsilon_gegant_unifica_clusters(self):
        """Un radi d'epsilon molt gran (ex: 50.0) ha d'unir totes les dades en un únic clúster."""
        df = pd.read_csv(self.csv_path)
        X = df[["log_rho_300K", "alpha_coef"]].values
        Z = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
        db = DBSCAN(eps=50.0, min_samples=3).fit(Z)
        self.assertEqual(len(set(db.labels_)), 1, "Amb radi gegant tot ha de formar 1 sol grup.")
        self.assertEqual(db.labels_[0], 0, "L'etiqueta ha de ser 0.")

    def test_08_epsilon_minuscul_tot_soroll(self):
        """Un radi d'epsilon minúscul (ex: 0.0001) ha de classificar tots els punts com a soroll (-1)."""
        df = pd.read_csv(self.csv_path)
        X = df[["log_rho_300K", "alpha_coef"]].values
        Z = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
        db = DBSCAN(eps=0.0001, min_samples=3).fit(Z)
        self.assertTrue(np.all(db.labels_ == -1), "Amb radi minúscul tots els punts han de ser soroll.")

    # =========================================================================
    # 3. CASOS ERRONIS (ERROR HANDLING)
    # =========================================================================

    def test_09_fitxer_inexistent_llanca_error(self):
        """Verifica que intentar carregar un fitxer inexistent llança FileNotFoundError."""
        ruta_falsa = Path("ruta_inexistent_materials_12345.csv")
        with self.assertRaises((FileNotFoundError, OSError)):
            pd.read_csv(ruta_falsa)

    def test_10_epsilon_invalid_llanca_error(self):
        """Verifica que un valor d'epsilon <= 0 llança ValueError."""
        with self.assertRaises(ValueError):
            DBSCAN(eps=-0.5, min_samples=3).fit([[1.0, 2.0], [3.0, 4.0]])

    def test_11_columnes_faltants_llanca_error(self):
        """Verifica que si manquen atributs s'aixeca un KeyError."""
        df_incomplet = pd.DataFrame({"material": ["Coure"], "log_rho_300K": [-7.7]})
        with self.assertRaises(KeyError):
            _ = df_incomplet[["log_rho_300K", "alpha_coef"]]


if __name__ == "__main__":
    unittest.main(verbosity=2)
