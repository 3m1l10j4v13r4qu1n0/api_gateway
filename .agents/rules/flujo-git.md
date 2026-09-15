# Flujo de Git — SGVIR

Reglas obligatorias de ramas, commits y merges. Aplican a agentes y humanos por igual.

## Ramas

- **Prohibido** trabajar directamente sobre `main` o `develop`.
- Crear `feature/<tema>` o `fix/<tema>` **siempre desde `develop`**.
- Una rama = una tarea/HU coherente. Mantener ramas cortas (PRs chicos se revisan mejor).

```text
main
└── develop
    ├── feature/hu-09-nueva-pantalla
    ├── fix/validacion-descuento
    └── docs/actualizar-readme
```

## Commits

- **Conventional Commits en español**, scope en minúscula:
  - `feat(routing): se agrega ruteo hacia el servicio de X`
  - `fix(backend): se corrige validacion de plazo en cambios`
  - `docs(rules): se agrega regla de flujo de git`
- Prohibido mensajes vagos ("cambios", "arreglos", "update", "cosas varias").
- Un tema por commit (commits atómicos). Si el commit necesita "y" para describirse, son dos commits.

## Antes de mergear a develop

1. Integrar primero `origin/develop` **dentro de la rama feature** (`git fetch` + `git merge origin/develop`) y resolver los conflictos ahí, no en develop.
2. Checklist obligatorio, todo en verde antes del merge:
   - Backend: `venv/bin/ruff check .` · `venv/bin/black --check .` · `venv/bin/python -m pytest`
   - Frontend: `npm run lint` · `npm run build` · `npm run test`
3. Solo entonces mergear a `develop`.
4. Pushear únicamente cuando el usuario lo pida o lo apruebe explícitamente.

## Limpieza

- Borrar las ramas ya mergeadas (local con `git branch -d`, que solo borra si está integrada).
- Para remotas, verificar antes con `git branch -r --merged develop` y luego `git push origin --delete <rama>`.
- Nunca borrar `main` ni `develop`.
