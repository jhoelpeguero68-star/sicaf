"""
SICAF - Semillero de Datos Iniciales (Seed Data)
Carga oficial de los 25 campos del Anexo A, almacenes de Anexo B, usuarios y tarifas.
"""
from datetime import datetime
from .database import SessionLocal, engine, Base
from .models import Empresa, Usuario, Campo, Trabajador, Tarifa, Almacen, RegistroCosecha, RecepcionBeneficio, Lote, MovimientoInventario, NominaSemana, NominaDetalle
from .security import hash_password

def seed_all():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Usuario).first():
        db.close()
        return

    print("Iniciando carga de datos maestros de SICAF...")

    # 1. Empresas
    myra = Empresa(nombre="Myra Café SRL", rnc="1-32-12345-1", tipo="AGRICOLA")
    insurrecto = Empresa(nombre="Insurrecto Coffee", rnc="1-32-98765-2", tipo="INDUSTRIAL")
    db.add_all([myra, insurrecto])
    db.commit()

    # 2. Usuarios
    u_admin = Usuario(nombre="Administrador General", email="admin@insurrecto.com", password_hash=hash_password("admin123"), rol="ADMIN")
    u_campo = Usuario(nombre="Capataz de Campo", email="campo@insurrecto.com", password_hash=hash_password("campo123"), rol="CAMPO")
    u_beneficio = Usuario(nombre="Encargado de Beneficio", email="beneficio@insurrecto.com", password_hash=hash_password("beneficio123"), rol="BENEFICIO")
    u_nomina = Usuario(nombre="Encargada de Nómina", email="nomina@insurrecto.com", password_hash=hash_password("nomina123"), rol="NOMINA")
    db.add_all([u_admin, u_campo, u_beneficio, u_nomina])
    db.commit()

    # 3. Almacenes oficiales (Anexo B)
    almacenes = [
        Almacen(nombre="Almacén Beneficio (Recepción Uva)", empresa="Insurrecto Coffee", ubicacion="Finca La Peñita, Rancho Arriba (San José de Ocoa)"),
        Almacen(nombre="Almacén de Secado – Baní", empresa="Insurrecto Coffee", ubicacion="Baní, Peravia"),
        Almacen(nombre="Almacén de Pergamino", empresa="Insurrecto Coffee", ubicacion="Finca La Peñita, Rancho Arriba"),
        Almacen(nombre="Almacén Tostaduría", empresa="Insurrecto Coffee", ubicacion="Tostaduría Central"),
        Almacen(nombre="Almacén Santo Domingo", empresa="Insurrecto Coffee", ubicacion="Distrito Nacional, Santo Domingo"),
        Almacen(nombre="Almacén Salcedo", empresa="Insurrecto Coffee", ubicacion="Salcedo, Hermanas Mirabal"),
    ]
    db.add_all(almacenes)
    db.commit()

    # 4. Los 25 Campos Oficiales (Anexo A)
    campos_raw = [
        ("CP-01", "La hacienda", "", 35.0, "Café Productivo"),
        ("CP-02", "Las gallinas", "", 28.0, "Café Productivo"),
        ("CP-03", "El vivero", "", 15.0, "Vivero / Café"),
        ("CP-04", "Los plátanos", "", 20.0, "Café Productivo"),
        ("CP-05", "Chivo 1", "", 40.0, "Café Productivo"),
        ("CP-06", "Chivo 2", "", 38.0, "Café Productivo"),
        ("CP-07", "Camino viejo", "", 25.0, "Café Productivo"),
        ("CP-08", "El triangulito", "", 18.0, "Café Productivo"),
        ("CP-09", "El 7", "", 45.0, "Café Productivo"),
        ("CP-10", "El 8", "", 50.0, "Café Productivo"),
        ("CP-11", "Alto del 6", "6", 30.0, "Café Productivo"),
        ("CP-12", "Medio del 6", "6", 32.0, "Café Productivo"),
        ("CP-13", "Viejo del 6", "6", 26.0, "Café Productivo"),
        ("CP-14", "El 5", "", 42.0, "Café Productivo"),
        ("CP-15", "Alto del 4", "4", 34.0, "Café Productivo"),
        ("CP-16", "Bajo del 4", "4", 29.0, "Café Productivo"),
        ("CP-17", "Fenelon", "", 48.0, "Café Productivo"),
        ("CP-18", "Medio del 2 abajo", "2", 31.0, "Café Productivo"),
        ("CP-19", "Medio del 2 arriba", "2", 33.0, "Café Productivo"),
        ("CP-20", "Bajo del 2", "2", 27.0, "Café Productivo"),
        ("CP-21", "Alto del 2", "2", 36.0, "Café Productivo"),
        ("CP-22", "Alto del 3", "3", 38.0, "Café Productivo"),
        ("CP-23", "Medio del 3", "3", 35.0, "Café Productivo"),
        ("CP-24", "Llano del 3", "3", 40.0, "Café Productivo"),
        ("CP-25", "Abajo del monte", "", 22.0, "Café Productivo"),
    ]
    campos_objs = []
    for cod, nom, sec, area, uso in campos_raw:
        campos_objs.append(Campo(
            codigo=cod, nombre=nom, sector=sec, area_tareas=area, variedad="Caturra Rojo / Típica", tipo_uso=uso, activo=True
        ))
    db.add_all(campos_objs)
    db.commit()

    # 5. Tarifas
    t1 = Tarifa(tipo="KILO", valor_rd=8.0)
    t2 = Tarifa(tipo="JORNADA", valor_rd=800.0)
    db.add_all([t1, t2])

    # 6. Trabajadores iniciales
    trabajadores = [
        Trabajador(nombre_completo="Juan Pérez", cedula_id="001-1234567-1", cuadrilla="Cuadrilla 1"),
        Trabajador(nombre_completo="María Gómez", cedula_id="001-2345678-2", cuadrilla="Cuadrilla 1"),
        Trabajador(nombre_completo="Pedro Santana", cedula_id="001-3456789-3", cuadrilla="Cuadrilla 2"),
        Trabajador(nombre_completo="Ana Rodríguez", cedula_id="001-4567890-4", cuadrilla="Cuadrilla 2"),
        Trabajador(nombre_completo="Carlos Durán", cedula_id="001-5678901-5", cuadrilla="Cuadrilla 1"),
    ]
    db.add_all(trabajadores)
    db.commit()

    # 7. Registros de muestra para el panel (4,850 kg totales)
    # Cosecha distribuida
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

    # Recepciones validadas en beneficio
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

    # Lotes e inventario inicial
    lote1 = Lote(codigo="LOTE-20261107-A", origen_tipo="PROPIO", variedad="Caturra", clasificacion="PRIMERA", estado_cafe="PERGAMINO_MOJADO", humedad_actual=45.0, almacen_actual_id=1, kg_disponibles=400.0)
    db.add(lote1)
    db.commit()

    db.add(MovimientoInventario(
        lote_id=lote1.id, almacen_id=1, tipo_movimiento="ENTRADA_COSECHA", kg_afectados=998.0,
        documento_ref="REC-20261107-A", usuario="Encargado de Beneficio", observacion="Cambio de propietario Myra -> Insurrecto"
    ))
    db.commit()

    print("Carga de datos completada con éxito.")
    db.close()

if __name__ == "__main__":
    seed_all()
