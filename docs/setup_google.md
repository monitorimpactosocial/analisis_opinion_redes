# Setup Google Sheets y Drive

## Destinos

- Sheet: `19qCi8dMDZa89OrZhUth5EhQ0qvkrup6PaqTN3BN7NCc`
- Drive folder: `1RGaWR4DJLrjHRNOoDEw7tdELaAYACcLd`

## Opcion con service account

1. Crear service account en Google Cloud.
2. Descargar JSON a una carpeta segura fuera del repo.
3. Compartir el Sheet y la carpeta Drive con el correo de la service account.
4. Definir:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\secure\service_account.json"
$env:WRITE_GOOGLE="true"
```

## Opcion con credenciales de usuario

Si se usa Google Cloud SDK:

```powershell
gcloud auth application-default login
$env:WRITE_GOOGLE="true"
```

## Validacion

```powershell
python -m analisis_opinion_redes.cli sample --write-google
```

