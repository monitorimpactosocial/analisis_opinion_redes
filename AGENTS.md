# AGENTS.md

## Reglas del proyecto

Este repositorio contiene un ensayo de descarga y analisis de comentarios de redes sociales usando APIs oficiales.

- No automatizar login con usuario y password de Facebook, Instagram ni Google.
- No guardar tokens, passwords, archivos `client_secret*.json`, service accounts, exports reales ni datos personales en git.
- Usar OAuth/tokens oficiales de Meta Graph API y credenciales Google fuera del repo.
- Antes de editar, revisar `git status --branch --short`.
- Mantener `BITACORA.md`, `README.md`, `docs/manual_tecnico.md`, `docs/diccionario_datos.md` y la secuencia de prompts.
- Las salidas reales deben ir a Google Sheets y Drive configurados por variables de entorno.
- Los directorios `outputs/`, `evidence/` y `data/` son locales e ignorados por git.
- Si se trabaja con datos identificables, anonimizar IDs de autores por defecto.

