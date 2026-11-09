# SICAF — Especificación Maestra del Sistema v2.3
**Sistema Integral de Control y Administración del Café**
**Empresas:** Myra Café SRL (Operación Agrícola) · Insurrecto Coffee (Industrialización y Marca)
**Ubicación Principal:** Finca La Peñita, Rancho Arriba (San José de Ocoa, República Dominicana)
**Almacén de Secado:** Baní, Peravia (Secado Solar Controlado)
**Estado:** Versión Maestra Consolidada, Auditada y Operativa en Producción Local.
**Fecha:** 9 de noviembre de 2026

---

## 1. Identidad, Propósito y Alcance

**Nombre oficial:** SICAF (Sistema Integral de Control y Administración del Café).  
**Empresas participantes:**
- **Myra Café SRL:** Empresa responsable de la producción agrícola, mantenimiento de fincas, cosecha de café uva y compra a productores externos locales.
- **Insurrecto Coffee:** Empresa responsable de la recepción de café uva, beneficiado, secado, almacenamiento, trillado, tostado, empaque, distribución y comercialización.

### Principio Fundamental
> **SICAF no administra únicamente cantidades de café; administra la historia completa de cada cantidad de café.**  
> Ningún proceso debe perder la identidad del café que recibe del proceso anterior. Cuando un lote se divide, se transforma o se mezcla, SICAF conserva su genealogía y permite reconstruir su procedencia en menos de 1 minuto.

---

## 2. Cálculo del Rendimiento del Café por Campo y por Etapa (Regla Central v2.3)

Este componente es el núcleo analítico de SICAF. La regla central es **comparar kilogramos cosechados en cada campo con kilogramos de café tostado atribuibles al mismo origen**, calculando las mermas específicas de cada proceso.

### 2.1. Objetivos del Cálculo
1. Cuántos kilogramos de café uva se cosecharon en cada campo ($P_{cosechado}$).
2. Cuánto café se obtuvo después del despulpado y lavado (Pergamino mojado).
3. Cuánto café se obtuvo después del secado (Pergamino seco).
4. Cuánto café se obtuvo después del trillado y selección (Café oro).
5. Cuánto café verde (fruta inmadura) se detectó en el muestreo manual de recepción.
6. Cuánto café tostado se produjo ($P_{tostado}$).
7. Cuál fue la merma de cada etapa individual.
8. Cuál fue el rendimiento global de cada campo.

### 2.2. Fórmulas Matemáticas Oficiales

#### A. Rendimiento Porcentual de Etapa
Indica qué porcentaje del peso inicial ingresado se conserva como producto principal después del proceso:
$$R = \frac{P_f}{P_i} \times 100$$
Donde:
- $R$: Rendimiento porcentual de la etapa.
- $P_f$: Peso obtenido al finalizar el proceso.
- $P_i$: Peso que ingresó al proceso.

#### B. Porcentaje de Merma de Etapa
Indica qué proporción del peso inicial se perdió o transformó durante el proceso:
$$M = \frac{P_i - P_f}{P_i} \times 100 = 100 - R$$

#### C. Kilogramos de Merma de Etapa
$$M_{kg} = P_i - P_f$$

#### D. Rendimiento Global por Campo (Regla Central)
$$R_{global} = \frac{P_{tostado}}{P_{cosechado}} \times 100$$
$$M_{global\_kg} = P_{cosechado} - P_{tostado}$$
$$M_{global\_\%} = 100 - R_{global}$$

> **Regla de Oro:** Cada merma se calcula respecto al peso de entrada de su propia etapa. **Nunca se suman porcentajes de merma de diferentes etapas** para calcular la merma global. El rendimiento global es el producto encadenado de los rendimientos fraccionarios o la división directa entre el café tostado final atribuible y el café cosechado original.

---

### 2.3. Ejemplo Práctico Oficial: Comparación entre Campos

Supongamos que se cosecharon 100 kg de café uva en dos campos distintos:

| Concepto | Campo 1 | Campo 2 |
|---|---:|---:|
| Café cosechado ($P_i$) | 100 kg | 100 kg |
| Café tostado obtenido ($P_f$) | 60 kg | 70 kg |
| **Rendimiento final global ($R_{global}$)** | **60 %** | **70 %** |
| **Merma global acumulada ($M_{global}$)** | **40 %** | **30 %** |

