"""
SICAF - Modelos de Datos Relacionales v2.2 (SQLAlchemy)
Implementación integral de las entidades de la Especificación Maestra:
Maestros, Operaciones de Campo, Beneficio, Secado, Traslados, Transformación,
Inventario Libro Mayor (Append-Only), Nómina, Calidad y Auditoría Inmutable con Hash Chaining.
"""
import hashlib
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, func
)
from sqlalchemy.orm import relationship
from .database import Base

class Empresa(Base):
    __tablename__ = "seg_empresas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    rnc = Column(String(20), nullable=True)
    tipo = Column(String(30), nullable=False) # 'AGRICOLA' (Myra Café SRL) | 'INDUSTRIAL' (Insurrecto Coffee)

class Usuario(Base):
    __tablename__ = "seg_usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False) # 'ADMIN', 'CAMPO', 'BENEFICIO', 'SECADO', 'NOMINA', 'AUDITOR', 'CALIDAD', 'TOSTADURIA'
    activo = Column(Boolean, default=True)
    creado_el = Column(DateTime, default=datetime.utcnow)

class Campana(Base):
    __tablename__ = "mae_campanas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False) # ej: "Cosecha 2026-2027"
    fecha_inicio = Column(String(10), nullable=False)
    fecha_fin = Column(String(10), nullable=True)
    estado = Column(String(20), default="ACTIVA") # 'ACTIVA' | 'CERRADA'

class Campo(Base):
    __tablename__ = "mae_campos"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    sector = Column(String(50), nullable=True)
    area_tareas = Column(Float, default=0.0)
    cantidad_plantas = Column(Integer, default=0) # Cantidad de plantas en el campo
    variedad = Column(String(100), default="Caturra Rojo / Típica")
    tipo_uso = Column(String(50), default="Café Productivo")
    altitud_msnm = Column(Integer, default=1150)
    ano_siembra = Column(Integer, default=2018)
    activo = Column(Boolean, default=True)

class CampoHistorial(Base):
    __tablename__ = "mae_campo_historial"
    id = Column(Integer, primary_key=True, index=True)
    tipo_cambio = Column(String(30), nullable=False) # 'FUSION', 'DIVISION', 'RENOMBRE', 'DESACTIVACION'
    campo_origen_id = Column(Integer, ForeignKey("mae_campos.id"), nullable=True)
    campo_destino_id = Column(Integer, ForeignKey("mae_campos.id"), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    motivo = Column(String(255), nullable=False)
    autorizado_por = Column(String(100), nullable=False)

class Trabajador(Base):
    __tablename__ = "mae_trabajadores"
    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(120), nullable=False)
    cedula_id = Column(String(30), nullable=True)
    cuadrilla = Column(String(50), default="Cuadrilla Principal")
    activo = Column(Boolean, default=True)

class ProductorExterno(Base):
    __tablename__ = "mae_productores_externos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    rnc_cedula = Column(String(30), nullable=True)
    comunidad = Column(String(100), default="Rancho Arriba")
    telefono = Column(String(30), nullable=True)
    activo = Column(Boolean, default=True)

class Tarifa(Base):
    __tablename__ = "mae_tarifas"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False) # 'KILO' | 'JORNADA'
    valor_rd = Column(Float, nullable=False)
    vigencia_desde = Column(DateTime, default=datetime.utcnow)
    vigencia_hasta = Column(DateTime, nullable=True)
    creado_por = Column(String(100), default="Administrador")
    aprobado_por = Column(String(100), default="Gerencia General")
    activo = Column(Boolean, default=True)

class Almacen(Base):
    __tablename__ = "mae_almacenes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    empresa = Column(String(50), default="Insurrecto Coffee")
    tipo = Column(String(30), default="PROPIO") # 'PROPIO', 'TERCERO_CUSTODIA', 'TRANSITO_VIRTUAL'
    ubicacion = Column(String(150), nullable=False)
    activo = Column(Boolean, default=True)

