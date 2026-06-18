# Setup Meta Graph API

## Ruta recomendada

1. Crear una app en Meta Developers.
2. Agregar el producto correspondiente para Facebook Login / Graph API.
3. Autorizar con la cuenta humana que administra la pagina.
4. Obtener permisos de pagina para leer contenido y engagement segun el alcance aprobado.
5. Usar `list-pages` para identificar el `META_PAGE_ID`.
6. Ejecutar `collect` con limites bajos para el primer ensayo.

## Comandos

```powershell
python -m analisis_opinion_redes.cli validate-config
python -m analisis_opinion_redes.cli list-pages
python -m analisis_opinion_redes.cli collect --write-google
```

## No hacer

- No guardar password de Facebook.
- No guardar tokens en README, BITACORA ni commits.
- No usar scraping de la interfaz web.
- No mezclar datos reales en `samples/`.

