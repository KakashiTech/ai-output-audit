# Reality check — 2026-10-26

Este documento responde una sola pregunta: **¿hay evidencia de que alguien pague por auditar salidas de IA?** No es un plan de negocio. Es el registro de lo que se midió, lo que no, y qué haría falta para creerlo.

## Veredicto en una línea

El **método** está validado (funciona, es barato y reproducible). La **demanda** no está validada. El **set sintético** tampoco discrimina: un modelo real de 20B sacó 15/15. El mercado de freelancing no es el canal: allí la auditoría de IA se paga a $15–25, no a $1.500.

## Lo que se midió

| Fuente | Consulta | Resultado | Lectura |
|---|---|---|---|
| GitHub API | `llm eval in:name,description` | **16.124 repos** | La capa de *tooling* está saturada y es gratis. Vender herramientas es perder. |
| Freelancer API | `llm` | **15 proyectos activos** | El trabajo específicamente LLM es ~2,6% de los proyectos de IA. |
| Freelancer API | `openai` | **19** | Mismo orden de magnitud. |
| Freelancer API | `chatgpt` | **29** | Más demanda por integración que por evaluación. |
| Freelancer API | `ai` | **572** | Tamaño del paraguas. |
| Freelancer API | `machine learning` | **183** | — |
| Freelancer API | `wordpress` (control) | **155** | El índice de la API devuelve cientos, no miles: los números son comparables, no un censo. |
| Freelancer API | `python` (control) | **145** | Igual. |

### Los 15 proyectos de `llm`, revisados a mano

- **1** es una auditoría: *“AI SaaS Model Audit & Fixes”*, presupuesto **$15–25**. Por debajo de cualquier precio sostenible.
- **1** es un cliente construyendo su propio producto de evals (*Latent Lens*): competencia, no comprador.
- **1** es QA/seguridad de una plataforma, sin componente de IA.
- El resto: chatbots, RAG, desarrollo full-stack, asistentes virtuales.

**Cero** proyectos de auditoría de IA con presupuesto ≥ $1.500.

### Un detalle metodológico que invalida la mitad de los datos

La API de Freelancer **ignora las comillas** y busca por OR. Por eso `"ai audit"` devuelve 729 y `"llm evaluation"` 56: no son proyectos de auditoría, son proyectos que contienen “ai” **o** “audit”. Cualquier conclusión basada en esos conteos sería falsa. Solo los términos de una palabra son interpretables.

## Segunda medición: un modelo real (2026-10-26)

Se corrió el mismo golden set contra **`gpt-oss-20b`** (endpoint OpenAI-compatible anónimo, temperatura 0, n=15).

| Métrica | Fixture `mock` | Modelo real |
|---|---:|---:|
| Acierto | 53,3% | **100%** |
| Fallos | 7/15 | **0/15** |
| IC 95% | 30,1–75,2% | 79,6–100% |

Los outputs eran genuinos: JSON válido en los 10 casos de extracción y código que pasó los 5 tests ocultos. No fue un artefacto de parseo.

### Lo que esto invalida

El **53,3% no es una tasa de fallo de mercado**. Es un fixture construido con fallos plantados (identificador inventado, error de unidad, campo omitido, prosa en vez de JSON, dos off-by-one) para probar que el detector los encuentra. Un modelo real resolvió el set entero.

Por tanto:

- El set sintético es **demasiado fácil**: párrafos limpios de una sola fuente, funciones de libro de texto, sin contexto largo ni reglas de dominio.
- Presentar el 53,3% como argumento de venta sería el mismo pecado que critico: un número que impresiona y no significa lo que parece.
- El informe ahora marca **“techo detectado”** cuando el acierto es ≥ 90%, para no vender un 100% como certificado de calidad.

### Lo que sí prueba

1. El adaptador funciona contra un endpoint real, con reintentos y backoff.
2. El grader ejecuta código real y no se deja impresionar por comentarios o docstrings.
3. El informe sabe decir **“no concluyente”**, que es la característica que separa una medición de una opinión.

### Qué haría falta para que discrimine

- Documentos reales: tablas, notas al pie, condiciones de medida, valores contradictorios, 40 páginas de contexto.
- Reglas de dominio que no están en el prompt: absoluto vs. recomendado, tolerancias, unidades implícitas.
- Código integrado: APIs del repo, concurrencia, rendimiento, casos límite que el modelo no ve.
- 200–500 outputs del cliente, no 15 sintéticos.

## Lo que esto significa

1. **El comprador de $1.500+ no publica en Freelancer.** Publica cuando ya tiene un problema concreto y alguien de confianza se lo señala. El canal es outbound directo, no marketplaces.
2. **La saturación es de herramientas, no de criterio.** 16.124 repos de evals no compiten con “audito *tu* corpus con *tus* criterios y te doy 10 fallos reproducidos”.
3. **El precio de mercado para trabajo genérico es $15–25.** Competir ahí es destruir el margen. La única defensa es especificidad: un vertical, un artefacto, un número.
4. **No hay señal de demanda, pero tampoco evidencia de ausencia.** Ausencia de datos no es dato de ausencia: Upwork bloqueó el acceso (HTTP 403) y no se midió LinkedIn ni referrals.

## Lo que NO prueba este reality check

- Que no exista demanda: solo que **no está en Freelancer** y que Upwork no se pudo medir.
- Que el precio sea correcto: no hubo ni una propuesta enviada.
- Que el segmento elegido sea el correcto: no se habló con ninguna agencia ni startup.
- Que el harness aguante datos reales: el dataset es sintético (n=15).
- Que el set actual mida algo difícil: un modelo real lo pasó entero. La demo prueba el detector, no la tasa de fallo.

## El test que sí decide (14 días)

| Día | Acción | Umbral |
|---|---|---|
| 1–3 | 40 contactos dirigidos: agencias “AI dev”, startups con Cursor/Copilot, consultoras | ≥ 8 respuestas |
| 4–7 | 3 llamadas de 20 min con un problema concreto | ≥ 3 llamadas |
| 8–10 | 2 propuestas a precio fijo ($1.500–3.500) | ≥ 2 propuestas |
| 11–14 | Cerrar la primera auditoría (gratis o $300 con testimonio) | 1 sí |

**Si falla el primer umbral**, el problema es el mensaje o el segmento, no el producto. **Si fallan los tres**, la hipótesis es falsa y hay que girar.

## Reproducir

```bash
curl -s "https://api.github.com/search/repositories?q=llm+eval+in:name,description" | jq .total_count

curl -s "https://www.freelancer.com/api/projects/0.1/projects/active/?query=llm&limit=50&full_description=true" \
  | jq '.result.total_count, (.result.projects[] | {title, budget})'
```

La segunda consulta es la que importa: leer los títulos a mano, no confiar en el conteo.
