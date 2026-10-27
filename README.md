# ai-output-audit

Mide la **tasa de error real** de una salida de IA con graders deterministas y devuelve un informe que un cliente puede correr por su cuenta.

No es un benchmark de modelos. Es una herramienta para auditar **el output concreto** de un modelo concreto en un dominio concreto.

**Demo (fixture sintético):** 53.3% de acierto (IC95 30.1–75.2), 7/15 fallos.
**Modelo real (gpt-oss-20b, mismo set):** **100% (15/15, IC95 79.6–100)**.

El fixture está construido con fallos plantados para probar el detector. El modelo real pasó todo: el set sintético **no** demuestra que la IA falle, solo que el harness detecta fallos cuando existen. Un informe vendible usa outputs del cliente, no este set.

## El problema que mide

La IA genera trabajo que *parece* correcto. Un humano lo firma. Semanas después aparece el fallo: un identificador inventado, un campo que se perdió, un factor de 1000 en una unidad, un `chunk()` que se come el último elemento.

Los números públicos apuntan a lo mismo: 45% del código generado falla tests de seguridad (Veracode 2025), la refactorización cayó 70% mientras la duplicación subió 81% (GitClear 2026), y desarrolladores experimentados tardaron 19% más con IA creyendo ser 20% más rápidos (METR 2025).

Nadie compra "menos alucinaciones". Compran **"dime cuáles de estos 100 outputs están mal, con pruebas"**.

## Qué hace

| Familia | Grader | Cómo decide |
|---|---|---|
| `extraction` | comparación campo a campo contra un registro de oro | pass/fail + tipo de fallo |
| `code` | ejecuta el código generado contra tests ocultos | pytest en directorio temporal |

Y clasifica cada fallo en una taxonomía que sí es accionable:

- `hallucination` — valor inventado que no existe en la fuente (sev 4)
- `unit_error` — factor 10x/1000x (sev 3)
- `substitution` — tomó un dato real del lugar equivocado (sev 2)
- `omission` — campo ausente (sev 2)
- `format_error` — salida no parseable (sev 2)
- `logic_error` / `runtime_error` — el código falla o no corre (sev 3)

Cada fallo se traduce a minutos de retrabajo y a dólares, porque un porcentaje no le mueve el presupuesto a nadie.

## Quickstart

Requiere Python 3.10+ y `pytest`. Sin dependencias de red.

```bash
make demo     # regenera el run sintético y produce reports/demo/
make test     # 16 tests del harness
cat reports/demo/report.md
```

## Auditar un modelo real

Cualquier endpoint compatible con OpenAI (OpenAI, Ollama, vLLM, LM Studio, OpenRouter):

```bash
# local, gratis
ollama serve
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama

PYTHONPATH=src python3 -m audit run \
  --adapter openai \
  --model qwen2.5-coder:7b \
  --out reports/qwen
```

```bash
# hosted
export OPENAI_API_KEY=sk-...
PYTHONPATH=src python3 -m audit run --adapter openai --model gpt-4.1-mini --out reports/gpt
```

## Estructura

```
src/audit/
  core.py       modelo de datos, intervalo de Wilson, coste de retrabajo
  graders.py    graders de extracción y de código + taxonomía
  adapters.py   mock (replay) y openai-compatible (urllib, sin SDK)
  report.py     informe markdown + JSON
  cli.py        python -m audit run ...
datasets/
  extraction/   10 casos sintéticos de datasheet -> JSON
  code/         5 tareas con tests ocultos
runs/demo-model outputs grabados que emulan un modelo "casi bueno"
docs/
  OPPORTUNITY.md  memo crítico: qué prueba esto, qué no, y cuándo matar la idea
  REALITY-CHECK.md  qué se midió (GitHub, Freelancer, modelo real) y qué invalida
  OUTREACH.md    guion para 40 contactos, sin promesas falsas
  PROPOSAL.md    propuesta de una página + intake de datos
  SALES-FAQ.md   respuestas aprobadas a preguntas técnicas y objeciones
  CALL-SCRIPT.md guion de 15 minutos, objeciones y video demo
  OPERATIONS.md  buzón dedicado, aprobación por carpetas, SLA y seguridad
scripts/
  outreach.py    draft / send / fetch / status con aprobación humana
templates/
  agency_es.txt  plantilla de correo para agencias
data/
  targets.csv    plantilla de 40 objetivos (sin datos reales en el repo)
```

## Añadir casos

**Extracción**: una línea JSONL en `datasets/extraction/tasks.jsonl` con `id`, `source` y `expected`.

**Código**: un test en `datasets/code/tests/` que importe `from solution import ...`, y una línea en `datasets/code/manifest.jsonl`.

Regla: si el caso no se puede verificar sin pedirle permiso a un humano, no vale. La gracia es que el cliente pueda repetir el resultado.

## Estado de validación

- Método: **validado** (19 tests, demo reproducible, corrida contra un modelo real).
- Demanda: **no validada**. El 2026-10-26 se midió GitHub (16.124 repos de evals) y Freelancer (15 proyectos con “llm”; 1 auditoría a $15–25). Cero proyectos de auditoría ≥ $1.500.
- Set sintético: **no discrimina**. `gpt-oss-20b` pasó 15/15; el 53,3% del fixture es un test del detector, no una tasa de fallo de mercado. El informe ahora marca “techo detectado” cuando esto ocurre.
- Detalle y criterios de muerte: [`docs/REALITY-CHECK.md`](docs/REALITY-CHECK.md) y [`docs/OPPORTUNITY.md`](docs/OPPORTUNITY.md).

## Qué NO es

- No es un benchmark de modelos ni una opinión sobre "qué IA es mejor".
- No mide corrección semántica: mide conformidad con un criterio explícito.
- El dataset incluido es **sintético y pequeño** (n=15). Sirve para demostrar el método; un informe vendible usa 200–500 outputs reales del cliente.
- `runs/demo-model` es un fixture, no la auditoría de un proveedor real.
- Ejecutar código generado requiere contenedor o VM. Aquí el radio de daño es un `TemporaryDirectory`.

## Licencia

MIT.