class ProductoSKU(Base):
    __tablename__ = "mae_productos_sku"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    marca = Column(String(50), nullable=False) # "Café El Vecino", "Insurrecto Morning Blend"
    presentacion = Column(String(50), nullable=False) # "7 oz", "250 g", "400 g", "12 oz", "2.5 lb"
    formato = Column(String(20), default="GRANO") # 'GRANO' | 'MOLIDO'
    peso_neto_kg = Column(Float, nullable=False)
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
    confirmado_trabajador = Column(Boolean, default=True) # RN-11
    creado_en = Column(DateTime, default=datetime.utcnow)

    campo = relationship("Campo")
    trabajador = relationship("Trabajador")

class RecepcionBeneficio(Base):
    __tablename__ = "trx_recepcion_beneficio"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String(10), nullable=False)
    tipo_proveedor = Column(String(30), default="MYRA_CAFE") # 'MYRA_CAFE' | 'PRODUCTOR_EXTERNO'
    productor_externo_id = Column(Integer, ForeignKey("mae_productores_externos.id"), nullable=True)
    campo_id = Column(Integer, ForeignKey("mae_campos.id"), nullable=True) # Campo específico si viene de la finca
    cantidad_bultos = Column(Integer, default=1) # Cantidad de bultos/sacos recibidos
    kg_campo_total = Column(Float, nullable=False)
    kg_validados = Column(Float, nullable=False) # Peso validado en báscula de beneficio
    kg_lavado_primera = Column(Float, default=0.0) # Kg obtenidos después de lavar Primera
    kg_lavado_segunda = Column(Float, default=0.0) # Kg obtenidos después de lavar Segunda
    diferencia_kg = Column(Float, default=0.0) # Diferencia de recepción
    pct_fruta_inmadura = Column(Float, default=0.0) # Muestreo manual calidad
    alerta_calidad = Column(Boolean, default=False) # Umbral > 5.0%
    lote_codigo = Column(String(50), unique=True, nullable=False)
    validado_por = Column(String(100), nullable=False)
    observaciones = Column(Text, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    campo = relationship("Campo")
    productor_externo = relationship("ProductorExterno")

class Lote(Base):
    __tablename__ = "inv_lotes"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    empresa_propietaria = Column(String(50), default="Insurrecto Coffee") # RN-50 / RN-51
    origen_tipo = Column(String(20), default="PROPIO") # 'PROPIO' | 'EXTERNO'
    variedad = Column(String(100), default="Caturra")
    clasificacion = Column(String(30), default="PRIMERA") # 'PRIMERA' | 'SEGUNDA' | 'BOLA'
    estado_cafe = Column(String(40), default="CEREZA") # 'CEREZA', 'PERGAMINO_MOJADO', 'EN_SECADO', 'PERGAMINO_SECO', 'ORO', 'TOSTADO', 'EMPACADO'
    humedad_actual = Column(Float, default=0.0)
    almacen_actual_id = Column(Integer, ForeignKey("mae_almacenes.id"), nullable=False)
    estado_stock = Column(String(30), default="DISPONIBLE") # 'DISPONIBLE', 'RESERVADO', 'EN_TRANSITO', 'CUARENTENA'
    kg_disponibles = Column(Float, default=0.0)
    activo = Column(Boolean, default=True)

    almacen = relationship("Almacen")

class LoteCampo(Base):
    """Genealogía y participación de campo en cada lote para método encadenado F-09/F-10"""
    __tablename__ = "inv_lote_campo"
    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("inv_lotes.id"), nullable=False)
    campo_id = Column(Integer, ForeignKey("mae_campos.id"), nullable=False)
    kg_cereza_equivalente = Column(Float, nullable=False)
    porcentaje_participacion = Column(Float, nullable=False) # Suma 100%
    metodo = Column(String(20), default="MEDIDO") # 'MEDIDO', 'MIXTO', 'ASIGNADO'

    lote = relationship("Lote")
    campo = relationship("Campo")

