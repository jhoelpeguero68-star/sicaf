"""
SICAF - Motor de Cálculo v2.2 Oficial
Implementación estricta de las Fórmulas F-01 a F-16 y Métodos de la Especificación Maestra
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional

def to_d(val, decimals: int = 3) -> Decimal:
    """Convierte a Decimal con precisión estricta para evitar error de punto flotante"""
    if val is None:
        return Decimal("0.000")
    if isinstance(val, (int, float, str)):
        return Decimal(str(val)).quantize(Decimal(10) ** -decimals, rounding=ROUND_HALF_UP)
    return val

def f01_rendimiento_etapa(peso_inicial: float, peso_final: float) -> float:
    """F-01 Rendimiento de etapa: R = (Pf / Pi) * 100"""
    if not peso_inicial or peso_inicial <= 0:
        return 0.0
    return float(round(Decimal(str(peso_final)) / Decimal(str(peso_inicial)) * 100, 3))

def f02_merma_etapa_kg(peso_inicial: float, peso_final: float) -> float:
    """F-02 Merma de etapa en kg: M_kg = Pi - Pf"""
    pi = Decimal(str(peso_inicial or 0))
    pf = Decimal(str(peso_final or 0))
    return float(round(max(Decimal("0.0"), pi - pf), 3))

def f03_merma_porcentual(peso_inicial: float, peso_final: float) -> float:
    """F-03 Merma porcentual: M = (M_kg / Pi) * 100 = 100 - R"""
    if not peso_inicial or peso_inicial <= 0:
        return 0.0
    pi = Decimal(str(peso_inicial))
    pf = Decimal(str(peso_final))
    return float(round(((pi - pf) / pi) * 100, 3))

def f04_rendimiento_acumulado(rendimientos_fraccion: List[float]) -> float:
    """
    F-04 Rendimiento acumulado: R_acum = R1 * R2 * ... * Rn
    Producto de los rendimientos de etapa (en fracción). Nunca se suman mermas.
    """
    if not rendimientos_fraccion:
        return 0.0
    acum = Decimal("1.0")
    for r in rendimientos_fraccion:
        acum *= Decimal(str(r))
    return float(round(acum * 100, 3))

def f05_f06_balance_masa(
    pi: float,
    producto: float,
    subproductos: float = 0.0,
    descarte: float = 0.0,
    muestra: float = 0.0
) -> Dict[str, Any]:
    """
    F-05 Pi = sum(producto) + sum(subproductos) + sum(descarte) + sum(muestra) + Residual
    F-06 Residual % = (Residual / Pi) * 100
    """
    pi_d = Decimal(str(pi or 0))
    prod_d = Decimal(str(producto or 0))
    sub_d = Decimal(str(subproductos or 0))
    desc_d = Decimal(str(descarte or 0))
    mues_d = Decimal(str(muestra or 0))

    salidas_pesadas = prod_d + sub_d + desc_d + mues_d
    residual = pi_d - salidas_pesadas
    residual_pct = (residual / pi_d * 100) if pi_d > 0 else Decimal("0.0")

    return {
        "peso_inicial": float(pi_d),
        "salidas_pesadas": float(salidas_pesadas),
        "residual_kg": float(round(residual, 3)),
        "residual_pct": float(round(residual_pct, 3))
    }

def f07_normalizacion_humedad(peso_real: float, humedad_real: float, humedad_ref: float = 12.0) -> float:
    """F-07 P_norm = P_real * (100 - H_real) / (100 - H_ref)"""
    if not peso_real or humedad_ref >= 100:
        return 0.0
    p = Decimal(str(peso_real))
    hr = Decimal(str(humedad_real))
    href = Decimal(str(humedad_ref))
    norm = p * (Decimal("100.0") - hr) / (Decimal("100.0") - href)
    return float(round(norm, 3))

def f08_factor_rendimiento(p_pergamino_seco: float, p_oro_primera: float, u: float = 70.0) -> float:
    """F-08 Factor de rendimiento: FR = U * (P_pergamino_seco / P_oro_primera)"""
    if not p_oro_primera or p_oro_primera <= 0:
        return 0.0
    ps = Decimal(str(p_pergamino_seco))
    po = Decimal(str(p_oro_primera))
    u_dec = Decimal(str(u))
    fr = u_dec * (ps / po)
    return float(round(fr, 2))

def f09_rendimiento_encadenado(rendimientos_antes: List[float], rendimientos_despues: List[float]) -> float:
    """
    F-09 R_global(c) = Pi(R_etapa_antes(c)) * Pi(R_etapa_después(lote))
    Calcula el rendimiento de un campo participante en una mezcla.
    """
    acum = Decimal("1.0")
    for r in rendimientos_antes:
        acum *= Decimal(str(r))
    for r in rendimientos_despues:
        acum *= Decimal(str(r))
    return float(round(acum * 100, 4))

def f10_asignacion_lote_mezclado(cantidad_producto: float, peso_campo_en_mezcla: float, peso_total_mezcla: float) -> float:
    """F-10 A_c = Q * (w_c / sum(w_j))"""
    if not peso_total_mezcla or peso_total_mezcla <= 0:
        return 0.0
    q = Decimal(str(cantidad_producto))
    wc = Decimal(str(peso_campo_en_mezcla))
    wt = Decimal(str(peso_total_mezcla))
    return float(round(q * (wc / wt), 3))

def f11_rendimiento_periodo(total_pf: float, total_pi: float) -> float:
    """F-11 R_periodo = sum(Pf) / sum(Pi) * 100 (Nunca promedio simple de porcentajes)"""
    if not total_pi or total_pi <= 0:
        return 0.0
    return float(round(Decimal(str(total_pf)) / Decimal(str(total_pi)) * 100, 3))

def f12_productividad_superficie(kg_cereza: float, tareas: float) -> Dict[str, float]:
    """
    F-12 Productividad por superficie: kg / tarea y kg / ha
    1 tarea dominicana = 628.86 m2 = 0.062886 hectáreas.
    """
    if not tareas or tareas <= 0:
        return {"kg_tarea": 0.0, "kg_ha": 0.0}
    kg = Decimal(str(kg_cereza))
    t = Decimal(str(tareas))
    kg_tarea = kg / t
    # 1 ha = 10000 m2 / 628.86 m2 = 15.90179 tareas
    ha = t * Decimal("0.062886")
    kg_ha = kg / ha if ha > 0 else Decimal("0.0")
    return {
        "kg_tarea": float(round(kg_tarea, 2)),
        "kg_ha": float(round(kg_ha, 2))
    }

def f13_productividad_trabajador(kg_totales: float, numero_trabajadores: int, dias_jornada: float = 1.0) -> float:
    """F-13 Productividad por trabajador y jornada: kg / (trabajador * dia)"""
    denom = Decimal(str(numero_trabajadores)) * Decimal(str(dias_jornada))
    if denom <= 0:
        return 0.0
    return float(round(Decimal(str(kg_totales)) / denom, 2))

def f14_pago_por_kilo(kg: float, tarifa_kg: float) -> float:
    """F-14 Pago por kilo: kg * tarifa vigente"""
    k = Decimal(str(kg or 0))
    t = Decimal(str(tarifa_kg or 0))
    return float(round(k * t, 2))

def f15_pago_por_jornada(fraccion_jornada: float, tarifa_jornada: float) -> float:
    """F-15 Pago por jornada: fraccion * tarifa (fracciones válidas: 0.25, 0.50, 0.75, 1.00)"""
    f = Decimal(str(fraccion_jornada or 0))
    t = Decimal(str(tarifa_jornada or 0))
    return float(round(f * t, 2))

def f16_neto_semanal(bruto: float, bonos: float = 0.0, deducciones: float = 0.0, adelantos: float = 0.0) -> float:
    """F-16 Neto semanal = Pagos diarios + Bonos - Deducciones - Adelantos"""
    b = Decimal(str(bruto or 0))
    bo = Decimal(str(bonos or 0))
    de = Decimal(str(deducciones or 0))
    ad = Decimal(str(adelantos or 0))
    return float(round(b + bo - de - ad, 2))

def conversion_presentacion_kg(unidad: str, valor: float) -> float:
    """
    Convierte unidades de empaque comerciales a kg netos:
    1 oz = 0.0283495 kg (7 oz = 0.1984 kg, 12 oz = 0.3402 kg)
    1 lb = 0.453592 kg (2.5 lb = 1.1340 kg)
    g = valor / 1000
    """
    v = Decimal(str(valor))
    u = unidad.lower().strip()
    if u in ["oz", "onzas"]:
        return float(round(v * Decimal("0.0283495"), 4))
    elif u in ["lb", "libras"]:
        return float(round(v * Decimal("0.453592"), 4))
    elif u in ["g", "gramos"]:
        return float(round(v / Decimal("1000.0"), 4))
    elif u in ["kg", "kilos"]:
        return float(round(v, 4))
    return float(round(v, 4))