**Interpretación Gerencial:**  
Aunque ambos campos produjeron exactamente 100 kg en la cosecha, el **Campo 2 tuvo un rendimiento superior**, produciendo **10 kg adicionales de café tostado comercializable** por cada 100 kg cosechados. SICAF identifica automáticamente esta brecha agronómica para orientar decisiones de fertilización, poda y manejo del suelo.

---

### 2.4. Estructura de Conversión y Mermas por Cada Etapa

| Etapa | Peso Entrada ($P_i$) | Peso Salida ($P_f$) | Rendimiento ($R$) | Merma ($M_{kg}$) | Merma ($M_\%$) |
|---|---:|---:|---:|---:|---:|
| **1. Cosecha (Recepción)** | 100.0 kg | 100.0 kg | 100.0 % | 0.0 kg | 0.0 % |
| **2. Despulpado y Lavado** | 100.0 kg | 80.0 kg | 80.0 % | 20.0 kg | 20.0 % |
| **3. Secado (Baní / Finca)** | 80.0 kg | 40.0 kg | 50.0 % | 40.0 kg | 50.0 % |
| **4. Trillado y Selección** | 40.0 kg | 35.0 kg | 87.5 % | 5.0 kg | 12.5 % |
| **5. Tostaduría** | 35.0 kg | 28.0 kg | 80.0 % | 7.0 kg | 20.0 % |
| **Resultado Global Acumulado** | **100.0 kg** | **28.0 kg** | **28.0 %** | **72.0 kg** | **72.0 %** |

*(Valores ilustrativos de calibración. La merma global es de 72 kg / 72%).*

---

### 2.5. Clasificaciones de Café: Primera, Segunda y Bola

- **Café de Primera y Segunda:** Obtenidos tras el despulpado y lavado mecánico. Continúan con pesajes independientes hacia secado, almacenamiento de pergamino, trillado y tostado.
- **Café Bola (Ruta Natural):** Café que **no se despulpa**. Va directamente con su cáscara al secado solar hasta ~12 % de humedad, se traslada a tostaduría y pasa por descascarillado, trillado y tueste. El sistema calcula su rendimiento sin exigir registros de despulpado.

---

### 2.6. Porcentaje de Humedad y Control de Calidad
- Es un dato obligatorio en cada cierre de secado (rango objetivo: **10.0 % a 12.5 %**).
- Si un lote cierra fuera de este rango, pasa automáticamente al estado de **CUARENTENA**, requiriendo re-secado o autorización gerencial para su despacho.
- El sistema incorpora la **Fórmula F-07 de peso normalizado al 12 % de humedad**:
  $$P_{norm} = P_{real} \times \frac{100 - H_{real}}{100 - 12.0}$$

---

### 2.7. Distinción Estricta entre % de Fruta Inmadura y Rendimiento
- **% de Fruta Inmadura (Muestreo Manual):** Dato digitado exclusivamente por el encargado de beneficio tras inspeccionar la fruta recibida. SICAF **no lo calcula, no lo modifica ni lo promedia**. Si supera el **5.0 %**, genera una alerta visual de calidad.
- **Rendimiento de Producción:** Cálculo matemático estricto realizado por el sistema basado en básculas validadas de entrada y salida.

---

## 3. Módulo de Cosecha y App Móvil Offline-First

- **Pesaje Individual (RN-10 y RN-15):** La app móvil captura saco por saco por recolector, campo, fecha y báscula.
- **Offline-First con Idempotencia (RN-70 y RN-71):** Funciona sin cobertura celular mediante IndexedDB/LocalStorage y claves UUID únicas para evitar duplicados en la reconexión.
- **Validación Segregada (RN-13 y RN-14):** El personal de campo solo registra; el encargado de beneficio valida el total recibido.
- **Cambio de Propietario (RN-51):** En la recepción del beneficio, el café uva pasa formalmente de Myra Café SRL a Insurrecto Coffee **sin registrar precio ni valor monetario**.

---

## 4. Módulo de Nómina de Cosecha y Tarifas Administrativas

- **Control Administrativo de Tarifas:**
  - El administrador fija y modifica las tarifas vigentes desde el panel:
    - **Tarifa por Kilo (RD$/kg)**: Valor configurable (ej. RD$ 8.00 / kg).
    - **Tarifa por Jornada (RD$/día)**: Valor configurable (ej. RD$ 800.00 / día, con fracciones 0.25, 0.50, 0.75, 1.00).
