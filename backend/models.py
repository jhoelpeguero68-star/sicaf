"""
SICAF - Modelos de Datos v2.2 (SQLAlchemy)
Reflejo exacto del esquema relacional y las 11 pestañas de Google Sheets
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from .database import Base

class Empresa(Base):
    __tablename__ = "seg_empresas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    rnc = Column(String(20), nullable=True)
    tipo = Column(String(30), nullable=False) # 'AGRICOLA' (Myra) | 'INDUSTRIAL' (Insurrecto)

class Usuario(Base):
    __tablename__ = "seg_usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False) # 'ADMIN', 'CAMPO', 'BENEFICIO', 'SECADO', 'NOMINA', 'AUDITOR'
    activo = Column(Boolean, default=True)
    creado_el = Column(DateTime, default=datetime.utcnow)

class Campo(Base):
    __tablename__ = "mae_campos"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    sector = Column(String(50), nullable=True)
    area_tareas = Column(Float, default=0.0)
    variedad = Column(String(100), default="Caturra / Típica")
    tipo_uso = Column(String(50), default="Café Productivo")
    activo = Column(Boolean, default=True)

class Trabajador(Base):
    __tablename__ = "mae_trabajadores"
    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(120), nullable=False)
    cedula_id = Column(String(30), nullable=True)
    cuadrilla = Column(String(50), default="Cuadrilla Principal")
    activo = Column(Boolean, default=True)

class Tarifa(Base):
    __tablename__ = "mae_tarifas"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False) # 'KILO' | 'JORNADA'
    valor_rd = Column(Float, nullable=False)
    vigencia_desde = Column(DateTime, default=datetime.utcnow)
    vigencia_hasta = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True)

class Almacen(Base):
    __tablename__ = "mae_almacenes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    empresa = Column(String(50), default="Insurrecto Coffee")
    ubicacion = Column(String(150), nullable=False)
    activo = Column(Boolean, default=True)

class JornadaCosecha(Base):
    __tablename__ = "trx_jornadas_cosecha"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String(10), nullable=False) # YYYY-MM-DD
    estado = Column(String(20), default="ABIERTA") # 'ABIERTA', 'CERRADA', 'VALIDADA'
    cerrada_por = Column(String(100), nullable=True)
    cerrada_en = Column(DateTime, nullable=True)

class RegistroCosecha(Base):
    __tablename__ = "trx_cosecha_campo"
    id = Column(Integer, primary_key=True, index=True)
    clave_idempotencia = Column(String(100), unique=True, index=True, nullable=False)
    fecha = Column(String(10), nullable=False)
    campo_id = Column(Integer, ForeignKey("mae_campos.id"), nullable=False)
    trabajador_id = Column(Integer, ForeignKey("mae_trabajadores.id"), nullable=False)
    kg_pesados = Column(Float, nullable=False)
    modalidad = Column(String(20), default="KILO") # 'KILO' | 'JORNADA'
    fraccion_jornada = Column(Float, default=1.0)
    bascula_id = Column(String(50), default="Báscula #1")
    registrado_por = Column(String(100), nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)

    campo = relationship("Campo")
    trabajador = relationship("Trabajador")

class RecepcionBeneficio(Base):
    __tablename__ = "trx_recepcion_beneficio"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String(10), nullable=False)
    kg_campo_total = Column(Float, nullable=False)
    kg_validados = Column(Float, nullable=False)
    diferencia_kg = Column(Float, default=0.0)
    pct_fruta_inmadura = Column(Float, default=0.0) # Muestreo de calidad manual
    alerta_calidad = Column(Boolean, default=False) # Si inmadura > 5.0%
    lote_codigo = Column(String(50), unique=True, nullable=False)
    validado_por = Column(String(100), nullable=False)
    observaciones = Column(Text, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

class Lote(Base):
    __tablename__ = "inv_lotes"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    origen_tipo = Column(String(20), default="PROPIO") # PROPIO | EXTERNO
    variedad = Column(String(100), default="Caturra")
    clasificacion = Column(String(30), default="PRIMERA") # PRIMERA | SEGUNDA | BOLA
    estado_cafe = Column(String(40), default="CEREZA") # CEREZA | PERGAMINO_MOJADO | EN_SECADO | PERGAMINO_SECO | ORO | TOSTADO
    humedad_actual = Column(Float, default=0.0)
    almacen_actual_id = Column(Integer, ForeignKey("mae_almacenes.id"), nullable=False)
    kg_disponibles = Column(Float, default=0.0)
    activo = Column(Boolean, default=True)

class MovimientoInventario(Base):
    """Libro Mayor de Inventario (Solo Inserción / Append-Only)"""
    __tablename__ = "trx_movimientos_inv"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    lote_id = Column(Integer, ForeignKey("inv_lotes.id"), nullable=False)
    almacen_id = Column(Integer, ForeignKey("mae_almacenes.id"), nullable=False)
    tipo_movimiento = Column(String(30), nullable=False) # ENTRADA_COSECHA, CAMBIO_PROPIETARIO, TRASLADO_SALIDA, TRASLADO_ENTRADA, CONSUMO, AJUSTE
    kg_afectados = Column(Float, nullable=False) # Positivo o Negativo
    documento_ref = Column(String(100), nullable=True)
    usuario = Column(String(100), nullable=False)
    observacion = Column(String(255), nullable=True)

class NominaSemana(Base):
    __tablename__ = "trx_nomina_semanal"
    id = Column(Integer, primary_key=True, index=True)
    codigo_semana = Column(String(20), unique=True, nullable=False) # ej: 2026-W45
    fecha_inicio = Column(String(10), nullable=False)
    fecha_fin = Column(String(10), nullable=False)
    total_recolectores = Column(Integer, default=0)
    total_kg = Column(Float, default=0.0)
    total_bruto_rd = Column(Float, default=0.0)
    total_adelantos_rd = Column(Float, default=0.0)
    total_neto_rd = Column(Float, default=0.0)
    estado = Column(String(20), default="ABIERTA") # ABIERTA | EN_REVISION | APROBADA | PAGADA | CERRADA
    aprobada_por = Column(String(100), nullable=True)

class NominaDetalle(Base):
    __tablename__ = "trx_nomina_detalle"
    id = Column(Integer, primary_key=True, index=True)
    nomina_semana_id = Column(Integer, ForeignKey("trx_nomina_semanal.id"), nullable=False)
    trabajador_id = Column(Integer, ForeignKey("mae_trabajadores.id"), nullable=False)
    total_kg = Column(Float, default=0.0)
    tarifa_kg_rd = Column(Float, default=8.0)
    subtotal_kg_rd = Column(Float, default=0.0)
    dias_jornada = Column(Float, default=0.0)
    tarifa_jornada_rd = Column(Float, default=800.0)
    subtotal_jornada_rd = Column(Float, default=0.0)
    adelantos_rd = Column(Float, default=0.0)
    neto_rd = Column(Float, default=0.0)

    trabajador = relationship("Trabajador")

class AuditoriaLog(Base):
    __tablename__ = "auditoria_log"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    usuario = Column(String(100), nullable=False)
    accion = Column(String(50), nullable=False) # LOGIN, REGISTRO_COSECHA, VALIDAR_RECEPCION, APROBAR_NOMINA, etc.
    entidad = Column(String(50), nullable=False)
    registro_id = Column(String(50), nullable=True)
    detalle = Column(Text, nullable=True)
    ip_origen = Column(String(45), default="127.0.0.1")