class MovimientoInventario(Base):
    """
    Libro Mayor de Inventario (Solo Inserción / Append-Only / RN-02).
    Los saldos NUNCA se editan, se obtienen sumando los movimientos.
    """
    __tablename__ = "trx_movimientos_inv"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    lote_id = Column(Integer, ForeignKey("inv_lotes.id"), nullable=False)
    almacen_id = Column(Integer, ForeignKey("mae_almacenes.id"), nullable=False)
    estado_stock = Column(String(30), default="DISPONIBLE")
    tipo_movimiento = Column(String(35), nullable=False) 
    # 'ENTRADA_COSECHA', 'CAMBIO_PROPIETARIO', 'CONSUMO_PROCESO', 'PRODUCCION_PROCESO',
    # 'TRASLADO_SALIDA', 'TRASLADO_ENTRADA', 'AJUSTE_CONTEO', 'MUESTRA', 'DESCARTE', 'VENTA'
    kg_afectados = Column(Float, nullable=False) # Positivo o Negativo
    documento_ref = Column(String(100), nullable=True)
    usuario = Column(String(100), nullable=False)
    observacion = Column(String(255), nullable=True)

    lote = relationship("Lote")
    almacen = relationship("Almacen")

class SecadoLote(Base):
    """Control de Secado en Baní o La Peñita con seguimiento de humedad (RN-30a a RN-30d)"""
    __tablename__ = "trx_secado_lote"
    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("inv_lotes.id"), nullable=False)
    almacen_id = Column(Integer, ForeignKey("mae_almacenes.id"), nullable=False) # Almacén Baní o La Peñita
    fecha_inicio = Column(String(10), nullable=False)
    fecha_fin = Column(String(10), nullable=True)
    cantidad_bultos = Column(Integer, default=1) # Cantidad de bultos/sacos recibidos para secado
    categoria_cafe = Column(String(30), default="PRIMERA") # 'PRIMERA', 'SEGUNDA', 'BOLA'
    tipo_cafe_secando = Column(String(50), default="PERGAMINO_MOJADO") # Tipo de café puesto a secar
    peso_inicial_kg = Column(Float, nullable=False)
    peso_final_kg = Column(Float, nullable=True)
    humedad_inicial = Column(Float, default=50.0)
    humedad_final = Column(Float, nullable=True) # Obligatoria al cerrar secado
    dias_secado = Column(Integer, default=0)
    clima = Column(String(80), default="Soleado")
    temperatura_c = Column(Float, nullable=True) # Temperatura ambiente °C
    estado = Column(String(30), default="EN_SECADO") # 'EN_SECADO', 'FINALIZADO', 'CUARENTENA'
    responsable = Column(String(100), nullable=False)
    observaciones = Column(Text, nullable=True)

    lote = relationship("Lote")
    almacen = relationship("Almacen")

class MedicionHumedad(Base):
    __tablename__ = "trx_medicion_humedad"
    id = Column(Integer, primary_key=True, index=True)
    secado_id = Column(Integer, ForeignKey("trx_secado_lote.id"), nullable=False)
    dia_numero = Column(Integer, default=1) # Día 1, 2, 3...
    fecha_hora = Column(DateTime, default=datetime.utcnow)
    porcentaje_humedad = Column(Float, nullable=False) # Humedad al finalizar el secado del día
    humedad_cierre_dia = Column(Boolean, default=True) # Humedad registrada al final de la jornada de secado
    temperatura_c = Column(Float, nullable=True) # Temperatura °C registrada
    instrumento = Column(String(80), default="Higrómetro Digital Calibrado")
    clima = Column(String(80), default="Soleado y seco")
    observaciones = Column(String(255), nullable=True)
    responsable = Column(String(100), nullable=False)

    secado = relationship("SecadoLote")

