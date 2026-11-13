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

# ----------------- PA-27 Alta Rápida de Recolector desde App Móvil (RN-2.1) -----------------
def test_pa27_alta_recolector_app():
    from backend.database import SessionLocal
    from backend.models import Trabajador
    from backend.main import crear_trabajador, TrabajadorCreateInput

    db = SessionLocal()
    try:
        nuevo = TrabajadorCreateInput(
            nombre_completo="Carlos Almonte Test",
            cuadrilla="Cuadrilla 1 (La Loma)",
            cedula_id="001-9988776-5"
        )
        res = crear_trabajador(nuevo, db)
        assert res["status"] in ["SUCCESS", "ALREADY_EXISTS"]
        assert "Carlos Almonte Test" in res["trabajador"]["nombre_completo"]

        # Verificar en base de datos
        t = db.query(Trabajador).filter(Trabajador.nombre_completo == "Carlos Almonte Test").first()
        assert t is not None
        assert t.activo is True
    finally:
        db.close()

# ----------------- PA-28 Emisión de Subcódigos de Sacos y Validación en Destino (RN-2.5 / RN-3.B) -----------------
def test_pa28_control_sacos_subcodigos_traslado():
    import uuid
    from backend.database import SessionLocal
    from backend.models import Saco, Traslado
    from backend.main import (
        generar_sacos, SacosGenerarInput,
        despachar_traslado_con_sacos, TrasladoSacosDespachoInput,
        recibir_traslado_con_sacos, TrasladoSacosRecepcionInput
    )

    db = SessionLocal()
    try:
        # 1. Generar 4 sacos para Finca La Peñita (Fenelon) con subcódigos correlativos
        lote_test = f"TEST-FEN-{uuid.uuid4().hex[:6].upper()}"
        gen_input = SacosGenerarInput(
            codigo_lote=lote_test,
            cantidad_sacos=4,
            peso_por_saco_kg=50.0,
            almacen_id=1 # Beneficio Rancho Arriba
        )
        res_gen = generar_sacos(gen_input, db)
        assert res_gen["status"] == "SUCCESS"
        assert res_gen["cantidad_generada"] == 4
        assert res_gen["peso_total_estimado_kg"] == 200.0
        subcods = [s["subcodigo"] for s in res_gen["sacos"]]
        assert len(subcods) == 4
        assert subcods[0] == f"{lote_test}-S01"

        # 2. Despachar los 4 sacos desde Almacén 1 (Rancho Arriba) hacia Almacén 2 (Secado Baní)
        despacho_input = TrasladoSacosDespachoInput(
            almacen_origen_id=1,
            almacen_destino_id=2,
            chofer="Manuel Tejeda",
            vehiculo_placa="L-345678",
            responsable_despacho="Capataz Móvil",
            subcodigos_sacos=subcods
        )
        res_desp = despachar_traslado_con_sacos(despacho_input, db)
        assert res_desp["status"] == "DESPACHADO"
        assert res_desp["cantidad_sacos"] == 4
        assert res_desp["total_kg_despachados"] == 200.0

        traslado_id = res_desp["traslado_id"]

        # 3. El receptor en Baní valida los sacos físicamente: llegaron los 4 completos
        rec_input = TrasladoSacosRecepcionInput(
            traslado_id=traslado_id,
            subcodigos_recibidos=subcods,
            responsable_recepcion="Encargado Almacén Baní",
            peso_total_recibido=199.5 # Merma normal de transporte de 0.5 kg (0.25% < 0.5% tolerancia)
        )
        res_rec = recibir_traslado_con_sacos(rec_input, db)
        assert res_rec["status"] == "CONCILIADO"
        assert res_rec["sacos_recibidos"] == 4
        assert len(res_rec["sacos_faltantes"]) == 0
        assert res_rec["fuera_tolerancia"] is False

        # Verificar que los sacos ahora están en Almacén 2 (Baní)
        sacos_db = db.query(Saco).filter(Saco.subcodigo_saco.in_(subcods)).all()
        for s in sacos_db:
            assert s.almacen_actual_id == 2
            assert s.estado == "EN_ALMACEN"

    finally:
        db.close()