- **Ajustes de Nómina (RN-25):** Registro de adelantos, bonos por rendimiento y deducciones tipificadas con autorización.
- **Fórmula de Liquidación Semanal (F-16):**
  $$Neto = \sum Pagos\_Kilos + \sum Pagos\_Jornadas + Bonos - Adelantos - Deducciones$$
- **Inmutabilidad (RN-21 y RN-23):** Al aprobar la nómina semanal, los registros quedan bloqueados. Modificaciones futuras de tarifas no alteran semanas cerradas.

---

## 5. Módulo de Almacenes, Traslados y Trazabilidad

### 5.1. Almacenes Oficiales Iniciales
1. `Almacén Beneficio` — Finca La Peñita, Rancho Arriba (San José de Ocoa).
2. `Almacén de Secado` — Baní, Peravia (Clima cálido y seco).
3. `Almacén de Pergamino` — Finca La Peñita, Rancho Arriba.
4. `Almacén Tostaduría` — Tostaduría Central Insurrecto.
5. `Almacén Santo Domingo` — Distrito Nacional.
6. `Almacén Salcedo` — Salcedo, Hermanas Mirabal.

### 5.2. Control de Traslados (RN-31 a RN-39)
- Guía de traslado con origen, destino, chofer, vehículo, lote y peso despachado.
- El café despachado pasa al estado `EN_TRANSITO`.
- Al recibir, si la diferencia supera la tolerancia (**0.5 %**), se exige autorización y resolución tipificada (`PESAJE_BASCULA`, `PERDIDA_TRANSPORTE`, `HUMEDAD_EN_TRANSITO`). **Nunca se convierte automáticamente en merma de producción**.

### 5.3. Ficha de Trazabilidad Inversa (RN-47 / PA-22)
Desde cualquier bolsa o lote comercial, SICAF reconstruye:
- Finca de origen (La Peñita) y comunidad (Rancho Arriba).
- Campo(s) de origen con porcentaje de participación y método (`MEDIDO` o `MIXTO`).
- Variedad botánica.
- Fechas de cosecha, beneficiado, secado final en Baní, tueste y empaque.
- % de humedad del secado final.
- Recolectores que participaron.

---

## 6. Auditoría Criptográfica y Sincronización con Google Sheets

- **Aislamiento Seguro:** Las credenciales y URLs de Google Sheets nunca se exponen al navegador o dispositivo móvil.
- **Libro Maestro de 11 Pestañas:** Generación automatizada de `SICAF_GoogleSheets_Master.xlsx` con pestañas idénticas al modelo relacional:
  1. `seg_usuarios`
  2. `mae_campos`
  3. `mae_trabajadores`
  4. `mae_tarifas`
  5. `mae_almacenes`
  6. `trx_cosecha_campo`
  7. `trx_recepcion_beneficio`
  8. `trx_secado_humedad`
  9. `trx_movimientos_inv`
  10. `trx_nomina_semanal`
  11. `auditoria_log`
- **Hash Chaining SHA-256 (RN-85 / RN-86):** Cada evento de auditoría genera un hash encadenado al registro anterior. Si un registro es modificado en base de datos, la cadena se rompe y el sistema detecta la alteración.

---

## 7. Catálogo Oficial de los 25 Campos (Anexo A)

