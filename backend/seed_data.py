"""
SICAF - Semillero Completo de Datos Oficiales (Seed Data v2.2)
Carga integral de:
- Empresas (Myra Café SRL e Insurrecto Coffee)
- Campaña Cosecha 2026-2027
- 25 Campos Oficiales (Anexo A) con áreas en tareas y altitudes
- Almacenes Oficiales (Anexo B)
- Catálogo de Productos y SKUs (Anexo B: Café El Vecino e Insurrecto Morning Blend)
- Productores Externos de café uva
- Tarifas vigentes (RD$ 8.00/kg y RD$ 800.00/jornada)
- Recolectores y personal
- Lotes en todas las etapas para trazabilidad completa (cereza, pergamino mojado, secado en Baní, pergamino seco, oro, tostado, empaque)
- Auditoría criptográfica (Hash chaining)
"""
from datetime import datetime, timedelta
from .database import SessionLocal, engine, Base
from .models import (
    Empresa, Usuario, Campana, Campo, Trabajador, ProductorExterno, Tarifa,
    Almacen, ProductoSKU, RegistroCosecha, RecepcionBeneficio, Lote, LoteCampo,
    MovimientoInventario, SecadoLote, MedicionHumedad, ProcesoTransformacion,
    LoteGenealogia, Traslado, TrasladoDetalle, AnalisisCalidad, NominaSemana,
    NominaDetalle, AuditoriaLog, generar_hash_auditoria
)
from .security import hash_password

