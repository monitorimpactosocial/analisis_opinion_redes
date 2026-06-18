# Actualizar datos del tablero

El boton **Actualizar datos** abre el workflow manual de GitHub Actions:

`https://github.com/monitorimpactosocial/analisis_opinion_redes/actions/workflows/update-dashboard.yml`

## Uso

1. Entrar con una cuenta de GitHub con permiso sobre el repositorio.
2. Abrir el boton **Run workflow**.
3. Definir `since_days`, por ejemplo `7`.
4. Dejar `write_google=false` para actualizar solo la appweb publica.
5. Usar `write_google=true` solamente si estan cargadas las credenciales Google como secrets.
6. Esperar que termine la accion. Si hay cambios, el workflow commitea `docs/status.json` y GitHub Pages queda actualizado.

## Secrets obligatorios

- `META_ACCESS_TOKEN`: token Meta valido.
- `META_PAGE_ID`: ID de la Pagina a monitorear.

## Secrets recomendados

- `META_PAGE_ACCESS_TOKEN`: token de Pagina, si se usa uno separado.
- `ANONYMIZATION_SALT`: sal estable para anonimizar autores.
- `GOOGLE_SPREADSHEET_ID`: ID del Google Sheet, si se reemplaza el destino por defecto.
- `GOOGLE_DRIVE_FOLDER_ID`: ID de carpeta Drive, si se reemplaza el destino por defecto.
- `GOOGLE_SERVICE_ACCOUNT_JSON`: JSON de service account, solo necesario si `write_google=true`.

## Variables opcionales

- `META_GRAPH_VERSION`: version de Graph API. Si no existe, se usa `v25.0`.
- `META_PAGE_NAME`: nombre visible de la Pagina. Si no existe, se usa `Monitorimpactosocial`.

## Seguridad

La appweb estatica no contiene tokens. El boton no llama directamente a Meta desde el navegador; solo abre una ejecucion protegida por GitHub.
