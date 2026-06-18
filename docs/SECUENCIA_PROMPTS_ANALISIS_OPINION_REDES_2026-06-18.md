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
- Se verifico que los HTML existen en `main` por raw GitHub con HTTP 200.
- La URL `monitorimpactosocial.github.io/analisis_opinion_redes/` seguia en HTTP 404, por lo que falta habilitar/configurar GitHub Pages o esperar activacion.

## Prompt 5

El usuario indico que ya tenia el token de Meta en el portapapeles.

Respuesta operativa:
- Se cargo el token en `.env` local sin imprimirlo ni commitearlo.
- El token valido el usuario `Diego Meza`.
- `/me/accounts` devolvio `pages: []`.
- `/me/permissions` mostro `pages_show_list`, `business_management`, `pages_read_engagement` y `public_profile`.
- `/me/businesses` devolvio lista vacia.
- Diagnostico: falta acceso efectivo a una Pagina o regenerar token incluyendo `pages_read_user_content`; aun no se puede ejecutar `collect` real.

## Prompt 6

El usuario confirmo que `/me/accounts?fields=id,name,tasks,access_token` ya devuelve la Pagina `Monitorimpactosocial`.

Respuesta operativa:
- Se cargo `META_PAGE_ID=1166992559831697` en `.env` local.
- Se cargo el Page access token en `.env` local sin imprimirlo ni commitearlo.
- Se corrigio el cliente Meta para leer `tasks` en vez de `perms`.
- `list-pages` devolvio `Monitorimpactosocial`.
- `collect` real ejecuto sin error, pero devolvio 0 comentarios.
- Diagnostico directo: la pagina es visible para la API, pero `/posts` no devuelve publicaciones visibles.
- Se registraron la ejecucion real, metricas cero y evidencias en Google Sheet/Drive.
- Pendiente: publicar una publicacion de prueba con comentario y repetir la corrida; regenerar token final porque hubo tokens expuestos.

## Prompt 7

El usuario aclaro que necesita un tablero que reporte todo sobre su pagina/perfil: opiniones, positivos, negativos, graficas y tablas.

Respuesta operativa:
- Se reconocio que la pagina anterior solo era una portada documental.
- Se transformo GitHub Pages en tablero operativo con KPIs, graficas y tablas.
- Se agrego `docs/status.json` como fuente publica sin secretos.
- Se agrego exportador Python para regenerar el JSON desde cada corrida.
- Se aclaro que el perfil personal no es accesible como Pagina por Meta API; el tablero actual cubre la Pagina de Facebook y deja sitio web/GA4 como fuente pendiente.
- Se publico el tablero en GitHub Pages y se verifico la URL publica con `docs/status.json` respondiendo HTTP 200.

## Prompt 8

El usuario creo un comentario positivo con otro usuario y pregunto como se actualiza la appweb porque no aparecia.

Respuesta operativa:
- Se explico que GitHub Pages es estatico: hay que correr `collect`, regenerar `docs/status.json`, commitear y pushear.
- Se ejecuto `collect` con `META_SINCE_DAYS=7`.
- Resultado `collect_20260618T205625Z`: 0 comentarios.
- Se consultaron endpoints directos: `feed`, `posts`, `published_posts`, `visitor_posts` y `ratings`.
- Diagnostico: feed/posts/visitor_posts devolvieron 0; ratings requiere `pages_read_user_content`.
- Se preparo el tablero para mostrar esta ultima corrida y el diagnostico.

## Prompt 9

El usuario pidio agregar un boton a la app para ejecutar la actualizacion.

Respuesta operativa:
- Se agrego el boton **Actualizar datos** al tablero publico.
- Se creo el workflow manual `.github/workflows/update-dashboard.yml`.
- El workflow usa GitHub Secrets para Meta, ejecuta `collect`, regenera `docs/status.json`, lo commitea y lo pushea.
- Se documento el uso en `docs/actualizar_datos.md`, `README.md`, `docs/manual_tecnico.md` y `docs/diccionario_datos.md`.
- Se mantuvo la actualizacion protegida: el frontend no contiene tokens ni llama directamente a Meta.