def seed_all(force: bool = False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if not force and db.query(Campana).first():
        db.close()
        return

    # Limpiar tablas si es forzado
    if force:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    print("Cargando estructura maestra de datos SICAF v2.2...")

    # 1. Empresas
    myra = Empresa(nombre="Myra Café SRL", rnc="1-32-12345-1", tipo="AGRICOLA")
    insurrecto = Empresa(nombre="Insurrecto Coffee", rnc="1-32-98765-2", tipo="INDUSTRIAL")
    db.add_all([myra, insurrecto])
    db.commit()

    # 2. Campaña activa
    campana = Campana(nombre="Campaña 2026-2027", fecha_inicio="2026-10-01", estado="ACTIVA")
    db.add(campana)
    db.commit()

    # 3. Usuarios
    usuarios = [
        Usuario(nombre="Administrador General", email="admin@insurrecto.com", password_hash=hash_password("admin123"), rol="ADMIN"),
        Usuario(nombre="Capataz de Campo", email="campo@insurrecto.com", password_hash=hash_password("campo123"), rol="CAMPO"),
        Usuario(nombre="Encargado de Beneficio", email="beneficio@insurrecto.com", password_hash=hash_password("beneficio123"), rol="BENEFICIO"),
        Usuario(nombre="Encargado de Secado (Baní)", email="secado@insurrecto.com", password_hash=hash_password("secado123"), rol="SECADO"),
        Usuario(nombre="Encargado de Tostaduría", email="tostaduria@insurrecto.com", password_hash=hash_password("tostaduria123"), rol="TOSTADURIA"),
        Usuario(nombre="Encargada de Nómina", email="nomina@insurrecto.com", password_hash=hash_password("nomina123"), rol="NOMINA"),
        Usuario(nombre="Especialista de Calidad", email="calidad@insurrecto.com", password_hash=hash_password("calidad123"), rol="CALIDAD"),
        Usuario(nombre="Auditor Interno", email="auditor@insurrecto.com", password_hash=hash_password("auditor123"), rol="AUDITOR"),
    ]
    db.add_all(usuarios)
    db.commit()

    # 4. Almacenes oficiales (Anexo B)
    alm_beneficio = Almacen(id=1, nombre="Almacén Beneficio (Recepción Café Uva)", empresa="Insurrecto Coffee", tipo="PROPIO", ubicacion="Finca La Peñita, Rancho Arriba (San José de Ocoa)")
    alm_secado_bani = Almacen(id=2, nombre="Almacén de Secado – Baní", empresa="Insurrecto Coffee", tipo="PROPIO", ubicacion="Baní, Peravia (Clima Seco y Cálido)")
    alm_pergamino = Almacen(id=3, nombre="Almacén de Pergamino", empresa="Insurrecto Coffee", tipo="PROPIO", ubicacion="Finca La Peñita, Rancho Arriba (San José de Ocoa)")
    alm_tostaduria = Almacen(id=4, nombre="Almacén Tostaduría", empresa="Insurrecto Coffee", tipo="PROPIO", ubicacion="Tostaduría Central Insurrecto")
    alm_sd = Almacen(id=5, nombre="Almacén Santo Domingo", empresa="Insurrecto Coffee", tipo="PROPIO", ubicacion="Distrito Nacional, Santo Domingo")
    alm_salcedo = Almacen(id=6, nombre="Almacén Salcedo", empresa="Insurrecto Coffee", tipo="PROPIO", ubicacion="Salcedo, Hermanas Mirabal")
    db.add_all([alm_beneficio, alm_secado_bani, alm_pergamino, alm_tostaduria, alm_sd, alm_salcedo])
    db.commit()

    # 5. Los 25 Campos Oficiales (Anexo A)
    campos_raw = [
        ("CP-01", "La hacienda", "", 35.0, "Café Productivo", 1120),
        ("CP-02", "Las gallinas", "", 28.0, "Café Productivo", 1140),
        ("CP-03", "El vivero", "", 15.0, "Vivero / Café", 1110),
        ("CP-04", "Los plátanos", "", 20.0, "Café Productivo", 1130),
        ("CP-05", "Chivo 1", "", 40.0, "Café Productivo", 1180),
        ("CP-06", "Chivo 2", "", 38.0, "Café Productivo", 1175),
        ("CP-07", "Camino viejo", "", 25.0, "Café Productivo", 1160),
        ("CP-08", "El triangulito", "", 18.0, "Café Productivo", 1150),
        ("CP-09", "El 7", "", 45.0, "Café Productivo", 1210),
        ("CP-10", "El 8", "", 50.0, "Café Productivo", 1230),
        ("CP-11", "Alto del 6", "Sector 6", 30.0, "Café Productivo", 1250),
        ("CP-12", "Medio del 6", "Sector 6", 32.0, "Café Productivo", 1200),
        ("CP-13", "Viejo del 6", "Sector 6", 26.0, "Café Productivo", 1190),
        ("CP-14", "El 5", "", 42.0, "Café Productivo", 1180),
        ("CP-15", "Alto del 4", "Sector 4", 34.0, "Café Productivo", 1240),
        ("CP-16", "Bajo del 4", "Sector 4", 29.0, "Café Productivo", 1160),
        ("CP-17", "Fenelon", "", 48.0, "Café Productivo", 1220),
        ("CP-18", "Medio del 2 abajo", "Sector 2", 31.0, "Café Productivo", 1170),
        ("CP-19", "Medio del 2 arriba", "Sector 2", 33.0, "Café Productivo", 1210),
        ("CP-20", "Bajo del 2", "Sector 2", 27.0, "Café Productivo", 1150),
        ("CP-21", "Alto del 2", "Sector 2", 36.0, "Café Productivo", 1260),
        ("CP-22", "Alto del 3", "Sector 3", 38.0, "Café Productivo", 1250),
        ("CP-23", "Medio del 3", "Sector 3", 35.0, "Café Productivo", 1200),
        ("CP-24", "Llano del 3", "Sector 3", 40.0, "Café Productivo", 1140),
        ("CP-25", "Abajo del monte", "", 22.0, "Café Productivo", 1120),
    ]
    campos_list = []
    for cod, nom, sec, area, uso, alt in campos_raw:
        c = Campo(
            codigo=cod, nombre=nom, sector=sec or "General", area_tareas=area,
            variedad="Caturra Rojo / Típica", tipo_uso=uso, altitud_msnm=alt, activo=True
        )
        campos_list.append(c)
        db.add(c)
    db.commit()

    # 6. Catálogo Inicial de Productos y SKUs (Anexo B)
    # 7 oz = 0.1984 kg; 250 g = 0.2500 kg; 400 g = 0.4000 kg; 12 oz = 0.3402 kg; 2.5 lb = 1.1340 kg
    skus = [
        ProductoSKU(sku="EV-7OZ-GR", marca="Café El Vecino", presentacion="7 oz", formato="GRANO", peso_neto_kg=0.1984),
        ProductoSKU(sku="EV-7OZ-ML", marca="Café El Vecino", presentacion="7 oz", formato="MOLIDO", peso_neto_kg=0.1984),
        ProductoSKU(sku="EV-250G-GR", marca="Café El Vecino", presentacion="250 g", formato="GRANO", peso_neto_kg=0.2500),
        ProductoSKU(sku="EV-250G-ML", marca="Café El Vecino", presentacion="250 g", formato="MOLIDO", peso_neto_kg=0.2500),
        ProductoSKU(sku="EV-400G-GR", marca="Café El Vecino", presentacion="400 g", formato="GRANO", peso_neto_kg=0.4000),
        ProductoSKU(sku="EV-400G-ML", marca="Café El Vecino", presentacion="400 g", formato="MOLIDO", peso_neto_kg=0.4000),
        ProductoSKU(sku="MB-12OZ-GR", marca="Insurrecto Morning Blend", presentacion="12 oz", formato="GRANO", peso_neto_kg=0.3402),
        ProductoSKU(sku="MB-12OZ-ML", marca="Insurrecto Morning Blend", presentacion="12 oz", formato="MOLIDO", peso_neto_kg=0.3402),
        ProductoSKU(sku="MB-25LB-GR", marca="Insurrecto Morning Blend", presentacion="2.5 lb", formato="GRANO", peso_neto_kg=1.1340),
        ProductoSKU(sku="MB-25LB-ML", marca="Insurrecto Morning Blend", presentacion="2.5 lb", formato="MOLIDO", peso_neto_kg=1.1340),
    ]
    db.add_all(skus)
    db.commit()

    # 7. Tarifas vigentes
    t_kg = Tarifa(tipo="KILO", valor_rd=8.0, vigencia_desde=datetime(2026, 10, 1))
    t_jornada = Tarifa(tipo="JORNADA", valor_rd=800.0, vigencia_desde=datetime(2026, 10, 1))
    db.add_all([t_kg, t_jornada])
    db.commit()

    # 8. Trabajadores
    trabajadores = [
        Trabajador(nombre_completo="Juan Pérez", cedula_id="001-1234567-1", cuadrilla="Cuadrilla 1 (La Loma)"),
        Trabajador(nombre_completo="María Gómez", cedula_id="001-2345678-2", cuadrilla="Cuadrilla 1 (La Loma)"),
        Trabajador(nombre_completo="Pedro Santana", cedula_id="001-3456789-3", cuadrilla="Cuadrilla 2 (El Valle)"),
        Trabajador(nombre_completo="Ana Rodríguez", cedula_id="001-4567890-4", cuadrilla="Cuadrilla 2 (El Valle)"),
        Trabajador(nombre_completo="Carlos Durán", cedula_id="001-5678901-5", cuadrilla="Cuadrilla 1 (La Loma)"),
        Trabajador(nombre_completo="José Ramón Peña", cedula_id="001-6789012-6", cuadrilla="Cuadrilla 3 (El Alto)"),
    ]
    db.add_all(trabajadores)
    db.commit()

    # 9. Productores externos
    db.add(ProductorExterno(nombre="Pedro Almonte", rnc_cedula="001-9988776-5", comunidad="Rancho Arriba"))
    db.commit()

    # 10. Transacciones de cosecha (4,850 kg totales)
    cosechas = [
        RegistroCosecha(clave_idempotencia="IDEMP-001", fecha="2026-11-07", campo_id=1, trabajador_id=1, kg_pesados=520.0, modalidad="KILO", registrado_por="Capataz de Campo"),
        RegistroCosecha(clave_idempotencia="IDEMP-002", fecha="2026-11-07", campo_id=2, trabajador_id=2, kg_pesados=480.0, modalidad="KILO", registrado_por="Capataz de Campo"),
        RegistroCosecha(clave_idempotencia="IDEMP-003", fecha="2026-11-06", campo_id=7, trabajador_id=3, kg_pesados=410.0, modalidad="KILO", registrado_por="Capataz de Campo"),
        RegistroCosecha(clave_idempotencia="IDEMP-004", fecha="2026-11-06", campo_id=10, trabajador_id=4, kg_pesados=390.0, modalidad="KILO", registrado_por="Capataz de Campo"),
        RegistroCosecha(clave_idempotencia="IDEMP-005", fecha="2026-11-05", campo_id=1, trabajador_id=1, kg_pesados=680.0, modalidad="KILO", registrado_por="Capataz de Campo"),
        RegistroCosecha(clave_idempotencia="IDEMP-006", fecha="2026-11-05", campo_id=2, trabajador_id=5, kg_pesados=500.0, modalidad="KILO", registrado_por="Capataz de Campo"),
        RegistroCosecha(clave_idempotencia="IDEMP-007", fecha="2026-11-04", campo_id=5, trabajador_id=3, kg_pesados=850.0, modalidad="KILO", registrado_por="Capataz de Campo"),
        RegistroCosecha(clave_idempotencia="IDEMP-008", fecha="2026-11-03", campo_id=14, trabajador_id=2, kg_pesados=720.0, modalidad="KILO", registrado_por="Capataz de Campo"),
        RegistroCosecha(clave_idempotencia="IDEMP-009", fecha="2026-11-02", campo_id=17, trabajador_id=4, kg_pesados=300.0, modalidad="KILO", registrado_por="Capataz de Campo"),
    ]
    db.add_all(cosechas)
    db.commit()

    # 11. Recepciones en Beneficio
    rec1 = RecepcionBeneficio(
        fecha="2026-11-07", kg_campo_total=1000.0, kg_validados=998.0, diferencia_kg=2.0,
        pct_fruta_inmadura=8.5, alerta_calidad=True, lote_codigo="LOTE-20261107-A",
        validado_por="Encargado de Beneficio", observaciones="Muestreo 8.5% inmadura. Alerta de calidad emitida a gerencia."
    )
    rec2 = RecepcionBeneficio(
        fecha="2026-11-06", kg_campo_total=800.0, kg_validados=800.0, diferencia_kg=0.0,
        pct_fruta_inmadura=4.2, alerta_calidad=False, lote_codigo="LOTE-20261106-A",
        validado_por="Encargado de Beneficio", observaciones="Recepción conforme sin diferencias."
    )
    rec3 = RecepcionBeneficio(
        fecha="2026-11-05", kg_campo_total=1180.0, kg_validados=1176.0, diferencia_kg=4.0,
        pct_fruta_inmadura=3.9, alerta_calidad=False, lote_codigo="LOTE-20261105-A",
        validado_por="Encargado de Beneficio", observaciones="Validado y transferido a Insurrecto Coffee."
    )
    db.add_all([rec1, rec2, rec3])
    db.commit()

    # 12. Lotes e Inventario en todas las etapas para trazabilidad completa
    # Lote 1: Cereza en Beneficio recién recibido
    lote_cereza = Lote(
        codigo="LOTE-20261107-A", empresa_propietaria="Insurrecto Coffee", origen_tipo="PROPIO",
        variedad="Caturra", clasificacion="PRIMERA", estado_cafe="CEREZA", humedad_actual=62.0,
        almacen_actual_id=1, estado_stock="DISPONIBLE", kg_disponibles=998.0
    )
    db.add(lote_cereza)
    db.commit()

    db.add(LoteCampo(lote_id=lote_cereza.id, campo_id=1, kg_cereza_equivalente=518.96, porcentaje_participacion=52.0, metodo="MEDIDO"))
    db.add(LoteCampo(lote_id=lote_cereza.id, campo_id=2, kg_cereza_equivalente=479.04, porcentaje_participacion=48.0, metodo="MEDIDO"))
    db.add(MovimientoInventario(
        lote_id=lote_cereza.id, almacen_id=1, tipo_movimiento="ENTRADA_COSECHA", kg_afectados=998.0,
        documento_ref="REC-LOTE-20261107-A", usuario="Encargado de Beneficio", observacion="Cambio de propietario Myra -> Insurrecto"
    ))
    db.commit()

    # Lote 2: En secado en Baní
    lote_bani = Lote(
        codigo="LOTE-20261105-BANI", empresa_propietaria="Insurrecto Coffee", origen_tipo="PROPIO",
        variedad="Caturra", clasificacion="PRIMERA", estado_cafe="EN_SECADO", humedad_actual=16.5,
        almacen_actual_id=2, estado_stock="DISPONIBLE", kg_disponibles=480.0
    )
    db.add(lote_bani)
    db.commit()

    secado_reg = SecadoLote(
        lote_id=lote_bani.id, almacen_id=2, fecha_inicio="2026-11-05", peso_inicial_kg=510.0,
        humedad_inicial=52.0, dias_secado=3, estado="EN_SECADO", responsable="Encargado de Secado (Baní)"
    )
    db.add(secado_reg)
    db.commit()

    db.add(MedicionHumedad(secado_id=secado_reg.id, porcentaje_humedad=28.0, instrumento="Higrómetro Portátil", clima="Soleado Baní", responsable="Encargado de Secado"))
    db.add(MedicionHumedad(secado_id=secado_reg.id, porcentaje_humedad=16.5, instrumento="Higrómetro Portátil", clima="Soleado Baní", responsable="Encargado de Secado"))

    # Lote 3: Pergamino Seco en Finca (La Peñita) tras retornar de Baní a 11.8%
    lote_perg = Lote(
        codigo="LOTE-20261028-PERG", empresa_propietaria="Insurrecto Coffee", origen_tipo="PROPIO",
        variedad="Caturra", clasificacion="PRIMERA", estado_cafe="PERGAMINO_SECO", humedad_actual=11.8,
        almacen_actual_id=3, estado_stock="DISPONIBLE", kg_disponibles=850.0
    )
    db.add(lote_perg)
    db.commit()

    # Lote 4: Café Oro en Tostaduría
    lote_oro = Lote(
        codigo="LOTE-20261020-ORO", empresa_propietaria="Insurrecto Coffee", origen_tipo="PROPIO",
        variedad="Caturra", clasificacion="PRIMERA", estado_cafe="ORO", humedad_actual=11.5,
        almacen_actual_id=4, estado_stock="DISPONIBLE", kg_disponibles=680.0
    )
    db.add(lote_oro)
    db.commit()

    # Lote 5: Café Tostado
    lote_tostado = Lote(
        codigo="LOTE-20261022-TOST", empresa_propietaria="Insurrecto Coffee", origen_tipo="PROPIO",
        variedad="Caturra", clasificacion="PRIMERA", estado_cafe="TOSTADO", humedad_actual=2.1,
        almacen_actual_id=4, estado_stock="DISPONIBLE", kg_disponibles=540.0
    )
    db.add(lote_tostado)
    db.commit()

    # Lote 6: Productos Empacados en Santo Domingo y Salcedo
    lote_empaque_sd = Lote(
        codigo="LOTE-EMP-20261101-SD", empresa_propietaria="Insurrecto Coffee", origen_tipo="PROPIO",
        variedad="Caturra", clasificacion="PRIMERA", estado_cafe="EMPACADO", humedad_actual=2.0,
        almacen_actual_id=5, estado_stock="DISPONIBLE", kg_disponibles=250.0
    )
    lote_empaque_salcedo = Lote(
        codigo="LOTE-EMP-20261101-SAL", empresa_propietaria="Insurrecto Coffee", origen_tipo="PROPIO",
        variedad="Caturra", clasificacion="PRIMERA", estado_cafe="EMPACADO", humedad_actual=2.0,
        almacen_actual_id=6, estado_stock="DISPONIBLE", kg_disponibles=150.0
    )
    db.add_all([lote_empaque_sd, lote_empaque_salcedo])
    db.commit()

    # 13. Traslado Rancho Arriba -> Baní
    traslado_bani = Traslado(
        numero_guia="GUIA-20261105-01", almacen_origen_id=1, almacen_destino_id=2,
        fecha_despacho=datetime(2026, 11, 5, 8, 30), fecha_recepcion=datetime(2026, 11, 5, 12, 15),
        chofer="Ramón Antonio Díaz", vehiculo_placa="L-345890", responsable_despacho="Encargado de Beneficio",
        responsable_recepcion="Encargado de Secado (Baní)", estado="CONCILIADO",
        total_kg_despachados=512.0, total_kg_recibidos=510.0, diferencia_kg=2.0,
        resolucion_diferencia="PESAJE_BASCULA", autorizado_por="Gerencia Operaciones",
        observaciones="Diferencia de 2.0 kg dentro de tolerancia de calibración."
    )
    db.add(traslado_bani)
    db.commit()

    # 14. Análisis de Calidad y Catación
    cata1 = AnalisisCalidad(
        lote_id=lote_perg.id, fecha="2026-11-01", tipo_analisis="FISICO_Y_CATA",
        humedad_pct=11.8, defectos_totales=3, granulometria_zaranda="17/18 Superior",
        puntaje_catacion=85.5, notas_cata="Fragancia a jazmín, cuerpo cremoso, acidez brillante de manzana verde, notas a chocolate con leche y miel.",
        responsable="Especialista de Calidad"
    )
    db.add(cata1)
    db.commit()

    # 15. Nómina Semanal de Cosecha (Semana 45)
    semana45 = NominaSemana(
        codigo_semana="2026-W45", fecha_inicio="2026-11-01", fecha_fin="2026-11-07",
        total_recolectores=5, total_kg=4850.0, total_bruto_rd=38800.0, total_adelantos_rd=1500.0,
        total_neto_rd=37300.0, estado="EN_REVISION"
    )
    db.add(semana45)
    db.commit()

    # 16. Auditoría Inicial con Hash Chaining
    h0 = "0000000000000000000000000000000000000000000000000000000000000000"
    ts1 = datetime.utcnow().isoformat()
    h1 = generar_hash_auditoria(ts1, "Sistema", "INICIALIZACION", "SISTEMA", "Carga inicial de maestros y 25 campos oficiales", h0)
    db.add(AuditoriaLog(
        usuario="Sistema", accion="INICIALIZACION", entidad="SISTEMA", registro_id="GENESIS",
        detalle="Estructura inicial SICAF v2.2 desplegada", hash_previo=h0, hash_actual=h1
    ))
    db.commit()

    print("Datos maestros y transaccionales cargados con total éxito.")
    db.close()

if __name__ == "__main__":
    seed_all(force=True)
