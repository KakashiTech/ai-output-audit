# Outreach — 40 contactos, 14 días

El reality check dice que el comprador no está en Freelancer. Está en empresas que ya usan IA y tienen algo que perder. Este documento es el guion para hablar con 40 de ellas, no para mandar 400 mensajes.

## A quién (en este orden)

1. **Agencias de 5–50 personas que venden “AI development” o “AI automation”.** Señal: tienen casos de estudio con LLMs, piden “LLM engineer” en ofertas, o su web dice “AI-powered”.
2. **Startups seed/serie A con CTO técnico.** Señal: changelog con features de IA, código reciente de Cursor/Copilot, blog sobre agentes.
3. **Consultoras de datos/ingeniería que extraen documentos.** Señal: hablan de “document AI”, “PDF extraction”, “datasheets”.

**No contactes** a: empresas sin IA en producción, freelancers, ni grandes consultoras (ciclo de compra de 6 meses).

## Qué no decir

- “Soy experto en IA” — no lo eres; te desmontan en dos preguntas.
- “Hago auditorías de seguridad” — no firmas seguridad funcional; es otra cosa y tiene responsabilidad legal.
- “Tengo certificaciones” — no.
- “El 53% de las salidas de IA fallan” — es un fixture con fallos plantados, no una tasa real. Si lo dices, te lo desmontan.
- “Te audito gratis” sin límite — te usan y desaparecen. La primera es gratis **a cambio de un caso anonimizado**.

## Mensaje 1 — agencia (ES)

> **Asunto:** ¿revisáis el output de IA antes de entregarlo?
>
> Hola {nombre}:
>
> Vi que {empresa} hace {proyecto concreto}. Una pregunta incómoda: cuando la IA genera código o extracciones para un cliente, ¿alguien comprueba automáticamente que no inventa datos ni se come campos?
>
> Lo pregunto porque monté un harness público que mide exactamente eso: graders deterministas, informe con tasa de error e intervalo de confianza. En mi demo, el fixture falla 7 de 15; un modelo real pasó 15 de 15 en el mismo set. Por eso no vendo “la IA falla”: vendo medir *tu* caso con *tus* datos, que es donde aparecen los fallos que importan.
>
> Si te encaja, audito 200 outputs reales de un proyecto vuestro (sin datos sensibles) y te entrego los fallos reproducidos. La primera es gratis a cambio de permiso para publicar el caso anonimizado.
>
> Repo: https://github.com/KakashiTech/ai-output-audit
>
> ¿Te mando el informe demo de dos páginas?

## Mensaje 2 — CTO de startup (EN)

> **Subject:** does your AI-generated code pass its own tests?
>
> Hi {name} — saw {specific feature or post}. Quick question: when Cursor or Copilot writes code for {product}, what catches the cases where it looks right but isn’t?
>
> I built a small public harness for exactly that: deterministic graders, hidden tests, a failure taxonomy and a rework-cost estimate. My demo fixture fails 7/15; a real model passed 15/15 on the same set. That’s the point: generic tests are easy, your data is not.
>
> I’m offering three audits this month: 200–500 real outputs, a report with reproduced failures, and a regression suite you can run in CI. The first is free/at cost in exchange for an anonymized case study.
>
> Worth 15 minutes? Repo: https://github.com/KakashiTech/ai-output-audit

## Mensaje 3 — consultora de datos (ES)

> **Asunto:** ¿cuántos campos se pierden en vuestra extracción de PDFs?
>
> Hola {nombre}:
>
> Vi que {empresa} hace extracción de documentos con IA. El fallo típico no es que el modelo falle: es que acierta el 90%, el 10% pasa el review humano y el error aparece en el cliente tres semanas después.
>
> Tengo un método para medirlo: golden set del dominio, comparación campo a campo, detección de invención y de error de unidad, e informe con los fallos reproducidos. Es determinista y se puede correr en CI.
>
> ¿Os interesaría una auditoría de 200 documentos vuestros, con una muestra de los fallos y el coste de retrabajo? La primera la hago a cambio de un caso anonimizado.
>
> Repo: https://github.com/KakashiTech/ai-output-audit

## Seguimiento

- **Día 3:** un solo bump con un fallo concreto. *“Esto es lo que encontramos: un campo omitido que pasó el review. Si te pasa en producción, te cuesta X.”*
- **Día 7:** cierre. *“Si no es prioridad, lo dejo; si cambia, aquí estoy.”*
- **Nunca más de dos seguimientos.** El silencio es un dato.

## Tracking

| Fecha | Empresa | Persona | Canal | Señal (por qué esa) | Mensaje | Respuesta | Llamada | Propuesta | Resultado |
|---|---|---|---|---|---|---|---|---|---|

Regla: **40 contactos, no 400**. La señal viene de la calidad del targeting, no del volumen.

## Umbrales (los mismos del memo)

| Señal | Mínimo | Si no se cumple |
|---|---|---|
| Respuestas | 8/40 | El mensaje o el segmento están mal |
| Llamadas | 3 | No hay dolor real, solo curiosidad |
| Propuestas | 2 | No estás llegando a quien firma |
| Primer ingreso | 1 | El precio o el posicionamiento no funcionan |

Si tras 40 contactos no hay 3 llamadas, no escribas más código: cambia de segmento o de mensaje.
