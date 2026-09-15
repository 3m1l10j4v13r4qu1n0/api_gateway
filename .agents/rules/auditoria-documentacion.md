# Auditoría de documentación — actualizar plan de implementacion

Regla dura. Aplica a agentes y humanos por igual.

## 1. Contexto y por qué existe

Cuando se audita documentación del proyecto (requerimientos, especificaciones, planes,
contratos con los microservicios), el resultado no puede quedarse solo en un informe
aparte: el documento fuente del área afectada debe quedar **actualizado** para seguir
siendo la fuente de verdad.

## 2. Alcance

- Aplica a auditorías de cualquier documento de `docs/` (plan de implementación,
  estado actual, contratos/endpoints de los microservicios).

## 3. Pasos obligatorios

1. **Identificar** el área del documento auditado (gateway, ruteo, infraestructura,
   contrato con auth :8001, contrato con afiliados :8002).
2. **Leer completo** el archivo antes de editarlo (nunca editar sin releer).
3. **Marcar** con la leyenda de la sección 4 cada ítem según el estado verificado en la sesión.
4. **Aplicar** en el archivo las correcciones que surjan de la auditoría y estén
   verificadas (typos, valores, envs de ejemplo, estados).

## 4. Leyenda de estados

| Símbolo | Significado |
|---|---|
| ✅ | listo / ya cubierto por el proyecto (verificado en la sesión) |
| 🟡 | parcial: difiere levemente entre documentos o falta alinear |
| 🔵 | pendiente externo: depende de otro equipo / otro repo de microservicio |
| ⏳ | en proceso / bloqueado temporalmente |

## 5. Anti-alucinación

- Marcar ✅ **solo** lo verificado en la sesión actual (archivo leído, comando corrido).
- No cambiar estados que dependan de decisiones externas no confirmadas (ej. "microservicio
  en Docker" no se marca ✅ porque lo diga un plan: hay que verificar el docker-compose real).
- Releer el archivo tras editarlo (`.agents/rules/Reglas-anti-alucinacion.md` §4).

## 6. Cierre de la auditoría

1. Generar o actualizar el informe versionado en `docs/auditorias/auditoria-*.md`,
   referenciando el archivo modificado.
2. Actualizar `docs/estado_actual_proyecto.md` (sección correspondiente, in-place).
3. Agregar entrada en `docs/vitacora_agentica.md` (append-only) con fecha, qué se hizo,
   decisiones, archivos tocados y estado resultante.