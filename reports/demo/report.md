# Auditoría de salida de IA — `mock:demo-model`

**Fecha:** 2026-10-26T00:41:12+00:00  
**Casos evaluados:** 15  
**Método:** golden set + graders deterministas (ejecución de código y comparación campo a campo).

## Veredicto

> Tasa de acierto: **53.3%** (IC 95%: 30.1% – 75.2%). 7 de 15 outputs fallaron.

Coste estimado de retrabajo si esto se repite 100 veces: **$1733** (21.7 h a $80/h).

## Por familia de tarea

| Familia | Casos | Aciertos | Tasa | Fallos |
|---|---:|---:|---:|---:|
| `code` | 5 | 3 | 60.0% | 2 |
| `extraction` | 10 | 5 | 50.0% | 5 |

## Taxonomía de fallos

| Tipo | Ocurrencias | Qué significa |
|---|---:|---|
| `logic_error` | 2 | el código se ejecuta pero falla los tests |
| `substitution` | 1 | tomó un dato real del lugar equivocado |
| `unit_error` | 1 | error de unidad o factor (~10x, ~1000x) |
| `hallucination` | 1 | valor inventado que no existe en la fuente |
| `omission` | 1 | campo ausente |
| `format_error` | 1 | salida no parseable |

## Severidad

| Severidad | Fallos |
|---|---:|
| crítico | 1 |
| alto | 3 |
| medio | 3 |

## Fallos reproducidos (máx. 10)

1. **ext_002** `iq_typ_ua` — `substitution` (sev 2): tomó 0.8 de otro sitio del texto
2. **ext_004** `iq_typ_ua` — `unit_error` (sev 3): 0.0012 vs 1.2 (~1000x menor)
3. **ext_005** `part_number` — `hallucination` (sev 4): 'TRX-6010' no aparece en la fuente (esperado 'TRX-6090')
4. **ext_007** `package` — `omission` (sev 2): campo ausente (se esperaba 'SOT-563')
5. **ext_009** — `format_error` (sev 2): respuesta no contiene un objeto JSON parseable
6. **code_002** — `logic_error` (sev 3): E assert [[1, 2], [3, 4]] == [[1, 2], [3, 4], [5]]
7. **code_005** — `logic_error` (sev 3): E assert [2.0, 3.0] == [2.0, 3.0, 4.0]

## Metodología

- Cada caso tiene una respuesta de referencia verificable, no una opinión.
- `extraction`: comparación campo a campo + detección de invención y de error de unidad.
- `code`: el código generado se ejecuta contra tests ocultos en un directorio temporal.
- El intervalo de confianza es Wilson al 95%; con n pequeño el rango es ancho a propósito.
- Los minutos de retrabajo por severidad son un supuesto editable, no una medición.

## Limitaciones

- El golden set es sintético y pequeño: mide el método, no el modelo en producción del cliente.
- Un acierto no prueba corrección semántica, solo conformidad con el criterio definido.
- Ejecutar código generado requiere aislamiento (contenedor/VM) en trabajo real.
