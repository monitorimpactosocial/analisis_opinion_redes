# Secuencia de prompts - Analisis opinion redes

Ultima edicion: 2026-06-18

## Prompt 1

El usuario pidio investigar si era posible automatizar descarga y analisis diario de comentarios de Facebook e Instagram, indicando que cuenta con credenciales de acceso.

Respuesta operativa:
- Se recomendo usar APIs oficiales de Meta y OAuth.
- Se descarto guardar passwords o automatizar login.
- Se propuso un pipeline con webhooks/job diario, Google Sheets/Drive y clasificacion de comentarios.

## Prompt 2

El usuario pidio crear un ensayo en el repositorio GitHub `monitorimpactosocial/analisis_opinion_redes.git`, usar una cuenta humana de Facebook como autorizadora, guardar resultados/metricas en el Google Sheet indicado y evidencias en la carpeta Drive indicada.

Respuesta operativa:
- Se preparo un scaffold Python para Meta Graph API.
- Se dejaron variables de entorno para tokens y credenciales.
- Se prepararon tabs de Google Sheet y evidencia de corrida.
- Se mantuvo la cuenta humana fuera del codigo y de los commits.

## Resultado de la corrida inicial

- Repo local preparado en `analisis_opinion_redes`.
- Sheet `ANALISIS_REDES` estructurado con pestanas operativas.
- Corrida de muestra `sample_20260618T191120Z`.
- 3 comentarios anonimos de muestra procesados.
- 2 alertas generadas.
- 3 archivos de evidencia subidos a Drive.
- Descarga real de Facebook pendiente hasta configurar token OAuth y `META_PAGE_ID`.

## Prompt 4

El usuario reporto que al acceder al enlace principal ve el README, pero al entrar por `docs` GitHub Pages devuelve `404 File not found`.

Respuesta operativa:
- Se diagnostico falta de `index.html` para GitHub Pages.
- Se agrego portada en la raiz del repo.
- Se agrego indice en `docs/index.html`.
- Se agrego `docs/404.html` y alias `docs/docs/index.html` para cubrir rutas comunes.
- Se dejo pendiente verificar la URL publica luego del push y la propagacion de GitHub Pages.