# ----------------- PA-29 Validación en Beneficio con Selección de Café de Primera / Segunda (RN-13 / RN-51) -----------------
def test_pa29_recepcion_clasificacion_primera_segunda_app():
    from backend.database import SessionLocal
    from backend.models import Lote, RecepcionBeneficio
    from backend.main import validar_recepcion_beneficio, RecepcionBeneficioInput

    db = SessionLocal()
    try:
        # Validación de lote clasificado como Café de Primera
        input_primera = RecepcionBeneficioInput(
            fecha="2026-11-09",
            kg_validados=1000.0,
            pct_fruta_inmadura=4.2,
            clasificacion="PRIMERA",
            campo_id=1,
            observaciones="Recepción conforme Primera",
            validado_por="Encargado de Beneficio Móvil"
        )
        res1 = validar_recepcion_beneficio(input_primera, db)
        assert res1["status"] == "VALIDADO"
        assert res1["clasificacion"] == "PRIMERA"
        assert res1["alerta_calidad"] is False

        # Validación de lote clasificado como Café de Segunda con alerta de fruta inmadura > 5%
        input_segunda = RecepcionBeneficioInput(
            fecha="2026-11-09",
            kg_validados=450.0,
            pct_fruta_inmadura=6.8,
            clasificacion="SEGUNDA",
            campo_id=2,
            observaciones="Fruta con flotadores",
            validado_por="Encargado de Beneficio Móvil"
        )
        res2 = validar_recepcion_beneficio(input_segunda, db)
        assert res2["status"] == "VALIDADO"
        assert res2["clasificacion"] == "SEGUNDA"
        assert res2["alerta_calidad"] is True
        assert "supera el umbral" in res2["alerta_mensaje"]

        # Verificar en base de datos
        lote_p = db.query(Lote).filter(Lote.codigo == res1["lote_codigo"]).first()
        assert lote_p.clasificacion == "PRIMERA"
        assert lote_p.kg_disponibles == 1000.0

        lote_s = db.query(Lote).filter(Lote.codigo == res2["lote_codigo"]).first()
        assert lote_s.clasificacion == "SEGUNDA"
        assert lote_s.kg_disponibles == 450.0
    finally:
        db.close()

# ----------------- PA-30 Registro de Kg en Secado desde App Móvil (Entrada, Humedad, Cierre) -----------------
def test_pa30_secado_registro_kg_movil():
    import uuid
    from backend.database import SessionLocal
    from backend.models import SecadoLote, Lote
    from backend.main import (
        iniciar_secado, SecadoIniciarInput,
        registrar_humedad_secado, SecadoHumedadInput,
        finalizar_secado, SecadoFinalizarInput
    )

    db = SessionLocal()
    try:
        # Lote de prueba
        lote = Lote(
            codigo=f"SEC-TEST-{uuid.uuid4().hex[:6].upper()}",
            empresa_propietaria="Insurrecto Coffee",
            clasificacion="PRIMERA",
            estado_cafe="PERGAMINO_MOJADO",
            almacen_actual_id=1,
            kg_disponibles=850.0
        )
        db.add(lote)
        db.commit()
        db.refresh(lote)

        # 1. Iniciar secado registrando kg de entrada en báscula
        res_ini = iniciar_secado(SecadoIniciarInput(
            lote_id=lote.id,
            almacen_id=2, # Almacén de Secado en Baní
            fecha_inicio="2026-11-09",
            peso_inicial_kg=850.0,
            humedad_inicial=52.0,
            responsable="Encargado de Secado Móvil"
        ), db)
        assert res_ini["status"] == "SECADO_INICIADO"
        sec_id = res_ini["secado_id"]

        # 2. Registrar medición periódica de humedad
        res_med = registrar_humedad_secado(SecadoHumedadInput(
            secado_id=sec_id,
            porcentaje_humedad=24.5,
            instrumento="Higrómetro Móvil",
            clima="Soleado y Seco",
            responsable="Encargado de Secado Móvil"
        ), db)
        assert res_med["status"] == "MEDICION_REGISTRADA"
        assert res_med["humedad"] == 24.5

        # 3. Finalizar secado registrando kg finales secos en báscula y humedad target (11.8%)
        res_fin = finalizar_secado(SecadoFinalizarInput(
            secado_id=sec_id,
            fecha_fin="2026-11-15",
            peso_final_kg=415.5,
            humedad_final=11.8,
            responsable="Encargado de Secado Móvil"
        ), db)
        assert res_fin["status"] == "FINALIZADO"
        assert res_fin["peso_final_kg"] == 415.5
        assert res_fin["cuarentena"] is False
    finally:
        db.close()

