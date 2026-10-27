# FAQ de venta — respuestas aprobadas

Regla de oro: **si no lo sabes, no improvises**. La frase que construye confianza es:

> “No te doy un número sin medirlo. Te mando el detalle por escrito hoy, con el caso reproducible.”

La lentitud con evidencia genera más confianza que la velocidad con humo. En una llamada no te examinan de ingeniería: te preguntan si pueden confiar en el número.

## Técnicas

**1. ¿Qué mides exactamente?**
La tasa de acierto de tu modelo en un conjunto de casos verificables de tu workflow. No mido “calidad” en abstracto ni hago un ranking de modelos.

**2. ¿Cómo construyes el golden set?**
Con tu experto: 20–50 casos reales, un criterio de aceptación explícito y una versión congelada. Tú apruebas el criterio antes de que se ejecute nada.

**3. ¿Cómo evito que esto sea una opinión?**
Graders deterministas: comparación campo a campo, tests que se ejecutan y reglas de dominio. El informe incluye el comando para reproducir el número.

**4. ¿Y si el modelo pasa todo?**
Es un resultado válido: te llevas evidencia y una suite de regresión. Si el acierto es ≥ 90%, el informe marca “techo detectado”: el set puede ser demasiado fácil y no se vende como certificado.

**5. ¿Qué pasa si no estoy de acuerdo con un fallo?**
Revisamos los 10 fallos. Si el criterio estaba mal, se corrige el golden set y se vuelve a ejecutar. El número cambia y queda documentado. No hay fallos “porque yo lo digo”.

**6. ¿Qué modelos y lenguajes cubres?**
Cualquier endpoint compatible con OpenAI. Código en Python hoy; otros lenguajes se añaden con sus tests. La extracción es agnóstica al dominio.

**7. ¿Puedes auditar agentes?**
Sí: trazas de tool calls, secuencia y argumentos esperados, con checks deterministas. Necesito 50–200 trazas reales.

**8. ¿Cómo proteges los datos?**
NDA, anonimización, ejecución local o en contenedor, nada a APIs de terceros sin permiso escrito, borrado a los 30 días.

**9. ¿Firmas seguridad o cumplimiento?**
No. Mido calidad; no certifico ISO 26262, SOC 2 ni seguridad funcional. Si necesitas esa firma, no soy el proveedor.

**10. ¿Por qué no usar Langfuse, DeepEval o lo que ya tengo?**
Son herramientas; el valor está en el corpus y el criterio de tu dominio. Si ya las tienes, las uso. El entregable es la auditoría, no la herramienta.

**11. ¿Cuánto tarda?**
5 días laborables desde que tengo datos y criterios. El diagnóstico inicial con 20–50 outputs puede ser 48–72 horas.

**12. ¿Cómo sé que no inventaste los fallos?**
El informe trae el output crudo, el caso mínimo y el comando para reproducirlo. Tú lo corres.

**13. ¿Qué experiencia tienes?**
No voy a inventar credenciales. Traigo un método reproducible y un repo público. La primera auditoría es a coste para que lo verifiques antes de pagar una completa.

**14. ¿Qué necesitas de mí?**
20–50 outputs con su input, criterio de aceptación, 3–5 reglas de dominio, un contacto técnico y NDA.

**15. ¿Cómo cobras?**
50% al inicio, 50% al entregar. Factura electrónica; USD o COP. La primera es gratis o a coste a cambio de un caso anonimizado.

## Objeciones comerciales

| Objeción | Respuesta |
|---|---|
| “Es caro” | “Compáralo con el coste de retrabajo. Empezamos con 50 outputs para que veas el método antes de comprometer 500.” |
| “Ya tenemos evals” | “Bien. Audito si tus evals cubren los fallos que te cuestan dinero. No reemplazo tu stack.” |
| “Nuestro modelo es bueno” | “Entonces la auditoría es barata: te llevas evidencia para tu cliente y la suite de regresión.” |
| “No podemos compartir datos” | “Anonimiza, corro local, empiezo con una muestra y firmamos NDA.” |
| “Lo tengo que pensar” | “Te dejo el informe de muestra y te pido 20 outputs como siguiente paso. Sin compromiso.” |
| “¿Me garantizas que encontrarás fallos?” | “No. Garantizo el método y la reproducibilidad; no el resultado.” |
| “¿Eres una IA?” | “Parte del análisis y la redacción se apoyan en IA; la responsabilidad y la firma son mías.” |

## Cuándo retirarse

- Piden certificación de seguridad o cumplimiento.
- Piden garantía del 100%.
- No comparten ni 20 outputs.
- Piden usar el RUT o la factura de otra persona.
- Piden “arreglar el modelo” gratis como condición para pagar.

Retirarse a tiempo también es posicionamiento.
