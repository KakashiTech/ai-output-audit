# Guion de llamada — 15 minutos

No vas a demostrar que eres ingeniero. Vas a demostrar que **mides lo que otros adivinan**. La llamada es para escuchar y cualificar; el detalle técnico va por escrito después.

## Antes de la llamada

1. Manda un anexo de una página: qué mides, qué no, cómo se reproduce, qué necesitas.
2. Pide **20 outputs de ejemplo** (anonimizados). Si no los dan antes, la llamada es de descubrimiento, no de venta.
3. Ten abierto el informe demo y el repo.
4. Ten este guion en una segunda pantalla.

## Estructura

| Min | Qué haces |
|---|---|
| 0–2 | Contexto: “Cuéntame qué workflow tenéis y qué fallo te preocupa.” |
| 2–6 | Cuantificar: volumen, coste del error, quién revisa hoy, quién firma. |
| 6–9 | Explicar el método en 3 frases. |
| 9–12 | Encaje y siguiente paso: 20 outputs, NDA, 5 días. |
| 12–15 | Preguntas. Si no sabes: “te lo mando por escrito hoy”. |

## Las 10 preguntas

1. ¿Qué workflow usa IA y qué produce?
2. ¿Cuántos outputs al mes?
3. ¿Qué pasa cuando uno sale mal? ¿Quién lo detecta?
4. ¿Cuánto cuesta rehacerlo (horas, cliente, multa, retraso)?
5. ¿Quién revisa hoy y con qué criterio?
6. ¿Ese criterio está escrito o vive en la cabeza de alguien?
7. ¿Qué modelo y qué prompt usáis?
8. ¿Habéis medido la tasa de fallo alguna vez?
9. ¿Quién firma la compra y qué necesita para aprobarla?
10. ¿Qué haría que esto fuera un “no” para ti?

## Método en 3 frases

> “Definimos contigo qué es correcto, caso por caso. Lo convierto en tests que se ejecutan solos. Te entrego la tasa de fallo, los fallos reproducidos y el coste de retrabajo; tú puedes correr el mismo comando.”

## Si preguntan algo técnico y no lo sabes

No improvises. Usa una de estas:

- “Buena pregunta. No te doy un número sin medirlo; te mando el detalle por escrito hoy con el caso reproducible.”
- “Eso es una decisión de arquitectura. Lo que yo mido es si el output cumple el criterio; si quieres, lo revisamos con una muestra.”
- “No firmo seguridad. Si necesitas certificación, no soy el proveedor. Lo que sí puedo es medir los fallos que te cuestan dinero.”
- “No lo sé todavía. Necesito ver 20 outputs para responderte con datos, no con opinión.”

Eso no es debilidad: es el producto.

## Objeciones en llamada

| Dicen | Respondes |
|---|---|
| “¿Cuánto cuesta?” | “Depende del volumen: 1.500–3.500 USD por 200–500 outputs. El diagnóstico de 50 es 300 USD o gratis con caso anonimizado.” |
| “¿Me garantizas que encontrarás fallos?” | “No. Garantizo el método y que puedes reproducirlo. Si no hay fallos, te llevas evidencia y la suite de regresión.” |
| “Ya lo hace nuestro proveedor” | “Perfecto. ¿Te enseña la tasa de fallo con intervalo de confianza y los casos reproducidos? Si sí, no me necesitas.” |
| “Es caro” | “Compáralo con una semana de retrabajo. Empezamos con 50 outputs para que lo veas antes de 500.” |
| “No podemos compartir datos” | “Anonimiza, corro local, empezamos con 20. NDA antes de recibir nada.” |

## Frases prohibidas

- “Te garantizo que la IA falla.”
- “Certifico que es seguro.”
- “Mi IA lo hace todo sola.”
- “Somos expertos en tu dominio” (si no lo eres).
- “Te lo mando cuando pueda” (di una hora concreta).

## Email post-llamada

> Asunto: resumen y siguiente paso
>
> Hola {nombre}:
>
> Gracias por el tiempo. Resumen:
> - Workflow: {workflow}
> - Dolor: {dolor}
> - Siguiente paso: 20 outputs anonimizados + criterio de aceptación.
> - Plazo: informe de diagnóstico en 72 h.
>
> Te adjunto el NDA y la lista de lo que necesito. Si prefieres, empiezo con 10 outputs para que veas el formato.
>
> Un saludo,

## Video demo de 3 minutos (sin cara)

Si no quieres llamada, graba pantalla:

1. Abre `reports/demo/report.md`.
2. Lee el veredicto y el IC.
3. Muestra un fallo concreto y el comando que lo reproduce.
4. Di qué necesitas: 20 outputs, NDA, 72 h.
5. Cierra con el enlace al repo.

No edites de más. La prueba es que el comando corra en vivo.

## Ensayo

Pídeme que haga de CTO escéptico y practicamos 3 rondas: precio, garantía y “¿por qué tú?”. No se aprende leyendo el guion; se aprende diciéndolo en voz alta.
