"""Download the datasets suggested in the assignment into datos/ (git-ignored).

    .venv\\Scripts\\python.exe descargar_datos.py            # everything
    .venv\\Scripts\\python.exe descargar_datos.py hr gaia    # only some
    .venv\\Scripts\\python.exe descargar_datos.py --forzar   # re-download

- hr     -> datos/hr_hipparcos.csv: Hipparcos catalogue (VizieR I/239) stars with parallax better than 10 %
            (colour B-V ~ temperature, absolute V magnitude ~ luminosity) for K-Means vs the HR diagram.
- gaia   -> datos/gaia_pleiades.csv: Gaia DR3 cone of 3 deg around the Pleiades (M45), with proper motions
            and parallax, to find the cluster with DBSCAN (astroquery).
- kepler -> datos/kepler10_curva_luz.csv: Kepler long-cadence light curve of Kepler-10 (all quarters,
            stitched and normalised) to detect transits as anomalies (lightkurve).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

DATOS = Path(__file__).resolve().parent / "datos"

PLEIADES_ADQL = """
SELECT TOP 50000 source_id, ra, dec, parallax, parallax_error, pmra, pmdec, phot_g_mean_mag, bp_rp
FROM gaiadr3.gaia_source
WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 56.75, 24.12, 3.0))
  AND parallax > 1 AND parallax_over_error > 5 AND phot_g_mean_mag < 18
"""


def gaia(adql: str):
    from astroquery.gaia import Gaia
    Gaia.ROW_LIMIT = -1
    return Gaia.launch_job_async(adql).get_results().to_pandas()


def hr(destino: Path) -> None:
    from astroquery.vizier import Vizier
    v = Vizier(columns=["HIP", "RAICRS", "DEICRS", "Vmag", "Plx", "e_Plx", "B-V", "SpType"], row_limit=-1)
    df = v.get_catalogs("I/239/hip_main")[0].to_pandas()
    df = df[(df["Plx"] > 0) & (df["e_Plx"] / df["Plx"] < 0.1)].dropna(subset=["Vmag", "B-V"])
    df["abs_v_mag"] = df["Vmag"] + 5 * np.log10(df["Plx"] / 1000) + 5  # Plx in mas
    df.to_csv(destino, index=False)


def pleiades(destino: Path) -> None:
    gaia(PLEIADES_ADQL).to_csv(destino, index=False)


def kepler(destino: Path) -> None:
    import lightkurve as lk
    res = lk.search_lightcurve("Kepler-10", mission="Kepler", author="Kepler", exptime="long")
    if len(res) == 0:
        raise RuntimeError("lightkurve no encuentra curvas de Kepler-10")
    lc = res.download_all(download_dir=str(DATOS / "lightkurve_cache")).stitch().remove_nans()
    df = lc.to_pandas().reset_index()[["time", "flux", "flux_err", "quality"]]
    df.to_csv(destino, index=False)


TAREAS = {
    "hr": ("hr_hipparcos.csv", hr),
    "gaia": ("gaia_pleiades.csv", pleiades),
    "kepler": ("kepler10_curva_luz.csv", kepler),
}


def main(argv: list[str]) -> int:
    forzar = "--forzar" in argv
    elegidas = [a for a in argv if not a.startswith("--")] or list(TAREAS)
    DATOS.mkdir(exist_ok=True)
    fallos = 0
    for nombre in elegidas:
        fichero, funcion = TAREAS[nombre]
        destino = DATOS / fichero
        if destino.exists() and not forzar:
            print(f"{nombre}: ya está ({destino.name})")
            continue
        print(f"{nombre}: descargando…", flush=True)
        try:
            funcion(destino)
            filas = sum(1 for _ in destino.open(encoding="utf-8")) - 1
            print(f"{nombre}: {destino.name} · {filas} filas · {destino.stat().st_size / 1e6:.1f} MB")
        except Exception as e:  # noqa: BLE001  (network / archive down: report and go on)
            fallos += 1
            print(f"{nombre}: ERROR {type(e).__name__}: {e}", file=sys.stderr)
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
