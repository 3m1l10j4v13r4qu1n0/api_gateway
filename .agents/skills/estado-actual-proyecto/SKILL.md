---
name: estado-actual-proyecto
description: contexto actual del proyecto para nuevas sesiones
disable-model-invocation: true
---


# Estado Actual del Proyecto

> Última actualización: YYYY-MM-DD
> Este archivo es una FOTO del presente, no un historial. Para el historial de cambios ver `vitacora_agentica.md`.
> El agente debe leer este archivo completo al iniciar cualquier tarea sobre el proyecto.

## 1. Resumen del proyecto
<!-- 2-4 líneas: qué es, para qué existe, stack principal -->

## 2. Arquitectura
<!-- Capas, patrones (Clean Architecture / Hexagonal / DDD, etc.), decisiones estructurales vigentes -->

## 3. Entidades / Modelos de dominio
<!-- Lista de entidades principales con 1 línea de descripción cada una -->

- `NombreEntidad` — descripción breve

## 4. Casos de uso / Servicios implementados
<!-- Qué funcionalidad de negocio existe hoy -->

- [x] Caso de uso X — implementado
- [ ] Caso de uso Y — iniciado, falta Z

## 5. Endpoints / Interfaces expuestas
<!-- API REST, CLI, eventos, etc. -->

| Método | Ruta | Descripción | Estado |
|---|---|---|---|
| POST | /ejemplo | ... | ✅ |

## 6. Infraestructura / Integraciones
<!-- DB, colas, servicios externos, variables de entorno relevantes -->

## 7. Pendientes / TODO conocidos
<!-- Cosas iniciadas pero no terminadas, deuda técnica identificada -->

## 8. Decisiones y convenciones vigentes
<!-- Cosas que el agente NO debe romper o reinterpretar: convenciones de nombres, capas que no se deben saltear, etc. -->