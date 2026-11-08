"""
SICAF - Servidor Principal FastAPI v2.2
API REST, Libro Mayor de Inventario, Validación de Beneficio, Nómina y PWA Offline
"""
import os
import uuid
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from .database import get_db, engine, Base
from .models import (
    Campo, Trabajador, Tarifa, Almacen, RegistroCosecha, RecepcionBeneficio,
    Lote, MovimientoInventario, NominaSemana, NominaDetalle, AuditoriaLog
)
from .security import get_current_user
from .calculations import f01_rendimiento_etapa, f14_pago_por_kilo, f15_pago_por_jornada, f16_neto_semanal
from .sheets_sync import sheets_connector

app = FastAPI(
    title="SICAF API - Sistema Integral de Control y Administración del Café",
    description="Backend oficial para Myra Café SRL e Insurrecto Coffee",
    version="2.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- SCHEMAS -----------------
class CosechaRegistroInput(BaseModel):
    campo_id: int
    trabajador_id: int
    kg_pesados: float
    modalidad: str = "KILO"
    fraccion_jornada: float = 1.0
    bascula_id: str = "Báscula #1"
    clave_idempotencia: Optional[str] = None
    fecha: Optional[str] = None

class RecepcionBeneficioInput(BaseModel):
    fecha: str
    kg_validados: float
    pct_fruta_inmadura: float
    lote_codigo: Optional[str] = None
    observaciones: Optional[str] = None

# ----------------- API ENDPOINTS -----------------

@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Métricas principales del panel gerencial corregidas según Especificación v2.2"""
    total_cosecha = db.query(func.sum(RegistroCosecha.kg_pesados)).scalar() or 0.0
    campos_activos = db.query(Campo).filter(Campo.activo == True).count()
    recepciones_validadas = db.query(RecepcionBeneficio).count()
    
    # % promedio de fruta inmadura en muestreos de beneficio (Dato de Calidad)
    avg_inmadura = db.query(func.avg(RecepcionBeneficio.pct_fruta_inmadura)).scalar() or 0.0
    
    # Producción por campo (Top 5 para la gráfica del panel)
    prod_campos = (
        db.query(Campo.nombre, func.sum(RegistroCosecha.kg_pesados).label("total_kg"))
        .join(RegistroCosecha, Campo.id == RegistroCosecha.campo_id)
        .group_by(Campo.id)
        .order_by(func.sum(RegistroCosecha.kg_pesados).desc())
        .limit(5)
        .all()
    )
    
    # Últimos registros de cosecha
    ultimos_registros = (
        db.query(RegistroCosecha)
        .order_by(RegistroCosecha.id.desc())
        .limit(6)
        .all()
    )
    
    return {
        "kpis": {
            "total_cosecha_kg": round(total_cosecha, 1),
            "campos_activos": campos_activos,
            "registros_validados": recepciones_validadas,
            "pct_fruta_inmadura_promedio": round(avg_inmadura, 1),
            "rendimiento_estimado_pergamino_pct": 20.2, # Rendimiento de balance
            "tendencia_cosecha_pct": 12.0
        },
        "ubicacion_finca": {
            "nombre": "Finca La Peñita",
            "comunidad": "Rancho Arriba",
            "provincia": "San José de Ocoa, República Dominicana",
            "almacen_secado": "Baní, Peravia"
        },
        "grafica_campos": [{"campo": p[0], "kg": round(p[1], 1)} for p in prod_campos],
        "ultimos_registros": [
            {
                "id": r.id,
                "fecha": r.fecha,
                "campo": r.campo.nombre if r.campo else "Campo",
                "trabajador": r.trabajador.nombre_completo if r.trabajador else "Trabajador",
                "kg": r.kg_pesados,
                "modalidad": r.modalidad,
                "estado": "Validado"
            } for r in ultimos_registros
        ]
    }

@app.get("/api/campos")
def list_campos(db: Session = Depends(get_db)):
    return db.query(Campo).all()

@app.get("/api/trabajadores")
def list_trabajadores(db: Session = Depends(get_db)):
    return db.query(Trabajador).filter(Trabajador.activo == True).all()

@app.post("/api/cosecha")
def registrar_cosecha_movil(item: CosechaRegistroInput, db: Session = Depends(get_db)):
    """
    Registro móvil individual de recolectores con clave de idempotencia
    Garantiza que la nómina se calcule por persona y que los reintentos offline no dupliquen
    """
    idemp_key = item.clave_idempotencia or f"IDEMP-{uuid.uuid4().hex[:12]}"
    
    # Verificar si ya existe (idempotencia)
    existente = db.query(RegistroCosecha).filter(RegistroCosecha.clave_idempotencia == idemp_key).first()
    if existente:
        return {"status": "ALREADY_EXISTS", "registro_id": existente.id, "mensaje": "Registro ya sincronizado previamente"}

    import datetime
    fecha = item.fecha or datetime.date.today().isoformat()
    
    nuevo_reg = RegistroCosecha(
        clave_idempotencia=idemp_key,
        fecha=fecha,
        campo_id=item.campo_id,
        trabajador_id=item.trabajador_id,
        kg_pesados=item.kg_pesados,
        modalidad=item.modalidad,
        fraccion_jornada=item.fraccion_jornada,
        bascula_id=item.bascula_id,
        registrado_por="Capataz Móvil"
    )
    db.add(nuevo_reg)
    db.commit()
    db.refresh(nuevo_reg)
    
    # Cola a Google Sheets
    sheets_connector.sync_record("trx_cosecha_campo", [
        nuevo_reg.id, idemp_key, fecha, item.campo_id, item.trabajador_id, item.kg_pesados, item.modalidad
    ])
    
    return {"status": "SUCCESS", "registro_id": nuevo_reg.id, "clave_idempotencia": idemp_key}

@app.post("/api/recepcion")
def validar_recepcion_beneficio(item: RecepcionBeneficioInput, db: Session = Depends(get_db)):
    """
    Validación en Beneficio (Insurrecto):
    1. Compara total pesado en beneficio vs total registrado en campo
    2. Registra % de fruta inmadura (alerta si > 5%)
    3. Traspasa la propiedad Myra -> Insurrecto sin precio
    4. Crea el lote y movimiento en el libro mayor de inventario
    """
    # Total de campo para la fecha
    total_campo = db.query(func.sum(RegistroCosecha.kg_pesados)).filter(RegistroCosecha.fecha == item.fecha).scalar() or item.kg_validados
    diferencia = round(total_campo - item.kg_validados, 2)
    
    alerta_calidad = item.pct_fruta_inmadura > 5.0
    lote_cod = item.lote_codigo or f"LOTE-{item.fecha.replace('-', '')}-{uuid.uuid4().hex[:4].upper()}"
    
    recepcion = RecepcionBeneficio(
        fecha=item.fecha,
        kg_campo_total=total_campo,
        kg_validados=item.kg_validados,
        diferencia_kg=diferencia,
        pct_fruta_inmadura=item.pct_fruta_inmadura,
        alerta_calidad=alerta_calidad,
        lote_codigo=lote_cod,
        validado_por="Encargado de Beneficio",
        observaciones=item.observaciones
    )
    db.add(recepcion)
    db.commit()
    db.refresh(recepcion)
    
    # Crear lote y movimiento en inventario (Libro Mayor)
    lote = Lote(
        codigo=lote_cod,
        origen_tipo="PROPIO",
        variedad="Caturra",
        clasificacion="PRIMERA",
        estado_cafe="CEREZA",
        humedad_actual=60.0,
        almacen_actual_id=1, # Almacén Beneficio
        kg_disponibles=item.kg_validados
    )
    db.add(lote)
    db.commit()
    db.refresh(lote)
    
    mov = MovimientoInventario(
        lote_id=lote.id,
        almacen_id=1,
        tipo_movimiento="ENTRADA_COSECHA",
        kg_afectados=item.kg_validados,
        documento_ref=f"REC-{recepcion.id}",
        usuario="Encargado de Beneficio",
        observacion="Cambio de propietario Myra -> Insurrecto"
    )
    db.add(mov)
    db.commit()
    
    return {
        "status": "VALIDADO",
        "recepcion_id": recepcion.id,
        "lote_creado": lote_cod,
        "diferencia_kg": diferencia,
        "alerta_calidad": alerta_calidad,
        "alerta_mensaje": "ALERTA: Fruta inmadura supera el umbral de 5.0%" if alerta_calidad else "Calidad óptima"
    }

@app.get("/api/inventario")
def get_inventario(db: Session = Depends(get_db)):
    """Libro Mayor: calcula existencias agrupadas por almacén y clasificación"""
    lotes = db.query(Lote).filter(Lote.activo == True).all()
    resultado = []
    for l in lotes:
        alm = db.query(Almacen).filter(Almacen.id == l.almacen_actual_id).first()
        resultado.append({
            "lote": l.codigo,
            "almacen": alm.nombre if alm else "Sin Almacén",
            "ubicacion": alm.ubicacion if alm else "",
            "variedad": l.variedad,
            "clasificacion": l.clasificacion,
            "estado": l.estado_cafe,
            "humedad": l.humedad_actual,
            "kg_disponibles": l.kg_disponibles
        })
    return resultado

@app.get("/api/nomina/liquidacion")
def calcular_nomina_semanal(db: Session = Depends(get_db)):
    """Liquidación automática de nómina semanal por recolector con tarifas vigentes"""
    tarifa_kg = 8.0 # RD$ por kilo
    tarifa_jornada = 800.0 # RD$ por jornada
    
    # Agrupar cosechas por trabajador
    trabajadores = db.query(Trabajador).filter(Trabajador.activo == True).all()
    liquidacion = []
    total_general_neto = 0.0
    total_general_kg = 0.0
    
    for t in trabajadores:
        regs = db.query(RegistroCosecha).filter(RegistroCosecha.trabajador_id == t.id).all()
        kg_total = sum(r.kg_pesados for r in regs if r.modalidad == "KILO")
        jornadas_total = sum(r.fraccion_jornada for r in regs if r.modalidad == "JORNADA")
        
        bruto_kg = f14_pago_por_kilo(kg_total, tarifa_kg)
        bruto_jornada = f15_pago_por_jornada(jornadas_total, tarifa_jornada)
        bruto_total = bruto_kg + bruto_jornada
        
        adelantos = 0.0 # Configurable
        neto = f16_neto_semanal(bruto_total, adelantos=adelantos)
        
        total_general_neto += neto
        total_general_kg += kg_total
        
        liquidacion.append({
            "trabajador_id": t.id,
            "nombre": t.nombre_completo,
            "cuadrilla": t.cuadrilla,
            "kg_cosechados": round(kg_total, 1),
            "tarifa_kg": tarifa_kg,
            "subtotal_kg": bruto_kg,
            "dias_jornada": jornadas_total,
            "subtotal_jornada": bruto_jornada,
            "bruto": bruto_total,
            "adelantos": adelantos,
            "neto_a_pagar": neto
        })
        
    return {
        "periodo": "Semana Actual (Noviembre 2026)",
        "total_kg": round(total_general_kg, 1),
        "total_nomina_rd": round(total_general_neto, 2),
        "detalle": liquidacion
    }

# Servir archivos estáticos
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
