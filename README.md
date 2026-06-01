# MP3 Player — Nintendo Switch Homebrew

Reproductor de música MP3 nativo para Homebrew de Nintendo Switch.  
Stack: **libnx · SDL2 · SDL2\_image · SDL2\_mixer · nlohmann/json** — compilado con devkitA64 (C++17).

---

## Requisitos previos

| Herramienta | Versión mínima | Notas |
|---|---|---|
| [devkitPro](https://devkitpro.org/wiki/Getting_Started) | cualquier reciente | Incluye devkitA64, libnx, elf2nro |
| macOS / Linux | — | Windows funciona con MSYS2 provisto por devkitPro |
| Python 3.9+ | opcional | Solo para el Theme Editor |

---

## 1 — Instalar devkitPro

Sigue la guía oficial para tu SO:  
<https://devkitpro.org/wiki/Getting_Started>

Una vez instalado, el instalador crea `/opt/devkitpro/` (macOS/Linux).

---

## 2 — Instalar las dependencias de Switch

Abre una terminal y ejecuta:

```bash
sudo dkp-pacman -Sy
sudo dkp-pacman -S switch-dev switch-sdl2 switch-sdl2_image switch-sdl2_mixer
```

Esto instala:
- `libnx` — API de Horizon OS
- `SDL2`, `SDL2_image`, `SDL2_mixer` — gráficos y audio
- `mpg123`, `libpng`, `libjpeg`, etc. — dependencias transitivas
- `elf2nro` — convierte el ELF final al NRO ejecutable por la consola

---

## 3 — Clonar / abrir el proyecto

```bash
cd /ruta/a/mplayer
```

La estructura esperada es:

```
mplayer/
├── Makefile
├── include/
│   └── nlohmann/
│       └── json.hpp          ← ver paso 4
├── source/
│   └── main.cpp
├── romfs/
│   ├── assets/               ← PNGs opcionales del tema base
│   └── themes/               ← temas generados con el Theme Editor
└── tools/
    └── theme_editor/
        ├── app.py
        └── requirements.txt
```

---

## 4 — Descargar nlohmann/json

El proyecto usa la librería de JSON como un único header.  
Ya debería estar en `include/nlohmann/json.hpp` si ejecutaste el comando del README anterior.  
Si no, descárgalo manualmente:

```bash
curl -Lo include/nlohmann/json.hpp \
  https://github.com/nlohmann/json/releases/download/v3.11.3/json.hpp
```

Verifica que existe:

```bash
ls -lh include/nlohmann/json.hpp
# → debe mostrar ~1.1 MB
```

---

## 5 — Configurar el entorno de devkitPro

Antes de compilar, exporta las variables de entorno requeridas.  
En macOS/Linux (agrégalas a `~/.zshrc` o `~/.bashrc` para hacerlo permanente):

```bash
export DEVKITPRO=/opt/devkitpro
export DEVKITARM=${DEVKITPRO}/devkitARM
export DEVKITA64=${DEVKITPRO}/devkitA64
export PATH=${DEVKITPRO}/tools/bin:${DEVKITA64}/bin:${PATH}
```

Aplica los cambios en la sesión actual:

```bash
source ~/.zshrc    # o ~/.bashrc según tu shell
```

Verifica que el compilador es accesible:

```bash
aarch64-none-elf-gcc --version
# → aarch64-none-elf-gcc (devkitA64 ...) ...
```

---

## 6 — Compilar

Desde la raíz del proyecto:

```bash
make
```

El proceso realiza los pasos siguientes automáticamente:

1. Compila `source/main.cpp` → `build/main.o`
2. Enlaza todos los objetos → `MP3Player.elf`
3. Genera el NACP (metadatos de la app) → `MP3Player.nacp`
4. Empaqueta el ELF + NACP + contenido de `romfs/` → **`MP3Player.nro`**

Salida esperada al terminar sin errores:

```
built ... MP3Player.nro
```

### Limpiar artefactos de compilación

```bash
make clean
```

Elimina `build/`, `MP3Player.elf`, `MP3Player.nro`, `MP3Player.nacp`.

---

## 7 — Probar en emulador (Ryujinx)

1. Abre Ryujinx.
2. Ve a **File → Open Ryujinx Folder** → carpeta `sdcard/`.
3. Crea la estructura de carpetas:
   ```
   sdcard/
   ├── switch/
   │   └── MP3Player.nro      ← copia el NRO aquí
   └── Music/
       └── *.mp3              ← tus archivos de música
   ```
4. En Ryujinx ve a **File → Load Application from File** y abre el NRO.

---

## 8 — Probar en hardware real

1. Inserta la microSD de la Switch en tu computadora.
2. Copia los archivos:
   ```bash
   cp MP3Player.nro /Volumes/microSD/switch/MP3Player/MP3Player.nro
   # Crea la carpeta de música si no existe:
   mkdir -p /Volumes/microSD/Music
   cp *.mp3 /Volumes/microSD/Music/
   ```
3. Expulsa la microSD, insértala en la Switch.
4. Abre el **Homebrew Menu** (Album o con la combinación de tu CFW) y ejecuta **MP3Player**.

### ⚠️ Notas importantes al probar en hardware

**Crashes y pantallas de error (negra con códigos hex)**  
Si el código tiene un error grave de memoria — puntero nulo, desbordamiento al leer un MP3 corrupto, etc. — Atmosphère mostrará una pantalla negra con el mensaje *"An error has occurred"* y códigos hexadecimales. Esto **no daña la consola**. Simplemente mantén presionado el botón de encendido para reiniciar el CFW y vuelve a intentarlo.

Para minimizar estos crashes:
- Verifica siempre que `Mix_LoadMUS()` no devuelve `nullptr` antes de llamar `Mix_PlayMusic()`.
- Evita archivos MP3 corruptos o con tags ID3 malformados en `sdmc:/Music`.
- Si un tema tiene assets PNG faltantes, la app ignora la textura y usa el color de fallback — no crashea.

**Cerrar correctamente con el botón +**  
La secuencia de limpieza al salir es crítica en audio. Si una app de Switch sale sin llamar `Mix_HaltMusic()` + `Mix_CloseAudio()` + `SDL_Quit()`, el servicio de audio de Horizon OS puede quedar bloqueado: **la siguiente app que intente reproducir sonido quedará muda hasta que reinicies la consola**. El botón **+** en este reproductor ejecuta esa secuencia completa y ordenada antes de devolver el control al Homebrew Menu.

---

## 9 — Theme Editor (opcional)

Herramienta web para crear temas visuales con preview en tiempo real.

```bash
cd tools/theme_editor
pip install -r requirements.txt    # instala Flask
python app.py
```

Abre <http://localhost:5000> en tu navegador.

- Diseña el tema en el panel izquierdo.
- El preview derecho refleja exactamente cómo se verá en la consola (1280×720).
- Pulsa **Save** → genera `romfs/themes/<nombre>/theme.json`.
- Vuelve a ejecutar `make` para empaquetar el tema en el NRO.

En la consola, pulsa **Y** en el reproductor para abrir el selector de temas.

---

## Controles en la consola

| Botón | Acción |
|---|---|
| `↑ / ↓` | Navegar la lista |
| `A` | Reproducir pista seleccionada |
| `B` | Pausar / reanudar |
| `L` | Pista anterior |
| `R` | Pista siguiente |
| `Y` | Abrir selector de temas |
| `+` | Salir al Homebrew Menu |

---

## Solución de problemas comunes

| Error | Causa probable | Solución |
|---|---|---|
| `DEVKITPRO not set` | Variable de entorno no exportada | Ejecuta `export DEVKITPRO=/opt/devkitpro` |
| `cannot find -lSDL2_mixer` | Paquetes no instalados | `sudo dkp-pacman -S switch-sdl2_mixer` |
| `json.hpp: No such file` | Header de nlohmann faltante | Ejecuta el comando del paso 4 |
| NRO no aparece en Homebrew Menu | Ruta incorrecta en la SD | Debe estar en `switch/<nombre>/<nombre>.nro` |
| Sin audio en hardware | Volumen del sistema en 0 | Sube el volumen desde la configuración del sistema |
