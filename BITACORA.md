# Bitacora

## 2026-06-18 - Scaffold inicial del ensayo

Objetivo:
- Preparar un repositorio vacio para ensayar descarga y analisis diario de comentarios de redes sociales.

Decisiones:
- Usar Meta Graph API, no automatizacion de login con password.
- Enfocar el primer ensayo en Facebook Pages administradas por el usuario.
- Mantener datos reales, tokens y evidencias locales fuera de git.
- Guardar resultados en el Google Sheet `ANALISIS_REDES` y evidencias en la carpeta Drive `ANALISIS_REDES`.

Archivos creados:
- `README.md`
- `AGENTS.md`
- `.env.example`
- `pyproject.toml`
- `src/analisis_opinion_redes/*`
- `docs/*`
- `samples/facebook_comments_sample.json`
- `tests/test_analyzer.py`

Pruebas previstas:
- `python -m compileall src tests`
- `python -m unittest discover -s tests`
- `python -m analisis_opinion_redes.cli sample`

Pruebas ejecutadas:
- `python -m compileall src tests`: OK.
- `$env:PYTHONPATH='src'; python -m unittest discover -s tests`: OK, 3 tests.
- `$env:PYTHONPATH='src'; python -m analisis_opinion_redes.cli validate-config`: OK, Meta no configurado.
- `$env:PYTHONPATH='src'; python -m analisis_opinion_redes.cli sample`: OK.

Resultados de la corrida de muestra:
- `run_id`: `sample_20260618T191120Z`.
- Comentarios procesados: 3.
- Alertas generadas: 2.
- Sentimiento: 1 positivo, 1 neutro, 1 negativo.
- Categorias: elogio, consulta, reclamo.

Google Sheet:
- URL: `https://docs.google.com/spreadsheets/d/19qCi8dMDZa89OrZhUth5EhQ0qvkrup6PaqTN3BN7NCc/edit`.
- Pestanas creadas: `CONFIGURACION`, `EJECUCIONES`, `COMENTARIOS`, `METRICAS_DIARIAS`, `ALERTAS`, `EVIDENCIAS`, `ERRORES`.
- Se cargaron encabezados, configuracion, comentarios de muestra, metricas, alertas y evidencia.

Evidencias Drive:
- CSV: `https://drive.google.com/file/d/1j5uGElc4_naeiKje2-phG3Gda5g1gUZR/view?usp=drivesdk`.
- Metricas JSON: `https://drive.google.com/file/d/1zYf-CyRCc_06zMS8bcoBKFjSpXluVo_v/view?usp=drivesdk`.
- Resumen Markdown: `https://drive.google.com/file/d/1Dfyb8eerIksGex0ks167V4gZTQcmoU-n/view?usp=drivesdk`.

Pendientes reales:
- Crear/autorizar app Meta y completar token local.
- Confirmar `META_PAGE_ID` de la pagina administrada.
- Configurar credenciales Google locales si el pipeline se ejecutara fuera de Codex.

## 2026-06-18 - Correccion de GitHub Pages 404

Problema reportado:
- Al acceder por GitHub Pages, la raiz publica o la ruta `/docs/` podia devolver `404 File not found`.
- El repositorio tenia README y documentos Markdown, pero no tenia `index.html` para la fuente publicada por Pages.

Cambios:
- Se agrego `index.html` en la raiz para Pages configurado desde `/`.
- Se agrego `docs/index.html` para Pages configurado desde `/docs`.
- Se agrego `docs/404.html` para una pantalla de error util.
- Se agrego `docs/docs/index.html` como alias defensivo si el usuario entra a `/docs/` mientras Pages publica desde la carpeta `docs`.
- Se agrego `docs/site.css` para una portada liviana con enlaces a manuales, credenciales, diccionario, secuencia de prompts y Google Sheet.

Verificacion prevista:
- `git status --branch --short`.
- Publicar commit y revalidar `https://monitorimpactosocial.github.io/analisis_opinion_redes/` y `https://monitorimpactosocial.github.io/analisis_opinion_redes/docs/` tras propagacion de GitHub Pages.
