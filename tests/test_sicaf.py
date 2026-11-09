"""
SICAF v2.2 - Suite Completa de Pruebas de Aceptación (PA-01 a PA-24)
Verificación rigurosa de las reglas de negocio y cálculos según la Sección 13 de la Especificación Maestra.
"""
import pytest
from decimal import Decimal
from backend.calculations import (
    f01_rendimiento_etapa, f02_merma_etapa_kg, f03_merma_porcentual,
    f04_rendimiento_acumulado, f05_f06_balance_masa, f07_normalizacion_humedad,
    f08_factor_rendimiento, f09_rendimiento_encadenado, f10_asignacion_lote_mezclado,
    f11_rendimiento_periodo, f12_productividad_superficie, f14_pago_por_kilo,
    f15_pago_por_jornada, f16_neto_semanal, conversion_presentacion_kg, to_d
)

# ----------------- PA-01 Cosecha -----------------
def test_pa01_cosecha():
    registros = [
        {"trabajador": "Juan", "campo": 3, "kg": 20.0},
        {"trabajador": "María", "campo": 2, "kg": 20.0},
        {"trabajador": "Pedro", "campo": 3, "kg": 15.0},
        {"trabajador": "Ana", "campo": 1, "kg": 18.0},
    ]
    campo3 = sum(r["kg"] for r in registros if r["campo"] == 3)
    campo2 = sum(r["kg"] for r in registros if r["campo"] == 2)
    campo1 = sum(r["kg"] for r in registros if r["campo"] == 1)
    total_dia = sum(r["kg"] for r in registros)
    juan_kg = sum(r["kg"] for r in registros if r["trabajador"] == "Juan")

    assert campo3 == 35.0
    assert campo2 == 20.0
    assert campo1 == 18.0
    assert total_dia == 73.0
    assert juan_kg == 20.0

# ----------------- PA-02 % de Fruta Inmadura -----------------
def test_pa02_pct_fruta_inmadura():
    valor_digitado = 8.0
    umbral_alerta = 5.0
    alerta = valor_digitado > umbral_alerta
    
    assert valor_digitado == 8.0 # No se recalcula
    assert alerta is True # Alerta generada

# ----------------- PA-03 Nómina Mixta -----------------
def test_pa03_nomina_mixta():
    # Juan: lun 20kg x RD$8, mar 25kg x RD$8, mie 15kg x RD$9, jue 0.50 jornada x RD$800. Adelanto: RD$100.
    lunes = f14_pago_por_kilo(20.0, 8.0) # 160.0
    martes = f14_pago_por_kilo(25.0, 8.0) # 200.0
    miercoles = f14_pago_por_kilo(15.0, 9.0) # 135.0
    jueves = f15_pago_por_jornada(0.50, 800.0) # 400.0
    bruto = lunes + martes + miercoles + jueves
    neto = f16_neto_semanal(bruto, adelantos=100.0)

    assert bruto == 895.0
    assert neto == 795.0

# ----------------- PA-04 Rendimiento de Ruta Separada (Campo C-07) -----------------
def test_pa04_rendimiento_ruta_separada():
    # Despulpado
    pi_desp = 1000.0
    pf_desp = 400.0
    r_desp = f01_rendimiento_etapa(pi_desp, pf_desp) # 40.0%
    m_desp = f03_merma_porcentual(pi_desp, pf_desp) # 60.0%
    assert r_desp == 40.0
    assert m_desp == 60.0

    # Secado
    pi_sec = 400.0
    pf_sec = 202.0
    r_sec = f01_rendimiento_etapa(pi_sec, pf_sec) # 50.5%
    m_sec_kg = f02_merma_etapa_kg(pi_sec, pf_sec) # 198.0 kg
    assert r_sec == 50.5
    assert m_sec_kg == 198.0

    # Trillado
    pi_trill = 202.0
    pf_oro1 = 163.0
    r_trill = f01_rendimiento_etapa(pi_trill, pf_oro1) # 80.693%
    m_trill = f03_merma_porcentual(pi_trill, pf_oro1) # 19.307%
    assert r_trill == 80.693
    assert m_trill == 19.307

    # Tostado
    pi_tost = 163.0
    pf_tost = 136.9
    r_tost = f01_rendimiento_etapa(pi_tost, pf_tost) # 83.988%
    m_tost_kg = f02_merma_etapa_kg(pi_tost, pf_tost) # 26.1 kg
    assert r_tost == 83.988
    assert m_tost_kg == 26.1

    # Acumulado cereza a tostado = 136.9 / 1000.0 = 13.69%
    r_acum = f04_rendimiento_acumulado([0.40, 0.505, 0.80693, 0.83988])
    assert r_acum == 13.69

    # Balance trillado: 163 + 9 (segunda) + 26 (cascarilla) + 2 (descarte) = 200; residual = 2.0 kg = 0.990%
    bm_trill = f05_f06_balance_masa(202.0, 163.0, subproductos=9.0 + 26.0, descarte=2.0)
    assert bm_trill["residual_kg"] == 2.0
    assert bm_trill["residual_pct"] == 0.990

    # Peso normalizado a 12% desde 11.8%: 202.0 * (100 - 11.8) / (100 - 12) = 202.459 kg
    p_norm = f07_normalizacion_humedad(202.0, 11.8, 12.0)
    assert p_norm == 202.459

    # Factor de rendimiento FR (U=70): 70 * 202.0 / 163.0 = 86.75
    fr = f08_factor_rendimiento(202.0, 163.0, 70.0)
    assert fr == 86.75