class ProcesoTransformacion(Base):
    """
    Procesos Industriales: Despulpado, Trillado, Tostado, Molienda, Empaque, Despacho.
    Cumple balance de masa F-05 y F-06.
    """
    __tablename__ = "trx_procesos"
    id = Column(Integer, primary_key=True, index=True)
    tipo_proceso = Column(String(40), nullable=False) # 'DESPULPADO', 'TRILLADO', 'TOSTADO', 'MOLIENDA', 'EMPAQUE', 'DESPACHO_FINAL'
    almacen_id = Column(Integer, ForeignKey("mae_almacenes.id"), nullable=False)
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)
    cantidad_bultos_recibidos = Column(Integer, default=0) # Bultos recibidos para el proceso
    peso_entrada_total = Column(Float, nullable=False) # Kilos recibidos
    
    # Trillado: Café verde / oro obtenido por categoría
    kg_oro_primera = Column(Float, default=0.0) # Verde de Primera obtenido
    kg_oro_segunda = Column(Float, default=0.0) # Verde de Segunda obtenido
    
    # Tostado: Cantidad que pasa a tueste de cada categoría
    kg_tueste_primera = Column(Float, default=0.0)
    kg_tueste_segunda = Column(Float, default=0.0)
    
    # Empaque: Paquetes / unidades obtenidas de cada SKU
    sku_id = Column(Integer, ForeignKey("mae_productos_sku.id"), nullable=True)
    paquetes_obtenidos = Column(Integer, default=0)
    
    # Despacho de producto final
    cliente_destino = Column(String(120), nullable=True)
    paquetes_despachados = Column(Integer, default=0)
    documento_despacho = Column(String(60), nullable=True)
    
    peso_salida_principal = Column(Float, default=0.0)
    peso_subproductos = Column(Float, default=0.0) # Pulpa, cascarilla
    peso_descarte = Column(Float, default=0.0) # Defectos, piedras
    peso_muestra = Column(Float, default=0.0)
    residual_kg = Column(Float, default=0.0)
    residual_pct = Column(Float, default=0.0)
    alerta_balance = Column(Boolean, default=False)
    grado_tueste = Column(String(30), nullable=True) # Claro, Medio, Oscuro
    responsable = Column(String(100), nullable=False)
    validador = Column(String(100), nullable=True)
    estado = Column(String(20), default="FINALIZADO") # 'EN_PROCESO', 'FINALIZADO', 'ANULADO'
    notas = Column(Text, nullable=True)

    sku = relationship("ProductoSKU")

class LoteGenealogia(Base):
    __tablename__ = "inv_lote_genealogia"
    id = Column(Integer, primary_key=True, index=True)
    lote_padre_id = Column(Integer, ForeignKey("inv_lotes.id"), nullable=False)
    lote_hijo_id = Column(Integer, ForeignKey("inv_lotes.id"), nullable=False)
    proceso_id = Column(Integer, ForeignKey("trx_procesos.id"), nullable=True)
    kg_aportados = Column(Float, nullable=False)
    fraccion_participacion = Column(Float, nullable=False)

class Traslado(Base):
    """
    Control de Traslados de la cadena:
    - Campo -> Beneficio
    - Beneficio -> Área de Secado
    - Área de Secado -> Almacén de la Finca
    - Finca -> Tostaduría
    - Tostaduría -> Almacén de Distribución en Santo Domingo
    - Finca -> Clientes
    Registra: fecha, lote/código, tipo de café, cantidad de bultos, kilos, chofer, vehículo, observaciones.
    """
    __tablename__ = "trx_traslados"
    id = Column(Integer, primary_key=True, index=True)
    numero_guia = Column(String(50), unique=True, index=True, nullable=False)
    tipo_ruta = Column(String(60), default="INTERNO") 
    # 'CAMPO_A_BENEFICIO', 'BENEFICIO_A_SECADO', 'SECADO_A_ALMACEN_FINCA', 'FINCA_A_TOSTADURIA', 'TOSTADURIA_A_SANTO_DOMINGO', 'FINCA_A_CLIENTES'
    codigo_lote = Column(String(60), nullable=True) # Lote o código de café trasladado
    tipo_cafe = Column(String(50), default="CEREZA") # 'CEREZA', 'PERGAMINO_MOJADO', 'PERGAMINO_SECO', 'ORO', 'TOSTADO', 'EMPACADO'
    cantidad_bultos = Column(Integer, default=1) # Cantidad de bultos trasladados
    almacen_origen_id = Column(Integer, ForeignKey("mae_almacenes.id"), nullable=True)
    almacen_destino_id = Column(Integer, ForeignKey("mae_almacenes.id"), nullable=True)
    cliente_destino_nombre = Column(String(120), nullable=True) # Para traslados Finca -> Clientes
    fecha_despacho = Column(DateTime, default=datetime.utcnow)
    fecha_recepcion = Column(DateTime, nullable=True)
    chofer = Column(String(100), nullable=False)
    vehiculo_placa = Column(String(30), nullable=False)
    responsable_despacho = Column(String(100), nullable=False)
    responsable_recepcion = Column(String(100), nullable=True)
    estado = Column(String(30), default="EN_TRANSITO") # 'BORRADOR', 'EN_TRANSITO', 'RECIBIDO', 'CONCILIADO', 'CON_DIFERENCIA'
    tolerancia_pct = Column(Float, default=0.5) # 0.5% por defecto
    total_kg_despachados = Column(Float, nullable=False)
    total_kg_recibidos = Column(Float, default=0.0)
    diferencia_kg = Column(Float, default=0.0)
    resolucion_diferencia = Column(String(40), nullable=True) 
    autorizado_por = Column(String(100), nullable=True)
    observaciones = Column(Text, nullable=True)

    almacen_origen = relationship("Almacen", foreign_keys=[almacen_origen_id])
    almacen_destino = relationship("Almacen", foreign_keys=[almacen_destino_id])

