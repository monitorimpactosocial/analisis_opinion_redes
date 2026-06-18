# Diccionario de datos

## COMENTARIOS

- `run_id`: identificador de corrida.
- `network`: red social de origen.
- `source_account`: pagina o cuenta monitoreada.
- `post_id`: identificador de publicacion.
- `post_url`: enlace de publicacion.
- `post_created_at`: fecha/hora de publicacion.
- `comment_id`: identificador del comentario.
- `comment_created_at`: fecha/hora del comentario.
- `message`: texto del comentario.
- `author_id_hash`: hash del autor, no ID crudo.
- `author_name`: nombre del autor solo si `STORE_AUTHOR_NAME=true`.
- `like_count`: reacciones/likes reportados por API.
- `reply_count`: respuestas al comentario.
- `parent_id`: comentario padre si aplica.
- `sentiment`: positivo, neutro o negativo.
- `sentiment_score`: puntaje numerico basado en reglas.
- `category`: tema operativo detectado.
- `urgency`: normal, media o alta.
- `needs_response`: indicador de seguimiento.
- `matched_keywords`: palabras que dispararon reglas.

## METRICAS_DIARIAS

- `comments_total`: total de comentarios por dia/red/cuenta.
- `positive_total`: comentarios positivos.
- `neutral_total`: comentarios neutros.
- `negative_total`: comentarios negativos.
- `alerts_total`: comentarios que requieren respuesta.
- `top_categories`: categorias principales con conteo.

## EVIDENCIAS

- `artifact_type`: tipo de archivo generado.
- `file_name`: nombre del archivo.
- `drive_url`: enlace Drive si fue subido.
- `local_path`: ruta local de ejecucion.
- `sha256`: hash de integridad del archivo.

## docs/status.json

- `generated_at_utc`: fecha UTC de generacion del estado publico.
- `scope_note`: alcance visible del tablero.
- `meta_page`: pagina Meta conectada sin tokens.
- `latest_run`: resumen de la ultima corrida.
- `sentiment`: conteos agregados por sentimiento.
- `categories`: categorias principales.
- `trend`: serie diaria publicada.
- `alerts`: alertas recientes sin datos sensibles de autor.
- `comments`: comentarios recientes sin identificadores crudos de autor.
- `destinations`: enlaces operativos a Sheet y Drive.
- `automation.workflow_url`: enlace al workflow manual de actualizacion.
- `automation.mode`: modo de actualizacion publicado.
- `evidence`: evidencias publicas de la ultima corrida.
- `security_note`: nota de seguridad del JSON publico.