| Código | Nombre del Campo | Sector | Área (Tareas) | Altitud | Variedad Predominante | Tipo de Uso |
|---|---|---|---:|---:|---|---|
| CP-01 | La hacienda | General | 35.0 | 1,120 m | Caturra Rojo / Típica | Café Productivo |
| CP-02 | Las gallinas | General | 28.0 | 1,140 m | Caturra Rojo / Típica | Café Productivo |
| CP-03 | El vivero | General | 15.0 | 1,110 m | Caturra / Vivero | Vivero / Café |
| CP-04 | Los plátanos | General | 20.0 | 1,130 m | Caturra Rojo / Típica | Café Productivo |
| CP-05 | Chivo 1 | General | 40.0 | 1,180 m | Caturra Rojo / Típica | Café Productivo |
| CP-06 | Chivo 2 | General | 38.0 | 1,175 m | Caturra Rojo / Típica | Café Productivo |
| CP-07 | Camino viejo | General | 25.0 | 1,160 m | Caturra Rojo / Típica | Café Productivo |
| CP-08 | El triangulito | General | 18.0 | 1,150 m | Caturra Rojo / Típica | Café Productivo |
| CP-09 | El 7 | General | 45.0 | 1,210 m | Caturra Rojo / Típica | Café Productivo |
| CP-10 | El 8 | General | 50.0 | 1,230 m | Caturra Rojo / Típica | Café Productivo |
| CP-11 | Alto del 6 | Sector 6 | 30.0 | 1,250 m | Caturra Rojo / Típica | Café Productivo |
| CP-12 | Medio del 6 | Sector 6 | 32.0 | 1,200 m | Caturra Rojo / Típica | Café Productivo |
| CP-13 | Viejo del 6 | Sector 6 | 26.0 | 1,190 m | Caturra Rojo / Típica | Café Productivo |
| CP-14 | El 5 | General | 42.0 | 1,180 m | Caturra Rojo / Típica | Café Productivo |
| CP-15 | Alto del 4 | Sector 4 | 34.0 | 1,240 m | Caturra Rojo / Típica | Café Productivo |
| CP-16 | Bajo del 4 | Sector 4 | 29.0 | 1,160 m | Caturra Rojo / Típica | Café Productivo |
| CP-17 | Fenelon | General | 48.0 | 1,220 m | Caturra Rojo / Típica | Café Productivo |
| CP-18 | Medio del 2 abajo | Sector 2 | 31.0 | 1,170 m | Caturra Rojo / Típica | Café Productivo |
| CP-19 | Medio del 2 arriba | Sector 2 | 33.0 | 1,210 m | Caturra Rojo / Típica | Café Productivo |
| CP-20 | Bajo del 2 | Sector 2 | 27.0 | 1,150 m | Caturra Rojo / Típica | Café Productivo |
| CP-21 | Alto del 2 | Sector 2 | 36.0 | 1,260 m | Caturra Rojo / Típica | Café Productivo |
| CP-22 | Alto del 3 | Sector 3 | 38.0 | 1,250 m | Caturra Rojo / Típica | Café Productivo |
| CP-23 | Medio del 3 | Sector 3 | 35.0 | 1,200 m | Caturra Rojo / Típica | Café Productivo |
| CP-24 | Llano del 3 | Sector 3 | 40.0 | 1,140 m | Caturra Rojo / Típica | Café Productivo |
| CP-25 | Abajo del monte | General | 22.0 | 1,120 m | Caturra Rojo / Típica | Café Productivo |

---

## 8. Catálogo Oficial de Productos Terminados (Anexo B)

| Marca | Presentación Comercial | Formato Disponible | Peso Neto (kg) |
|---|---|---|---:|
| **Café El Vecino** | Bolsa 7 oz | Grano Entero y Molido | 0.1984 kg |
| **Café El Vecino** | Bolsa 250 g | Grano Entero y Molido | 0.2500 kg |
| **Café El Vecino** | Bolsa 400 g | Grano Entero y Molido | 0.4000 kg |
| **Insurrecto Morning Blend** | Bolsa 12 oz | Grano Entero y Molido (100% Puro) | 0.3402 kg |
| **Insurrecto Morning Blend** | Bolsa 2.5 lb | Grano Entero y Molido (100% Puro) | 1.1340 kg |

*Nota Gerencial: Insurrecto Morning Blend es una línea de café 100% puro; no requiere recetas de mezcla con otros granos.*

---

## 9. Evaluación y Auditoría: ¿Qué le falta a SICAF para Fase de Campo?

Tras completar el desarrollo del software, los cálculos matemáticos, el backend seguro y la interfaz web interactiva, la auditoría técnica identifica los siguientes **pasos operativos de puesta en marcha**:

1. **Calibración con Pesajes Reales de la Cosecha Actual:**
   - La estructura de software está 100% lista. Se recomienda que el encargado de beneficio comience a registrar los tiques de báscula reales para calibrar las tolerancias de merma con el histórico propio de Rancho Arriba.
2. **Carga del Roster Completo de Recolectores de Temporada:**
   - Se encuentran cargados los recolectores modelo. Al inicio de cada semana de zafra, el capataz puede ingresar los jornaleros temporales directamente desde el módulo de personal.
3. **Despliegue de Credenciales de Google Sheets:**
   - El sistema opera actualmente con almacenamiento seguro en base de datos local y exportador de 11 pestañas a Excel. Para habilitar la sincronización en la nube en tiempo real, solo se requiere colocar el archivo `credentials.json` de la cuenta de servicio de Google Cloud en el directorio del programa.
