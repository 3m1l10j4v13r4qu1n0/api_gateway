# Reglas de verificación y flujo controlado

Estas reglas aplican a TODO trabajo del agente en este repo, no solo a
un skill puntual. El objetivo es que el agente actúe siempre sobre
evidencia verificada en la sesión actual, no sobre supuestos.

## 1. Verificar antes de afirmar

- Antes de decir "el proyecto usa X" o "ya existe Y", el agente debe
  haber leído ese archivo/símbolo en el turno actual (no de memoria de
  turnos anteriores de otra sesión).
- Si no lo verificó, debe decir "asumo que..." o preguntar, nunca
  presentarlo como hecho confirmado.

## 2. No inventar superficie de código

- Nombres de clases, métodos, rutas de archivos, endpoints o campos de
  modelos: solo se usan si se vieron en el código real de esta sesión,
  o se marcan explícitamente como "nuevo, a crear".
- Librerías y versiones: solo se citan si se verificaron en
  `requirements.txt` / `pyproject.toml` / `package.json` en esta sesión.

## 3. Trabajo en pasos chicos, no en bloques grandes

- Un caso de uso, un endpoint, o un componente por vez cuando el
  cambio toca más de un archivo o capa.
- Antes de pasar al siguiente paso, mostrar qué se hizo y qué falta
  confirmar. No encadenar varios pasos sin que el usuario los vea.

## 4. Releer después de escribir

- Después de crear o modificar un archivo, releerlo antes de seguir
  con el próximo paso del flujo. No asumir que el archivo quedó como
  se planeó solo porque la escritura no dio error.

## 5. Ambigüedad → pregunta, no silencio

- Decisiones de arquitectura (patrones, dónde vive un modelo, JWT vs
  sesión, etc.) que no estén explícitamente definidas por el usuario o
  por el código existente: preguntar antes de decidir por cuenta propia.

## 6. Confirmación explícita en cambios transversales

- Cualquier cambio que toque más de una HU/módulo a la vez requiere
  confirmación explícita del usuario antes de aplicarse, no solo
  antes de "seguir".

## 7. Reporte de cada paso

Cada respuesta que implique cambios de código debe incluir, en este
orden:
1. Qué se verificó (archivos leídos, comandos corridos).
2. Qué se propone o cambió.
3. Qué queda pendiente de confirmar o decidir.