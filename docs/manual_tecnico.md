# Manual tecnico

## Objetivo

Automatizar un ensayo diario de comentarios en Facebook Pages con Meta Graph API, analisis simple y escritura en Google Sheets/Drive.

## Flujo

1. Validar configuracion local.
2. Descargar publicaciones recientes de una pagina.
3. Descargar comentarios de esas publicaciones.
4. Anonimizar autor por hash.
5. Analizar sentimiento, categoria, urgencia y necesidad de respuesta.
6. Guardar JSONL, CSV, metricas y evidencia local.
7. Exportar `docs/status.json` para el tablero publico de GitHub Pages.
8. Si `WRITE_GOOGLE=true`, escribir en Sheets y subir archivos a Drive.
9. Si la corrida viene de GitHub Actions, commitear `docs/status.json` y publicarlo por GitHub Pages.

## Variables criticas

- `META_ACCESS_TOKEN`: token de usuario o pagina obtenido por OAuth.
- `META_PAGE_ID`: ID de la pagina a monitorear.
- `META_PAGE_ACCESS_TOKEN`: opcional si se usa token especifico de pagina.
- `ANONYMIZATION_SALT`: secreto local para hashes estables.
- `GOOGLE_APPLICATION_CREDENTIALS`: service account compartida con Sheet/Drive, si se usa esa via.
- `GOOGLE_SPREADSHEET_ID`: workbook de resultados.
- `GOOGLE_DRIVE_FOLDER_ID`: carpeta de evidencias.
- `DASHBOARD_STATUS_PATH`: ruta del JSON publico del tablero, por defecto `docs/status.json`.

## Tablero publico

`index.html` funciona como tablero operativo y lee `docs/status.json`.

El tablero muestra:

- KPIs: comentarios, positivos, negativos, neutros, alertas y publicaciones visibles.
- Graficas: dona de sentimiento, barras de categorias y tendencia diaria.
- Tablas: alertas, comentarios recientes y evidencias.
- Diagnostico y siguiente paso operativo.
- Boton de actualizacion manual protegida en GitHub Actions.

No se deben publicar tokens, passwords ni autores crudos en `docs/status.json`. El exportador omite identificadores de autores y solo publica datos operativos.

## Actualizacion con GitHub Actions

El workflow `.github/workflows/update-dashboard.yml` se ejecuta manualmente desde GitHub Actions. La appweb enlaza a ese workflow con el boton **Actualizar datos**.

Configuracion minima:

- Secrets `META_ACCESS_TOKEN` y `META_PAGE_ID`.
- Secret recomendado `META_PAGE_ACCESS_TOKEN`.
- Secret recomendado `ANONYMIZATION_SALT`.
- Variables opcionales `META_GRAPH_VERSION` y `META_PAGE_NAME`.

Para escribir resultados en Google Sheets/Drive desde el workflow:

- Ejecutar con `write_google=true`.
- Cargar `GOOGLE_SERVICE_ACCOUNT_JSON` como secret.
- Compartir el Google Sheet y la carpeta Drive con el service account.

Por seguridad, el frontend estatico no llama a Meta ni contiene tokens.

## Validaciones

```powershell
python -m compileall src tests
$env:PYTHONPATH="src"
python -m unittest discover -s tests
python -m analisis_opinion_redes.cli validate-config
python -m analisis_opinion_redes.cli sample
node --check docs/dashboard.js
python -m json.tool docs/status.json
```

## Restricciones conocidas

- No descarga comentarios de perfiles personales mediante password.
- Requiere permisos de Meta y, para produccion, posible App Review.
- La calidad del modelo inicial es basica; sirve para clasificacion operativa preliminar.
