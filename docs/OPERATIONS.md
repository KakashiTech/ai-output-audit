# Operaciones — correo, aprobación y límites

Este documento describe el modelo **B**: buzón dedicado, envío con aprobación humana y respuestas redactadas con contexto. No es un empleado 24/7; es un sistema que se activa.

## 1. Buzón dedicado

Nunca el correo personal. Crea una cuenta nueva:

- `auditoria@tudominio.com` (mejor), o
- `auditoria.ai.outputs@gmail.com` (si no tienes dominio).

Activa 2FA y genera una **app password** para correo. No me pases la contraseña principal. Guárdala en un archivo local, fuera del repo:

```bash
mkdir -p ~/.config/ai-output-audit
cat > ~/.config/ai-output-audit/mail.env <<'EOF'
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=auditoria.ai.outputs@gmail.com
SMTP_PASSWORD=LA_APP_PASSWORD
SMTP_FROM=auditoria.ai.outputs@gmail.com
SMTP_FROM_NAME=Tu Nombre
IMAP_HOST=imap.gmail.com
IMAP_USER=auditoria.ai.outputs@gmail.com
IMAP_PASSWORD=LA_APP_PASSWORD
EOF
chmod 600 ~/.config/ai-output-audit/mail.env
```

Puedes revocar la app password desde la cuenta de Google en cualquier momento. Si usas un dominio propio, añade SPF, DKIM y DMARC antes de enviar.

## 2. Flujo de aprobación por carpetas

```
outbox/drafts/      yo genero los borradores
outbox/approved/    tú mueves aquí lo que apruebas
outbox/sent/        el script mueve lo enviado
inbox/              respuestas descargadas para que yo las lea
```

Comandos:

```bash
# 1. Generar borradores desde el CSV
python3 scripts/outreach.py draft \
  --csv data/targets.csv \
  --template templates/agency_es.txt \
  --out outbox/drafts

# 2. Revisar y mover a outbox/approved/ lo que quieras enviar

# 3. Envío real (máximo 10 por pasada)
python3 scripts/outreach.py send --dir outbox/approved --limit 10 --send

# 4. Descargar respuestas nuevas
python3 scripts/outreach.py fetch --limit 20 --out inbox

# 5. Estado
python3 scripts/outreach.py status
```

Sin `--send`, el comando solo simula. El script no envía nada que no esté en `approved/`.

## 3. Matriz de autoridad

| Puedo enviar solo | Necesita tu OK | Nunca |
|---|---|---|
| Acuse de recibo, agendar, pedir 20 outputs, explicar el método, seguimiento, enviar el informe | Precio, alcance, plazo, descuento, NDA, promesas de resultados, condiciones legales | Firmar, facturar, certificar seguridad, aceptar responsabilidad, usar el RUT de otro |

Si un cliente pide algo de la columna “tu OK”, el borrador se queda en `drafts/` con una nota `APROBAR:` y no se envía.

## 4. SLA y tono

- Respuesta humana en **< 24 h laborables**.
- Técnico: con evidencia o con “no lo sé todavía; necesito ver 20 outputs”.
- Comercial: “lo consulto y te confirmo hoy”.
- Nunca: “te lo mando cuando pueda”.

## 5. Rutina diaria (30–45 min)

| Hora | Acción |
|---|---|
| 9:00 | `fetch`, leer respuestas, clasificar |
| 9:20 | Redactar 10 respuestas/borradores |
| 9:50 | Aprobar y `send` |
| 16:00 | Seguimientos a 3 y 7 días |
| Viernes | Métricas: enviados, respuestas, llamadas, propuestas, ingresos |

## 6. Métricas y umbrales

| Métrica | Mínimo | Si no |
|---|---:|---|
| Enviados | 40 en 14 días | No estás ejecutando |
| Respuestas | 8 | Mensaje o segmento mal |
| Llamadas | 3 | No hay dolor real |
| Propuestas | 2 | No llegas a quien firma |
| Primer ingreso | 1 | Precio/posicionamiento mal |

## 7. Seguridad

- 2FA en el correo; app password solo para este uso.
- `mail.env` con `chmod 600`; nunca en el repo ni en un chat.
- Revisa `outbox/sent.jsonl` una vez por semana.
- Si sospechas acceso, revoca la app password y cámbiala.
- No automatices más de 10 envíos/día desde una cuenta nueva.
- Texto plano, sin adjuntos, con dirección física y opción de baja.

## 8. Datos del cliente

- NDA antes de recibir nada.
- Anonimiza antes de que el dato salga de su empresa.
- Ejecuta en local o contenedor. Nada de APIs gratuitas con datos de cliente.
- Borra a los 30 días y confírmalo por escrito.
- El repo público solo contiene datos sintéticos.

## 9. Cuando un cliente dice “sí”

1. NDA firmado.
2. Intake: 20–50 outputs + input + criterio + 3–5 reglas + contacto técnico.
3. 50% o piloto gratis firmado.
4. Ejecutar, revisar fallos a mano, generar informe.
5. Llamada de entrega de 30 min (o video + email).
6. Factura y suite de regresión.
7. Pedir testimonio anonimizado y permiso para publicar el caso.

## 10. Lo que no hace este sistema

- No hace llamadas.
- No firma ni factura.
- No está disponible 24/7.
- No decide precio sin ti.
- No envía correos masivos ni compra listas.