class TrasladoDetalle(Base):
    __tablename__ = "trx_traslado_detalle"
    id = Column(Integer, primary_key=True, index=True)
    traslado_id = Column(Integer, ForeignKey("trx_traslados.id"), nullable=False)
    lote_id = Column(Integer, ForeignKey("inv_lotes.id"), nullable=False)
    kg_despachados = Column(Float, nullable=False)
    kg_recibidos = Column(Float, default=0.0)
    diferencia_kg = Column(Float, default=0.0)

    lote = relationship("Lote")

class Saco(Base):
    """
    Control de Sacos individuales con Códigos y Subcódigos (RN-2.5 / RN-3.B).
    El subcódigo generado se escribe a mano en la etiqueta física pegada en el saco.
    Permite validar que los sacos que salen de un almacén lleguen al almacén destino.
    """
    __tablename__ = "inv_sacos"
    id = Column(Integer, primary_key=True, index=True)
    codigo_lote = Column(String(50), index=True, nullable=False) # Ej: LOTE-2026-FENELON-01
    subcodigo_saco = Column(String(60), unique=True, index=True, nullable=False) # Ej: LOTE-2026-FENELON-01-S01
    campo_id = Column(Integer, ForeignKey("mae_campos.id"), nullable=True)
    lote_id = Column(Integer, ForeignKey("inv_lotes.id"), nullable=True)
    almacen_actual_id = Column(Integer, ForeignKey("mae_almacenes.id"), default=1) # 1: Beneficio Rancho Arriba
    peso_kg = Column(Float, nullable=False) # Peso específico de este saco
    tipo_cafe = Column(String(40), default="CEREZA") # 'CEREZA', 'PERGAMINO_MOJADO', 'PERGAMINO_SECO', 'ORO'
    estado = Column(String(30), default="EN_ALMACEN") # 'EN_ALMACEN', 'EN_TRANSITO', 'RECIBIDO', 'PROCESADO'
    etiqueta_escrita_a_mano = Column(Boolean, default=True) # Marcado físico a mano
    traslado_id = Column(Integer, ForeignKey("trx_traslados.id"), nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
    creado_por = Column(String(100), default="Capataz / Encargado")

    campo = relationship("Campo")
    lote = relationship("Lote")
    almacen_actual = relationship("Almacen")
    traslado = relationship("Traslado")

class AnalisisCalidad(Base):
    """Módulo de Calidad y Catación (RN-40 a RN-44)"""
    __tablename__ = "cal_analisis"
    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("inv_lotes.id"), nullable=False)
    fecha = Column(String(10), nullable=False)
    tipo_analisis = Column(String(30), default="FISICO_Y_CATA") # 'FISICO', 'CATACION', 'HUMEDAD'
    humedad_pct = Column(Float, nullable=True)
    defectos_totales = Column(Integer, default=0)
    granulometria_zaranda = Column(String(50), default="17/18 Superior")
    puntaje_catacion = Column(Float, nullable=True) # ej: 84.5 SCAA
    notas_cata = Column(Text, nullable=True) # Floral, notas a chocolate, acidez cítrica
    cuarentena = Column(Boolean, default=False)
    responsable = Column(String(100), nullable=False)

    lote = relationship("Lote")