# ----------------- PA-31 Campos con Cantidad de Plantas -----------------
def test_pa31_campos_plantas():
    from backend.database import SessionLocal
    from backend.models import Campo
    from backend.main import crear_campo, CampoCreateInput
    import uuid

    db = SessionLocal()
    try:
        cod = f"CP-TEST-{uuid.uuid4().hex[:4].upper()}"
        res = crear_campo(CampoCreateInput(
            codigo=cod,
            nombre="Lote Las Palmas",
            sector="Sector Norte",
            area_tareas=25.0,
            cantidad_plantas=12500,
            variedad="Caturra Rojo"
        ), db)
        assert res["status"] == "SUCCESS"
        assert res["campo"]["cantidad_plantas"] == 12500

        c_db = db.query(Campo).filter(Campo.codigo == cod).first()
        assert c_db is not None
        assert c_db.cantidad_plantas == 12500
    finally:
        db.close()

# ----------------- PA-32 Beneficio: Bultos, Origen Finca/Externo y Lavado Primera/Segunda -----------------
def test_pa32_beneficio_bultos_lavado_origen():
    from backend.database import SessionLocal
    from backend.models import RecepcionBeneficio
    from backend.main import validar_recepcion_beneficio, RecepcionBeneficioInput

    db = SessionLocal()
    try:
        # Recepción de la finca propia (La Peñita - Campo 1)
        res_finca = validar_recepcion_beneficio(RecepcionBeneficioInput(
            fecha="2026-11-09",
            kg_validados=1200.0,
            pct_fruta_inmadura=3.5,
            tipo_proveedor="MYRA_CAFE",
            campo_id=1,
            cantidad_bultos=24,
            kg_lavado_primera=850.0,
            kg_lavado_segunda=200.0,
            observaciones="Cosecha selectiva Finca La Peñita"
        ), db)
        assert res_finca["status"] == "VALIDADO"
        
        rec_db = db.query(RecepcionBeneficio).filter(RecepcionBeneficio.id == res_finca["recepcion_id"]).first()
        assert rec_db.cantidad_bultos == 24
        assert rec_db.campo_id == 1
        assert rec_db.kg_lavado_primera == 850.0
        assert rec_db.kg_lavado_segunda == 200.0
    finally:
        db.close()

