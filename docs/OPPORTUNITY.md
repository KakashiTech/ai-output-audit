# ¿Es real la oportunidad? Memo crítico

Fecha: 2026-10-26. Este documento existe para intentar matar la idea, no para venderla.

## Hipótesis

> Existe demanda pagable por auditar la salida de IA, porque el comprador no puede distinguir un output correcto de uno plausiblemente incorrecto, y el fallo le cuesta dinero después.

## Lo que la demo prueba

1. El método funciona: 15 casos, 16 tests, un informe reproducible con tasa, IC y taxonomía.
2. El coste de producción de un informe es **casi cero**: el harness corre en segundos y no necesita API de pago.
3. La taxonomía detecta los cuatro fallos que importan comercialmente (invención, unidad, omisión, formato).
4. El artefacto es falsable: cualquiera puede clonar el repo y obtener 8/15 otra vez.

## Lo que la demo NO prueba

1. **Que alguien pague.** Cero llamadas, cero propuestas, cero dólares. Esto es un artefacto, no un negocio.
2. **Que el método escale a datos reales.** El dataset es sintético, limpio y pequeño. Los datos de un cliente vienen sucios, sin campo esperado y con criterios en conflicto. Ahí es donde se gana o se pierde el contrato.
3. **Que el comprador exista en tu red.** Sin distribución, el mejor harness del mundo vale $0.
4. **Que el nicho dure.** Los modelos mejoran. Lo que no mejora rápido es la deuda acumulada por el código ya generado, ni la falta de criterios de aceptación en las empresas.
5. **Que puedas cobrar sin credenciales.** Puedes, pero solo en segmentos donde el deliverable es una medición, no una firma. Seguridad funcional queda fuera.

## Criterios de muerte (kill criteria)

Si en 30 días no se cumple nada de esto, la hipótesis es falsa y hay que girar:

| Señal | Umbral mínimo | Si no se cumple |
|---|---|---|
| Respuestas a 40 contactos dirigidos | ≥ 8 | El mensaje o el segmento están mal |
| Llamadas con un problema concreto | ≥ 3 | No hay dolor real, solo curiosidad |
| Propuestas enviadas | ≥ 2 | No estás llegando a quien firma |
| Primer ingreso (aunque sea $300) | 1 | El precio/posicionamiento no funciona |
| Segundo cliente sin bajar precio | 1 en 60 días | Es consultoría artesanal, no negocio |

## Segmentos, ordenados por probabilidad de compra

1. **Agencias que venden "AI development"** y no pueden permitirse un fallo en producción. Compran rápido, pagan poco, dan casos de estudio.
2. **Startups con código generado por Cursor/Copilot** y un CTO que sospecha. El dolor es real y tienen presupuesto.
3. **Equipos de datos con extracción de PDFs/datasheets**. El fallo es caro y medible.
4. **Consultoras de ingeniería** que quieren un "QA de IA" sin contratar. Ciclo más largo.
5. Empresas de hardware: **no ahora**. Sin credenciales de dominio, la venta es demasiado larga.

## Oferta y precio

- Auditoría de 5 días: **$1.500–3.500** (200–500 outputs, taxonomía, 10 fallos reproducidos, suite de regresión).
- Retainer: **$800–2.000/mes** para re-ejecutar el set en CI y avisar de regresiones.
- Primera: gratis o $300 a cambio de testimonio y permiso de publicar el caso (anonimizado).

## Plan de 14 días

| Día | Acción | Salida |
|---|---|---|
| 1–2 | Publicar este repo con el informe demo | URL pública |
| 3–4 | Auditar un modelo real vía Ollama y publicar diferencias | Segundo informe |
| 5–6 | Escribir 3 posts: un fallo concreto cada uno | Distribución |
| 7–10 | 40 contactos (agencias, startups, consultoras) | 8 respuestas |
| 11–12 | 3 llamadas de 20 min | Problema validado |
| 13–14 | 2 propuestas a precio fijo | Pipeline |

## Riesgos que pueden romperlo

- **Commoditización**: "AI code review" ya lo venden herramientas por $20/mes. La diferencia tiene que ser el *corpus específico del cliente*, no el análisis genérico.
- **Mejora de modelos**: si los modelos dejan de inventar identificadores, la cuña de extracción se estrecha. La cuña de código (deuda, seguridad, mantenibilidad) aguanta más.
- **Responsabilidad**: si te piden firmar que algo es seguro, no lo hagas. Vendes medición, no certificación.
- **Confidencialidad**: auditar código de cliente implica NDA, aislamiento y no filtrar outputs. Sin esto, no hay segundo contrato.

## Decisión

La oportunidad es **real pero no automática**. El harness demuestra que el método es barato y reproducible; no demuestra que haya un comprador esperando. El siguiente gasto no debe ser más código: debe ser **40 conversaciones**. Si esas 40 no producen 3 llamadas, el problema no era la herramienta.
