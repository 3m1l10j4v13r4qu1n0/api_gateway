# Versionado por Fases — Commits Atómicos y Tags

Reglas obligatorias para el cierre de cada fase del plan (`docs/plan_implementacion.md`).
Aplican a agentes y humanos por igual.

## Al terminar una fase

1. **Commits atómicos**: dividir el trabajo de la fase en commits chicos de un solo
   tema, con **Conventional Commits en español** y scope en minúscula
   (`feat(routing): se agrega ruteo hacia el servicio de X`, `chore(cfg): se andamia el repo`).
   Si el mensaje necesita "y" para describirse, son dos commits. Seguir el detalle de
   `.agents/rules/flujo-git.md`.
2. **Checklist previa en verde**: `venv/bin/ruff check .` · `venv/bin/black --check .` ·
   `venv/bin/python -m pytest` (una vez que existan tests).
3. **Tag anotado** sobre el último commit de la fase, **no** push por ahora.

## Tag por fase

- **Versión**: semver. Cada fase terminada incrementa la versión **menor**
  (`v1.0.0` → Fase 1, `v1.1.0` → Fase 2, `v1.2.0` → Fase 3…). La versión mayor solo
  cambia por decisión del equipo (producto nuevo, breaking changes, hito mayor).
- **Nombre**: acorde a la fase del plan (ej. `v1.0.0` para "Andamiaje",
  `v1.1.0` para "Gateway local", `v1.2.0` para "Docker Compose").
- **Comentario corto** que explique qué se implementó en la fase, con el nombre de la
  fase y el entregable principal. Crear SIEMPRE anotado:

  ```bash
  git tag -a v1.1.0 -m "Fase 2 - Gateway local: ruteo httpx, dashboard y proxy streaming hacia auth y afiliados"
  ```

- Si una fase se corrige después del tag, se versiona con `vX.Y.Z+1` (patch) o se
  re-tagea la corrección; nunca reescribir un tag ya pusheado.

## Push (prohibido sin preguntar)

- **Nunca** pushear la rama ni el tag sin aprobación explícita del usuario: primero
  preguntar (ej. "¿Pusheo la rama `feature/…` y el tag `vX.Y.Z`?").
- El push de la rama y el del tag son dos operaciones; se hacen juntos solo si el
  usuario lo aprueba.
- No mergear a `develop` ni a `main` por cuenta propia. Seguir el resto de
  `.agents/rules/flujo-git.md`.