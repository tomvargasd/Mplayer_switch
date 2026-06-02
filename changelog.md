### Changelog

#### MP3 Player for Nintendo Switch Homebrew — v0.1.1
* Fix de la posición del botón Play/Pause
* AlwaysOnDisplay implementado (se desactiva al cerrar la app)
* Agregado un numerador en la playlist

#### MP3 Player for Nintendo Switch Homebrew — v0.1.0
* Reproducción de archivos MP3 desde sdmc:/Music
* Interfaz SDL2 con layout a 1280×720 (modo portátil)
  * Header/footer, panel de reproductor, lista de reproducción (10 tracks visibles)
  * Arte de álbum (APIC extraído del MP3)
  * Barra de progreso y botones Prev/Play/Next
* Sistema de temas vía romfs:/themes/ con archivos theme.json
  * Selector de temas en pantalla (tecla Y → DPad + A)
  * Fallback a paleta interna si no hay temas
* Tema incluido: Cyberpunk Purple