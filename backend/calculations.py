"""
SICAF - Motor de Cálculo v2.2
Fórmulas oficiales F-01 a F-16 de la Especificación Maestra
"""
from decimal import Decimal, ROUND_HALF_UP

def to_decimal(val, decimals=3) -> Decimal:
    if val is None:
        return Decimal("0.000")
    if isinstance(val, (int, float, str)):
        return Decimal(str(val)).quantize(Decimal(10) ** -decimals, rounding=ROUND_HALF_UP)
    return val

def f01_rendimiento_etapa(peso_inicial: float, peso_final: float) -> float:
    """F-01 Rendimiento de etapa: R = (Pf / Pi) * 100"""
    if not peso_inicial or peso_inicial <= 0:
        return 0.0
    return round((peso_final / peso_inicial) * 100, 3)

def f02_merma_etapa_kg(peso_inicial: float, peso_final: float) -> float:
    """F-02 Merma de etapa en kg: M_kg = Pi - Pf"""
    return round(max(0.0, peso_inicial - peso_final), 3)

def f03_merma_porcentual(peso_inicial: float, peso_final: float) -> float:
    """F-03 Merma porcentual: M = (M_kg / Pi) * 100 = 100 - R"""
    if not peso_inicial or peso_inicial <= 0:
        return 0.0
    return round(((peso_inicial - peso_final) / peso_inicial) * 100, 3)

def f04_rendimiento_acumulado(rendimientos_fraccion: list[float]) -> float:
    """F-04 Rendimiento acumulado: R_acum = R1 * R2 * ... * Rn"""
    if not rendimientos_fraccion:
        return 0.0
    acum = 1.0
    for r in rendimientos_fraccion:
        acum *= r
    return round(acum * 100, 3)

def f05_f06_balance_masa(pi: float, producto: float, subproductos: float, descarte: float, muestra: float) -> dict:
    """
    F-05 Pi = sum(prod) + sum(subprod) + sum(descarte) + sum(muestra) + Residual
    F-06 Residual % = (Residual / Pi) * 100
    """
    salidas_pesadas = producto + subproductos + descarte + muestra
    residual = round(pi - salidas_pesadas, 3)
    residual_pct = round((residual / pi) * 100, 3) if pi > 0 else 0.0
    return {
        "peso_inicial": pi,
        "salidas_pesadas": salidas_pesadas,
        "residual_kg": residual,
        "residual_pct": residual_pct
    }

def f07_normalizacion_humedad(peso_real: float, humedad_real: float, humedad_ref: float = 12.0) -> float:
    """F-07 P_norm = P_real * (100 - H_real) / (100 - H_ref)"""
    if not peso_real or humedad_ref >= 100:
        return 0.0
    return round(peso_real * (100.0 - humedad_real) / (100.0 - humedad_ref), 3)

def f14_pago_por_kilo(kg: float, tarifa_kg: float) -> float:
    """F-14 Pago por kilo: kg * tarifa"""
    return round(kg * tarifa_kg, 2)

def f15_pago_por_jornada(fraccion_jornada: float, tarifa_jornada: float) -> float:
    """F-15 Pago por jornada: fraccion * tarifa (0.25, 0.50, 0.75, 1.00)"""
    return round(fraccion_jornada * tarifa_jornada, 2)

def f16_neto_semanal(bruto: float, bonos: float = 0.0, deducciones: float = 0.0, adelantos: float = 0.0) -> float:
    """F-16 Neto semanal = Pagos diarios + Bonos - Deducciones - Adelantos"""
    return round(bruto + bonos - deducciones - adelantos, 2)
