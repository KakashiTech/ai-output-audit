# Propuesta de auditoría — plantilla de una página

Copia esto, rellena los `{...}` y mándalo como PDF o en el cuerpo del email. No es asesoría legal: el contrato y el NDA los revisa un profesional en tu jurisdicción.

---

## Para {cliente}

{Una frase con su problema, no tu biografía. Ejemplo: “Entregáis extracciones de PDFs a {cliente final} y no tenéis forma de saber qué campos se pierden antes de que se queje”.}

## Qué medimos

- **{200–500} outputs reales** de vuestro workflow de {extracción / generación de código / agentes}.
- Golden set construido con {persona del cliente} y criterios explícitos, no con “lo que parece bien”.
- Graders deterministas: comparación campo a campo, ejecución de tests ocultos, reglas de dominio.
- Taxonomía de fallos: invención, error de unidad, sustitución, omisión, formato, lógica.
- Informe con tasa de acierto, **IC 95%**, los fallos reproducidos y el coste de retrabajo.

## Qué entregamos

1. `report.md` y `report.json` reproducibles por vosotros.
2. **10 fallos concretos** con evidencia, caso mínimo y severidad.
3. Suite de regresión ejecutable en CI para que no vuelvan.
4. Sesión de 45 minutos para revisar resultados y priorizar.

## Plazo y precio

- **5 días laborables** desde que recibimos los datos.
- **$1.500–3.500** según volumen y dificultad. 50% al inicio, 50% al entregar.
- Primera auditoría: **gratis o $300** a cambio de permiso para publicar el caso anonimizado.

## Qué NO hacemos

- No certificamos seguridad funcional, ISO 26262, SOC 2 ni cumplimiento normativo.
- No “arreglamos el modelo”: medimos y dejamos tests.
- No garantizamos encontrar el 100% de los fallos: el golden set es una muestra, y el informe lo dice.

## Datos y confidencialidad

- NDA antes de recibir nada.
- Solo el mínimo necesario; se anonimiza y se borra a los 30 días.
- Ejecución local o en contenedor. **Ningún dato del cliente se sube a una API de terceros** sin permiso escrito.

## Criterio de aceptación

- Vosotros podéis correr `PYTHONPATH=src python3 -m audit run ...` y obtener el mismo número.
- Si no coincide, lo revisamos sin coste.

## Siguiente paso

1. Llamada de 15 minutos para definir el workflow y el golden set.
2. Enviad **20 outputs de ejemplo** (anonimizados) antes de la llamada.
3. Si encaja, firmamos alcance y empezamos.

---

## Variante “factura limpia”

Si el acierto es **≥ 95% con n ≥ 100**, no hay fallos que cazar. En ese caso el entregable es:

- evidencia reproducible de que el workflow funciona,
- la suite de regresión para detectar bajadas,
- un precio menor (**$800–1.200**) porque el trabajo es confirmar, no investigar.

No es un fracaso de la auditoría: es el resultado que un CTO puede enseñar a su cliente. Cobrarlo es legítimo; inventar fallos para justificar el precio, no.

## Intake mínimo (lo que pides antes de empezar)

| Dato | Por qué |
|---|---|
| 20–50 outputs reales + input original | Sin el input no se puede distinguir invención de omisión |
| Salida esperada o criterio de aceptación | Es el golden set; sin esto no hay medición |
| 3–5 reglas de dominio | Unidades, tolerancias, campos obligatorios, excepciones |
| Versión del modelo y prompt usado | Para que el resultado sea atribuible |
| Permiso escrito y NDA | Sin esto, no se toca el dato |
| Persona de contacto técnica | Para resolver ambigüedades en 48 h, no en 2 semanas |

Si el cliente no puede dar ni 20 outputs, no hay auditoría: hay una llamada de descubrimiento. Cóbrala o regálala, pero no la llames auditoría.
