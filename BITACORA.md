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

Verificacion ejecutada:
- Commit publicado: `3aab6ac1db507721926fb2d3109e326a89a478e5`.
- `git rev-parse HEAD` coincide con `git rev-parse origin/main`.
- `https://raw.githubusercontent.com/monitorimpactosocial/analisis_opinion_redes/main/index.html`: HTTP 200.
- `https://raw.githubusercontent.com/monitorimpactosocial/analisis_opinion_redes/main/docs/index.html`: HTTP 200.
- `https://monitorimpactosocial.github.io/analisis_opinion_redes/?v=3aab6ac`: HTTP 404.
- `https://monitorimpactosocial.github.io/analisis_opinion_redes/docs/?v=3aab6ac`: HTTP 404.

Diagnostico:
- El contenido necesario ya esta en `main`.
- La URL publica todavia requiere habilitar/configurar GitHub Pages para este repositorio o esperar su activacion.

## 2026-06-18 - Validacion inicial de token Meta

Accion:
- Se creo `.env` local desde `.env.example`.
- Se cargo `META_ACCESS_TOKEN` desde el portapapeles sin imprimir el token.
- `.env` permanece ignorado por git.

Comandos/verificaciones:
- `python -m analisis_opinion_redes.cli validate-config`: OK, token presente pero falta `META_PAGE_ID`.
- `python -m analisis_opinion_redes.cli list-pages`: token valido para el usuario `Diego Meza`, pero `pages` devolvio lista vacia.
- Consulta `/me/permissions`: concedidos `pages_show_list`, `business_management`, `pages_read_engagement`, `public_profile`.
- Consulta `/me/businesses`: lista vacia.

Diagnostico:
- El token es valido como token de usuario, pero no expone ninguna Pagina administrada.
- Falta conceder `pages_read_user_content` para leer comentarios generados por usuarios.
- Tambien falta que el usuario/token tenga acceso efectivo a una Pagina de Facebook, o usar la cuenta que tenga control total de la Pagina.

Pendiente:
- Regenerar el token en Graph API Explorer con `pages_show_list`, `pages_read_engagement` y `pages_read_user_content`.
- Confirmar que `/me/accounts?fields=id,name,tasks` devuelva al menos una Pagina.
- Luego completar `META_PAGE_ID` en `.env` y ejecutar `collect`.

## 2026-06-18 - Primera corrida real con Pagina Monitorimpactosocial

Accion:
- Se confirmo que `/me/accounts?fields=id,name,tasks,access_token` ya devuelve la Pagina `Monitorimpactosocial`.
- `META_PAGE_ID` cargado localmente: `1166992559831697`.
- `META_PAGE_ACCESS_TOKEN` cargado en `.env` local sin imprimirlo.
- Se corrigio `src/analisis_opinion_redes/meta_client.py` para usar `tasks` en lugar de `perms`, porque Meta devolvio error `(#100) Tried accessing nonexisting field (perms)`.

Pruebas ejecutadas:
- `python -m compileall src tests`: OK.
- `$env:PYTHONPATH='src'; python -m unittest discover -s tests`: OK, 3 tests.
- `$env:PYTHONPATH='src'; python -m analisis_opinion_redes.cli validate-config`: OK, `meta_ready=true`.
- `$env:PYTHONPATH='src'; python -m analisis_opinion_redes.cli list-pages`: OK, devuelve `Monitorimpactosocial`.
- `$env:PYTHONPATH='src'; python -m analisis_opinion_redes.cli collect`: OK, `run_id=collect_20260618T201156Z`, 0 comentarios.
- `$env:PYTHONPATH='src'; $env:META_SINCE_DAYS='365'; python -m analisis_opinion_redes.cli collect`: OK, `run_id=collect_20260618T201224Z`, 0 comentarios.

Diagnostico API:
- Pagina visible para el token: `Monitorimpactosocial`.
- Consulta directa a la pagina: `posts_returned=0`.
- No hay comentarios para analizar porque la API no devuelve publicaciones visibles.

Google Sheet:
- Se agrego la ejecucion `collect_20260618T201224Z` en `EJECUCIONES`.
- Se agrego metrica cero en `METRICAS_DIARIAS`.
- Se agrego diagnostico `no_posts_visible` en `ERRORES`.

Evidencias Drive:
- CSV real: `https://drive.google.com/file/d/1tfRfRjZII_Sj2bxTos95XR8Ofd9_DBcN/view?usp=drivesdk`.
- Metricas reales: `https://drive.google.com/file/d/1uYhES1nPmbr3VHi7w5aP0ZjNOrvBe7j2/view?usp=drivesdk`.
- Resumen real: `https://drive.google.com/file/d/1t2W6n3fIqd-8IH1mR9OB_0dGcoxZhcVm/view?usp=drivesdk`.

Pendiente:
- Publicar una publicacion de prueba en la Pagina `Monitorimpactosocial` y dejar al menos un comentario.
- Repetir `collect` para validar descarga y analisis de comentario real.
- Regenerar el Page token final porque tokens previos fueron expuestos en capturas/chat.

## 2026-06-18 - Conversion de GitHub Pages en tablero operativo

Problema reportado:
- La pagina publica funcionaba, pero solo era una portada de documentacion y no un tablero util.
- El usuario necesita KPIs, graficas, tablas y conteos de opiniones positivas/negativas sobre su Pagina.

Cambios:
- `index.html` se reemplazo por un tablero operativo.
- `docs/dashboard.js` ahora renderiza KPIs, dona de sentimiento, barras de categorias, tendencia diaria, tabla de alertas, tabla de comentarios y evidencias.
- `docs/status.json` queda como fuente publica de datos del tablero, sin tokens ni autores crudos.
- Se agrego `src/analisis_opinion_redes/dashboard_export.py` para generar el JSON del tablero desde cada corrida.
- `src/analisis_opinion_redes/pipeline.py` ahora exporta `docs/status.json`.
- `.env.example` incluye `META_PAGE_NAME` y `DASHBOARD_STATUS_PATH`.

Alcance aclarado:
- El tablero reporta la Pagina de Facebook conectada por API.
- El perfil personal no se puede monitorear como Pagina mediante Meta Graph API.
- Para metricas de sitio web se debe conectar GA4, Search Console o logs del sitio.
