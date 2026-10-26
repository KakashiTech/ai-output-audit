# Auditoría de salida de IA — `gpt-oss-20b (Pollinations, tier anonimo)`

**Fecha:** 2026-10-26T00:51:25+00:00  
**Casos evaluados:** 15  
**Método:** golden set + graders deterministas (ejecución de código y comparación campo a campo).

## Veredicto

> Tasa de acierto: **100.0%** (IC 95%: 79.6% – 100.0%). 0 de 15 outputs fallaron.

Coste estimado de retrabajo si esto se repite 100 veces: **$0** (0.0 h a $80/h).

## Por familia de tarea

| Familia | Casos | Aciertos | Tasa | Fallos |
|---|---:|---:|---:|---:|
| `code` | 5 | 5 | 100.0% | 0 |
| `extraction` | 10 | 10 | 100.0% | 0 |

## Taxonomía de fallos

Sin fallos en esta muestra.

## Severidad

| Severidad | Fallos |
|---|---:|

## Fallos reproducidos (máx. 10)

Ninguno.

## Validez de la medición

- Techo detectado: 100% de acierto con n=15. El set no distingue un modelo excelente de uno que solo acierta lo fácil.
- Muestra pequeña (n=15): el IC 95% va de 79.6% a 100.0%. Cualquier conclusión es provisional.
- Cero fallos no significa cero riesgo: puede significar que el set es demasiado fácil o que el criterio está mal definido.

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