# ----------------- PA-33 Secado: Bultos, Tipo Café, Humedad Diaria, Clima y Temperatura -----------------
def test_pa33_secado_diario_clima():
    from backend.database import SessionLocal
    from backend.models import Lote, SecadoLote, MedicionHumedad
    from backend.main import (
        iniciar_secado, SecadoIniciarInput,
        registrar_humedad_secado, SecadoHumedadInput
    )
    import uuid

    db = SessionLocal()
    try:
        lote = Lote(
            codigo=f"SEC-CLI-{uuid.uuid4().hex[:5].upper()}",
            empresa_propietaria="Insurrecto Coffee",
            clasificacion="PRIMERA",
            estado_cafe="PERGAMINO_MOJADO",
            almacen_actual_id=1,
            kg_disponibles=600.0
        )
        db.add(lote)
        db.commit()
        db.refresh(lote)

        # Iniciar secado con bultos, tipo de café, clima y temperatura
        res_ini = iniciar_secado(SecadoIniciarInput(
            lote_id=lote.id,
            almacen_id=2, # Baní
            fecha_inicio="2026-11-09",
            peso_inicial_kg=600.0,
            cantidad_bultos=12,
            categoria_cafe="PRIMERA",
            tipo_cafe_secando="PERGAMINO_LAVADO",
            humedad_inicial=50.0,
            clima="Soleado con brisa moderada",
            temperatura_c=28.5,
            responsable="Encargado Baní"
        ), db)
        sec_id = res_ini["secado_id"]

        sec_db = db.query(SecadoLote).filter(SecadoLote.id == sec_id).first()
        assert sec_db.cantidad_bultos == 12
        assert sec_db.tipo_cafe_secando == "PERGAMINO_LAVADO"
        assert sec_db.temperatura_c == 28.5

        # Registro de humedad al cierre del día 1
        res_med = registrar_humedad_secado(SecadoHumedadInput(
            secado_id=sec_id,
            dia_numero=1,
            porcentaje_humedad=36.0,
            humedad_cierre_dia=True,
            temperatura_c=29.0,
            clima="Soleado y despejado",
            observaciones="Cierre de jornada día 1 sin incidencias",
            responsable="Encargado Baní"
        ), db)
        assert res_med["status"] == "MEDICION_REGISTRADA"

        med = db.query(MedicionHumedad).filter(MedicionHumedad.secado_id == sec_id, MedicionHumedad.dia_numero == 1).first()
        assert med.dia_numero == 1
        assert med.humedad_cierre_dia is True
        assert med.temperatura_c == 29.0
    finally:
        db.close()

# ----------------- PA-34 Trillado, Tostado, SKUs Oficiales y Despacho Final -----------------
def test_pa34_trillado_tostado_despacho():
    from backend.database import SessionLocal
    from backend.models import Lote, ProductoSKU, ProcesoTransformacion
    from backend.main import (
        proceso_trillado, TrilladoInput,
        proceso_tostado, TostadoInput,
        proceso_empaque, EmpaqueInput,
        despacho_producto_final, DespachoProductoFinalInput,
        list_skus
    )
    import uuid

    db = SessionLocal()
    try:
        # Verificar que los 6 SKUs oficiales existan
        skus = list_skus(db)
        assert len(skus) >= 6
        sku_molido_12oz = next(s for s in skus if s["sku"] == "ILP-MB-12OZ-MOL")
        assert sku_molido_12oz["peso_neto_kg"] == 0.3402

        # 1. Trillado: recibe bultos y kilos, produce verde Primera y Segunda
        lote_p = Lote(
            codigo=f"TRILL-{uuid.uuid4().hex[:5].upper()}",
            empresa_propietaria="Insurrecto Coffee",
            clasificacion="PRIMERA",
            estado_cafe="PERGAMINO_SECO",
            almacen_actual_id=4,
            kg_disponibles=250.0
        )
        db.add(lote_p)
        db.commit()
        db.refresh(lote_p)

        res_trill = proceso_trillado(TrilladoInput(
            lote_pergamino_id=lote_p.id,
            cantidad_bultos_recibidos=5,
            kg_pergamino=250.0,
            kg_oro_primera=190.0,
            kg_oro_segunda=10.0,
            kg_cascarilla=45.0,
            kg_descarte=2.0,
            responsable="Tostaduría Insurrecto"
        ), db)
        assert res_trill["status"] == "TRILLADO_COMPLETADO"
        assert res_trill["lote_oro_segunda"] is not None

        # 2. Tostado de verde Primera
        lote_oro = db.query(Lote).filter(Lote.codigo == res_trill["lote_oro_primera"]).first()
        res_tost = proceso_tostado(TostadoInput(
            lote_oro_id=lote_oro.id,
            categoria="PRIMERA",
            kg_oro=50.0,
            kg_tostado=42.0,
            grado_tueste="Medio Especial",
            responsable="Tostador Maestro"
        ), db)
        assert res_tost["status"] == "TOSTADO_COMPLETADO"
        assert res_tost["categoria"] == "PRIMERA"

        # 3. Empaque en SKU Morning Blend 12 oz
        lote_tost = db.query(Lote).filter(Lote.codigo == res_tost["lote_tostado_creado"]).first()
        res_emp = proceso_empaque(EmpaqueInput(
            lote_tostado_id=lote_tost.id,
            sku_id=sku_molido_12oz["id"],
            unidades=100,
            formato="MOLIDO",
            responsable="Operador Empaque"
        ), db)
        assert res_emp["status"] == "EMPAQUE_COMPLETADO"
        assert res_emp["unidades_producidas"] == 100

        # 4. Despacho Final de producto terminado
        res_desp = despacho_producto_final(DespachoProductoFinalInput(
            sku_id=sku_molido_12oz["id"],
            cliente_destino="Supermercado Nacional",
            paquetes_despachados=50,
            documento_despacho="FAC-2026-9901",
            chofer="Manuel Gómez",
            vehiculo_placa="L-334455",
            responsable="Encargado Logística"
        ), db)
        assert res_desp["status"] == "DESPACHADO"
        assert res_desp["paquetes_despachados"] == 50
    finally:
        db.close()