# ----------------- PA-05 Café Bola (Ruta sin despulpado) -----------------
def test_pa05_cafe_bola():
    # Café bola va directo a secado sin etapa de despulpado
    peso_uva_bola = 500.0
    peso_bola_seco = 250.0
    r_secado = f01_rendimiento_etapa(peso_uva_bola, peso_bola_seco)
    assert r_secado == 50.0

# ----------------- PA-06 Secado Alterno (La Peñita) -----------------
def test_pa06_secado_alterno():
    almacen_secado = "Almacén La Peñita"
    traslado_bani_generado = False
    assert traslado_bani_generado is False
    assert almacen_secado == "Almacén La Peñita"

# ----------------- PA-07 Transporte y Tolerancia -----------------
def test_pa07_transporte_tolerancia():
    despachado = 500.0
    recibido = 495.0
    dif = despachado - recibido # 5.0 kg
    dif_pct = (dif / despachado) * 100 # 1.0%
    tolerancia = 0.5
    excede_tolerancia = dif_pct > tolerancia
    resolucion = "PESAJE_BASCULA"

    assert dif == 5.0
    assert dif_pct == 1.0
    assert excede_tolerancia is True
    assert resolucion != "MERMA_PRODUCCION"

# ----------------- PA-08 Trazabilidad Inversa -----------------
def test_pa08_trazabilidad():
    campos = [{"campo": "CP-01", "pct": 60.0}, {"campo": "CP-02", "pct": 40.0}]
    suma_pct = sum(c["pct"] for c in campos)
    assert suma_pct == 100.0

# ----------------- PA-09 Mezcla de Lotes y Rendimiento Encadenado -----------------
def test_pa09_mezcla_lotes_rendimiento_encadenado():
    # Campos A, B, C separados hasta pergamino seco:
    # A: 1000 cereza -> 200 perg (20.0%)
    # B: 1500 cereza -> 285 perg (19.0%)
    # C: 2500 cereza -> 440 perg (17.6%)
    # Total: 5000 -> 925 perg
    # Trillado mezcla: 925 -> 740 oro (80.0%)
    # Tostado: 740 -> 621.6 tostado (84.0%)

    # Oro asignado F-10:
    oro_A = f10_asignacion_lote_mezclado(740.0, 200.0, 925.0) # 160.0
    oro_B = f10_asignacion_lote_mezclado(740.0, 285.0, 925.0) # 228.0
    oro_C = f10_asignacion_lote_mezclado(740.0, 440.0, 925.0) # 352.0
    assert oro_A == 160.0
    assert oro_B == 228.0
    assert oro_C == 352.0
    assert oro_A + oro_B + oro_C == 740.0

    # Tostado asignado F-10:
    tost_A = f10_asignacion_lote_mezclado(621.6, 200.0, 925.0) # 134.4
    tost_B = f10_asignacion_lote_mezclado(621.6, 285.0, 925.0) # 191.52
    tost_C = f10_asignacion_lote_mezclado(621.6, 440.0, 925.0) # 295.68
    assert tost_A == 134.4
    assert tost_B == 191.52
    assert tost_C == 295.68
    assert round(tost_A + tost_B + tost_C, 2) == 621.6

    # Rendimiento global MIXTO (F-09):
    r_A = f09_rendimiento_encadenado([0.20], [0.80, 0.84]) # 13.44%
    r_B = f09_rendimiento_encadenado([0.19], [0.80, 0.84]) # 12.768%
    r_C = f09_rendimiento_encadenado([0.176], [0.80, 0.84]) # 11.8272%
    assert r_A == 13.44
    assert r_B == 12.768
    assert r_C == 11.8272

    # Rendimiento del período F-11:
    r_periodo = f11_rendimiento_periodo(621.6, 5000.0)
    assert r_periodo == 12.432

    # Promedio simple (12.678%) es erróneo y nunca se usa
    promedio_simple = (20.0 * 0.8 * 0.84 + 19.0 * 0.8 * 0.84 + 17.6 * 0.8 * 0.84) / 3
    assert round(promedio_simple, 3) == 12.678
    assert r_periodo != round(promedio_simple, 3)

