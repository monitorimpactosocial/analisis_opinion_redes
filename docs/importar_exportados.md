# Importar archivos exportados

Esta via evita el bloqueo de `pages_read_user_content`: se descarga o arma un archivo local con comentarios y el pipeline lo analiza como fuente operativa.

## Formatos soportados

- CSV, TSV o TXT delimitado por coma, punto y coma, tabulador o barra vertical.
- JSON con lista de comentarios.
- JSONL con un comentario por linea.
- JSON con estructura tipo `posts[].comments[]`.

Los exports reales deben guardarse fuera de git, por ejemplo:

```powershell
data\imports\comentarios_facebook_2026-06-19.csv
```

La carpeta `data/` esta ignorada por git.

## Columnas reconocidas

El importador acepta nombres en ingles o espanol. Las mas importantes son:

- Texto: `message`, `comment`, `comentario`, `texto`, `content`, `opinion`.
- Fecha: `created_time`, `comment_created_at`, `created_at`, `fecha`, `fecha_comentario`, `timestamp`.
- Red: `network`, `red`, `platform`, `plataforma`.
- Pagina/cuenta: `source_account`, `page_name`, `pagina`, `page`, `account`, `cuenta`.
- Autor: `author_id`, `author`, `autor`, `user_name`, `from_name`.
- Enlace: `post_url`, `permalink_url`, `url`, `link`, `enlace`.
- Interacciones: `like_count`, `likes`, `me_gusta`, `reply_count`, `respuestas`.

Si no hay ID de comentario, el pipeline genera uno estable a partir del archivo, la fila, fecha y texto.

## Ejecutar importacion

```powershell
Set-Location -LiteralPath "G:\Mi unidad\MANUAL_MAESTRO_FORMATOS_FUNCIONES_APPWEB\analisis_opinion_redes"

$env:PYTHONPATH = "src"

python -m analisis_opinion_redes.cli import-file `
  --input "data\imports\comentarios_facebook_2026-06-19.csv" `
  --network facebook `
  --source-account Monitorimpactosocial

python -m json.tool .\docs\status.json > $null

git add .\docs\status.json
git commit -m "Update dashboard from exported comments"
git push origin main
```

## Escribir tambien en Google Sheets y Drive

Si estan configuradas las credenciales Google:

```powershell
$env:WRITE_GOOGLE = "true"

python -m analisis_opinion_redes.cli import-file `
  --input "data\imports\comentarios_facebook_2026-06-19.csv" `
  --source-account Monitorimpactosocial `
  --write-google
```

## Probar con muestra ficticia

```powershell
$env:PYTHONPATH = "src"
python -m analisis_opinion_redes.cli import-file --input samples\exported_comments_sample.csv --source-account Monitorimpactosocial
```

La muestra no contiene datos reales.