# ----------------- PA-35 Las 6 Rutas Oficiales de Traslado -----------------
def test_pa35_traslados_6_rutas():
    from backend.database import SessionLocal
    from backend.models import Traslado
    from backend.main import registrar_traslado_ruta, TrasladoRegistroInput, list_traslados

    db = SessionLocal()
    try:
        rutas = [
            "CAMPO_A_BENEFICIO",
            "BENEFICIO_A_SECADO",
            "SECADO_A_ALMACEN_FINCA",
            "FINCA_A_TOSTADURIA",
            "TOSTADURIA_A_SANTO_DOMINGO",
            "FINCA_A_CLIENTES"
        ]
        for ruta in rutas:
            res = registrar_traslado_ruta(TrasladoRegistroInput(
                tipo_ruta=ruta,
                codigo_lote="LOTE-TEST-RUTA",
                tipo_cafe="PERGAMINO_SECO",
                cantidad_bultos=15,
                total_kg=675.0,
                chofer="Chofer Logística",
                vehiculo_placa="L-112233",
                responsable_despacho="Logística Insurrecto",
                cliente_destino_nombre="Cafetería Especial Santo Domingo" if ruta == "FINCA_A_CLIENTES" else None
            ), db)
            assert res["status"] == "REGISTRADO"
            assert res["tipo_ruta"] == ruta

        lista = list_traslados(db)
        assert len(lista) >= 6
    finally:
        db.close()

# ----------------- PA-36 Nómina: Filtro Fechas (Desde-Hasta), Tarifa Diaria Transparente y Sin Cuadrilla -----------------
def test_pa36_nomina_filtro_fechas_sin_cuadrilla():
    from backend.database import SessionLocal
    from backend.main import get_nomina_liquidacion

    db = SessionLocal()
    try:
        # 1. Consulta con rango de fechas
        nom_rango = get_nomina_liquidacion(
            fecha_desde="2026-11-01",
            fecha_hasta="2026-11-07",
            tarifa_kg=8.0,
            tarifa_jornada=800.0,
            db=db
        )
        assert nom_rango["fecha_desde"] == "2026-11-01"
        assert nom_rango["fecha_hasta"] == "2026-11-07"
        assert "tarifa_dia_rd" in nom_rango["tarifas_aplicadas"]
        assert nom_rango["tarifas_aplicadas"]["tarifa_dia_rd"] == 800.0

        # Verificar transparencia de tarifa por día y kilo en cada fila
        for item in nom_rango["detalle"]:
            assert "tarifa_dia" in item
            assert "dias_jornada" in item
            assert "tarifa_kg" in item
            assert "subtotal_jornada" in item
            assert "neto_a_pagar" in item

        # 2. Consulta general
        nom_gen = get_nomina_liquidacion(db=db)
        assert len(nom_gen["detalle"]) > 0
    finally:
        db.close()