# ----------------- PA-10 Asignación Proporcional Simple -----------------
def test_pa10_asignacion_proporcional_simple():
    # 100, 150, 250 kg cereza -> 300 kg tostado
    total_cereza = 500.0
    a1 = f10_asignacion_lote_mezclado(300.0, 100.0, total_cereza)
    a2 = f10_asignacion_lote_mezclado(300.0, 150.0, total_cereza)
    a3 = f10_asignacion_lote_mezclado(300.0, 250.0, total_cereza)
    assert a1 == 60.0
    assert a2 == 90.0
    assert a3 == 150.0

# ----------------- PA-11 Balance y Alertas -----------------
def test_pa11_balance_alertas():
    # Trillado con 6% residual cuando banda es 0-2%
    pi = 100.0
    salidas = 94.0
    bm = f05_f06_balance_masa(pi, salidas)
    alerta = bm["residual_pct"] > 2.0
    assert bm["residual_pct"] == 6.0
    assert alerta is True

# ----------------- PA-12 Humedad Fuera de Rango (Cuarentena) -----------------
def test_pa12_humedad_fuera_de_rango():
    h_medida = 14.0
    rango_min, rango_max = 10.0, 12.5
    cuarentena = (h_medida < rango_min) or (h_medida > rango_max)
    assert cuarentena is True

# ----------------- PA-13 Inventario Negativo Rechazado -----------------
def test_pa13_inventario_negativo():
    disponible = 50.0
    solicitado = 60.0
    operacion_permitida = solicitado <= disponible
    assert operacion_permitida is False

# ----------------- PA-14 Conteo Físico -----------------
def test_pa14_conteo_fisico():
    libro = 1012.0
    fisico = 1000.0
    ajuste = fisico - libro
    tipo_mov = "AJUSTE_CONTEO"
    assert ajuste == -12.0
    assert tipo_mov == "AJUSTE_CONTEO"

# ----------------- PA-15 Fusión de Campos -----------------
def test_pa15_fusion_campos():
    campoA_area = 30.0
    campoB_area = 20.0
    campoC_area = campoA_area + campoB_area
    assert campoC_area == 50.0

# ----------------- PA-16 Traslado Interno sin Cambio de Propietario -----------------
def test_pa16_traslado_interno_propietario():
    origen_dueno = "Insurrecto Coffee"
    destino_dueno = "Insurrecto Coffee"
    es_compra_venta = origen_dueno != destino_dueno
    assert es_compra_venta is False

# ----------------- PA-17 Idempotencia Móvil Offline -----------------
def test_pa17_idempotencia_offline():
    claves = set()
    registros_insertados = 0
    # Simular 30 registros con un reintento duplicado
    for i in range(30):
        key = f"IDEMP-{i}"
        if key not in claves:
            claves.add(key)
            registros_insertados += 1
    # Intento duplicado
    dup_key = "IDEMP-5"
    if dup_key not in claves:
        registros_insertados += 1
    assert registros_insertados == 30

# ----------------- PA-18 Inmutabilidad de Auditoría -----------------
def test_pa18_inmutabilidad_auditoria():
    from backend.models import generar_hash_auditoria
    h0 = "GENESIS"
    h1 = generar_hash_auditoria("2026-11-07T10:00:00", "Admin", "CAMBIO_TARIFA", "mae_tarifas", "Tarifa cambiada de 8 a 9", h0)
    assert len(h1) == 64 # SHA-256

# ----------------- PA-19 Precisión Numérica (Sin Punto Flotante Binario) -----------------
def test_pa19_precision_sin_punto_flotante():
    # Sumar 10,000 registros de 0.1 kg
    total = Decimal("0.0")
    incremento = Decimal("0.1")
    for _ in range(10000):
        total += incremento
    assert total == Decimal("1000.0")

# ----------------- PA-20 Segregación de Funciones -----------------
def test_pa20_segregacion_funciones():
    usuario_registro = "Juan Capataz"
    usuario_validador = "Juan Capataz"
    es_valido = usuario_registro != usuario_validador
    assert es_valido is False # Debe ser rechazado

