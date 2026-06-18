# Analisis de opinion en redes

Ensayo operativo para descargar comentarios diarios desde Meta Graph API, analizarlos con un modelo simple basado en reglas y guardar resultados en Google Sheets/Drive.

## Destinos del ensayo

- Google Sheet: `19qCi8dMDZa89OrZhUth5EhQ0qvkrup6PaqTN3BN7NCc`
- Carpeta Drive de evidencias: `1RGaWR4DJLrjHRNOoDEw7tdELaAYACcLd`

## Alcance inicial

- Facebook Pages administradas por el usuario mediante Meta Graph API.
- Comentarios de publicaciones de pagina, no scraping ni login automatizado.
- Analisis simple: sentimiento, tema, urgencia y necesidad de respuesta.
- Persistencia local en `outputs/` y opcional en Google Sheets/Drive.

Importante: una cuenta personal de Facebook puede servir para autorizar OAuth si administra la pagina, pero la API oficial no debe usarse como un robot con password personal. Para perfiles personales, la lectura automatica de comentarios esta muy restringida; el ensayo esta preparado para paginas.

## Instalacion local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
Copy-Item .env.example .env
```

Editar `.env` con tokens y credenciales locales. No commitear `.env`.

## Ensayo con datos de muestra

```powershell
python -m analisis_opinion_redes.cli sample
```

Esto crea archivos locales en `outputs/` y `evidence/`.

Para escribir tambien en Google Sheets y subir evidencia a Drive:

```powershell
$env:WRITE_GOOGLE="true"
python -m analisis_opinion_redes.cli sample --write-google
```

## Ensayo con Meta Graph API

1. Crear una app en Meta Developers.
2. Autorizar con la cuenta humana que administra la pagina.
3. Obtener un token valido con permisos de pagina necesarios.
4. Completar `META_ACCESS_TOKEN`, `META_PAGE_ID` y, si aplica, `META_PAGE_ACCESS_TOKEN`.
5. Ejecutar:

```powershell
python -m analisis_opinion_redes.cli validate-config
python -m analisis_opinion_redes.cli list-pages
python -m analisis_opinion_redes.cli collect --write-google
```

## Estructura de Google Sheet

El workbook se organiza en estas pestanas:

- `CONFIGURACION`: parametros operativos del ensayo.
- `EJECUCIONES`: cada corrida del pipeline.
- `COMENTARIOS`: comentarios analizados.
- `METRICAS_DIARIAS`: agregados diarios por red/cuenta.
- `ALERTAS`: comentarios que requieren atencion.
- `EVIDENCIAS`: archivos generados o subidos.
- `ERRORES`: fallos y bloqueos.

## Seguridad

- No guardar contrasenas ni tokens en el repositorio.
- Usar `ANONYMIZATION_SALT` local para hashear IDs de autores.
- `STORE_AUTHOR_NAME=false` por defecto.
- Revisar las politicas de Meta antes de pasar de ensayo a produccion.