class ConteoFisico(Base):
    """Conteo Físico y Auditoría de Inventario (RN-07 y RN-08)"""
    __tablename__ = "inv_conteos_fisicos"
    id = Column(Integer, primary_key=True, index=True)
    almacen_id = Column(Integer, ForeignKey("mae_almacenes.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    responsable_conteo = Column(String(100), nullable=False)
    autorizado_por = Column(String(100), nullable=True)
    estado = Column(String(20), default="FINALIZADO") # 'EN_PROCESO', 'FINALIZADO'
    observacion = Column(String(255), nullable=True)

class ConteoDetalle(Base):
    __tablename__ = "inv_conteo_detalle"
    id = Column(Integer, primary_key=True, index=True)
    conteo_id = Column(Integer, ForeignKey("inv_conteos_fisicos.id"), nullable=False)
    lote_id = Column(Integer, ForeignKey("inv_lotes.id"), nullable=False)
    kg_libro = Column(Float, nullable=False)
    kg_fisico = Column(Float, nullable=False)
    diferencia_kg = Column(Float, nullable=False) # kg_fisico - kg_libro
    motivo_ajuste = Column(String(150), nullable=True)

class NominaSemana(Base):
    __tablename__ = "trx_nomina_semanal"
    id = Column(Integer, primary_key=True, index=True)
    codigo_semana = Column(String(20), unique=True, nullable=False) # ej: "2026-W45"
    fecha_inicio = Column(String(10), nullable=False)
    fecha_fin = Column(String(10), nullable=False)
    total_recolectores = Column(Integer, default=0)
    total_kg = Column(Float, default=0.0)
    total_bruto_rd = Column(Float, default=0.0)
    total_adelantos_rd = Column(Float, default=0.0)
    total_neto_rd = Column(Float, default=0.0)
    estado = Column(String(20), default="ABIERTA") # 'ABIERTA', 'EN_REVISION', 'APROBADA', 'PAGADA', 'CERRADA'
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

class NominaAjuste(Base):
    """Ajustes de nómina: adelantos, bonos, deducciones administrativas (F-16 / RN-25)"""
    __tablename__ = "trx_nomina_ajustes"
    id = Column(Integer, primary_key=True, index=True)
    nomina_semana_id = Column(Integer, ForeignKey("trx_nomina_semanal.id"), nullable=True)
    trabajador_id = Column(Integer, ForeignKey("mae_trabajadores.id"), nullable=False)
    tipo_ajuste = Column(String(30), nullable=False) # 'ADELANTO', 'BONO', 'DEDUCCION'
    monto_rd = Column(Float, nullable=False)
    motivo = Column(String(200), nullable=False)
    autorizado_por = Column(String(100), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

    trabajador = relationship("Trabajador")

class AuditoriaLog(Base):
    """
    Registro inalterable con encadenamiento criptográfico (Hash Chaining / RN-85 y RN-86).
    Cualquier intento de alteración rompe la cadena de integridad SHA-256.
    """
    __tablename__ = "auditoria_log"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    usuario = Column(String(100), nullable=False)
    accion = Column(String(60), nullable=False)
    entidad = Column(String(60), nullable=False)
    registro_id = Column(String(60), nullable=True)
    detalle = Column(Text, nullable=True)
    ip_origen = Column(String(45), default="127.0.0.1")
    hash_previo = Column(String(64), nullable=True)
    hash_actual = Column(String(64), nullable=False)

def generar_hash_auditoria(timestamp: str, usuario: str, accion: str, entidad: str, detalle: str, hash_previo: str) -> str:
    raw = f"{timestamp}|{usuario}|{accion}|{entidad}|{detalle}|{hash_previo or 'GENESIS'}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()