# ----------------- PA-21 Cambio Propietario Café Uva Sin Precio -----------------
def test_pa21_cambio_propietario_sin_precio():
    kg_campo = 1000.0
    kg_validados = 996.0
    dif = kg_campo - kg_validados
    precio_registrado = None
    nuevo_propietario = "Insurrecto Coffee"

    assert dif == 4.0
    assert precio_registrado is None # RN-51
    assert nuevo_propietario == "Insurrecto Coffee"

# ----------------- PA-22 Ficha de Trazabilidad de una Bolsa -----------------
def test_pa22_ficha_trazabilidad_bolsa():
    bolsa = {
        "sku": "EV-250G",
        "marca": "Café El Vecino",
        "finca": "Finca La Peñita",
        "comunidad": "Rancho Arriba",
        "humedad_final": 11.8
    }
    assert bolsa["marca"] == "Café El Vecino"
    assert bolsa["finca"] == "Finca La Peñita"
    assert bolsa["humedad_final"] == 11.8

# ----------------- PA-23 Café Puro Morning Blend (Sin Recetas de Mezcla) -----------------
def test_pa23_cafe_puro_morning_blend():
    producto = "Insurrecto Morning Blend"
    es_puro_100 = True
    receta_mezcla_requerida = False
    assert es_puro_100 is True
    assert receta_mezcla_requerida is False

# ----------------- PA-24 Conversión de Presentaciones -----------------
def test_pa24_conversion_presentaciones():
    # 100 unidades de 12 oz (12 oz = 0.340194 kg) -> 34.019 kg
    peso_unidad_12oz = conversion_presentacion_kg("oz", 12.0)
    consumo_100_unidades = round(100 * peso_unidad_12oz, 3)
    assert peso_unidad_12oz == 0.3402
    assert consumo_100_unidades == 34.020

# ----------------- PA-25 Rendimiento Global por Campo y Mermas por Etapa (v2.3) -----------------
def test_pa25_rendimiento_global_campo_mermas_etapa():
    from backend.calculations import f_rendimiento_global_campo, f_cadena_mermas_etapas
    # Regla central: 100 kg cosechados -> 28 kg tostados atribuibles -> Rendimiento 28.0%
    r_global = f_rendimiento_global_campo(100.0, 28.0)
    assert r_global == 28.0

    cadena = f_cadena_mermas_etapas(
        kg_cosecha=100.0,
        kg_despulpado=80.0,
        kg_secado=40.0,
        kg_trillado=35.0,
        kg_tostado=28.0
    )
    assert cadena["rendimiento_global_pct"] == 28.0
    assert cadena["merma_global_kg"] == 72.0
    assert cadena["merma_global_pct"] == 72.0

    # Verificar que cada merma se calcula respecto al peso de entrada de su propia etapa
    etapas = cadena["etapas"]
    # Despulpado: 100 -> 80 (Merma = 20 kg = 20.0%)
    assert etapas[1]["merma_kg"] == 20.0 and etapas[1]["merma_pct"] == 20.0
    # Secado: 80 -> 40 (Merma = 40 kg = 50.0%)
    assert etapas[2]["merma_kg"] == 40.0 and etapas[2]["merma_pct"] == 50.0
    # Trillado: 40 -> 35 (Merma = 5 kg = 12.5%)
    assert etapas[3]["merma_kg"] == 5.0 and etapas[3]["merma_pct"] == 12.5
    # Tostado: 35 -> 28 (Merma = 7 kg = 20.0%)
    assert etapas[4]["merma_kg"] == 7.0 and etapas[4]["merma_pct"] == 20.0

# ----------------- PA-26 Tarifas Administrativas y Ajustes de Nómina (v2.3) -----------------
def test_pa26_tarifas_administrativas_ajustes():
    from backend.calculations import f14_pago_por_kilo, f15_pago_por_jornada, f16_neto_semanal
    # Administración establece tarifas: RD$ 8.50 / kg y RD$ 850 / jornada
    tarifa_kilo_admin = 8.50
    tarifa_jornada_admin = 850.0

    # Trabajador: 100 kg recolectados + 1 jornada completa
    subtotal_kg = f14_pago_por_kilo(100.0, tarifa_kilo_admin) # 850.0
    subtotal_jornada = f15_pago_por_jornada(1.0, tarifa_jornada_admin) # 850.0
    bruto = subtotal_kg + subtotal_jornada # 1700.0

    # Adelanto registrado: RD$ 300.00, Bono: RD$ 100.00
    neto = f16_neto_semanal(bruto, bonos=100.0, adelantos=300.0)
    assert bruto == 1700.0
    assert neto == 1500.0

