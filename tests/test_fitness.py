"""Fitness functions del Lab 08 ejecutables con pytest o unittest estándar."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fitness.academica import simular_caida
from fitness.catalogo import simular_catalogo
from fitness.estructura import comprobar_regla, detectar_infracciones
from fitness.seguridad import EMISOR_PERMITIDO, identidad_autorizada, simular_intentos_externos


class FitnessEstructural(unittest.TestCase):
    def test_ff01_dominio_no_importa_adaptadores(self):
        self.assertEqual(comprobar_regla(RAIZ, "FF-01"), [])

    def test_ff02_adaptadores_no_importan_servicio(self):
        self.assertEqual(comprobar_regla(RAIZ, "FF-02"), [])

    def test_demostracion_detecta_violacion_controlada(self):
        codigo = "from reservas.servicio import ServicioReservas\n"
        self.assertTrue(detectar_infracciones("validadores", codigo, "FF-02"))


class FitnessDeCalidad(unittest.TestCase):
    def test_ff03_disponibilidad_con_cache_reciente(self):
        resultado = simular_caida(estrategia="respaldo")
        self.assertEqual(resultado["bloqueadas_con_cache"], 0)
        self.assertLessEqual(resultado["espera_max_s"], 3)
        self.assertLessEqual(resultado["plazo_reverificacion_min"], 30)
        self.assertEqual(resultado["reverificaciones_fuera_30m"], 0)

    def test_ff04_catalogo_p95_presupuesto(self):
        resultado = simular_catalogo(indice=True)
        self.assertLessEqual(resultado["p95_ms"], 1500)

    def test_ff05_identidades_externas_sin_acceso(self):
        intentos = simular_intentos_externos()
        self.assertEqual(intentos["rechazados"], 30)
        self.assertEqual(intentos["autorizados"], 0)
        self.assertTrue(identidad_autorizada("estudiante@unsa.edu.pe", EMISOR_PERMITIDO, True, True))
        self.assertFalse(identidad_autorizada("estudiante@unsa.edu.pe", EMISOR_PERMITIDO, True, False))


if __name__ == "__main__":
    unittest.main(verbosity=2)
