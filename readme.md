
# LAN-Caster

### Tu propio servicio de streaming local, sin internet, sin aplicaciones pesadas, directo al navegador de tu TV.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.x-blue?logo=python&logoColor=white" alt="Python 3.x">
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License MIT">
  <img src="https://img.shields.io/badge/dependencies-FFmpeg-orange" alt="FFmpeg">
</p>

---

## Que es LAN-Caster?

**LAN-Caster** es una herramienta CLI ultra-ligera para transmitir archivos de video desde tu ordenador hacia cualquier Smart TV, telefono o tablet en la misma red local, usando solo el navegador web.

Automatiza la creacion de un reproductor HTML5, convirtiendo subtitulos `.srt` a `.vtt` (formato web) de forma transparente.

### Por que existe esto?

Para reproducir contenido en Smart TVs con sistemas limitados (WebOS, Tizen, VIDAA) donde no hay acceso a VLC o Plex, y el unico punto de entrada es el navegador web integrado.

### Caracteristicas

- **Direct Stream** - Sin transcodificacion, carga instantanea
- **Servidor multihilo** - Maneja video y subtitulos simultaneamente
- **Conversion automatica** de subtitulos SRT a VTT
- **Modo GUI** - Selector de archivos grafico (--gui)
- **Subtitulos optimizados** para TV (tamanio proporcional a pantalla)
- **Atajos de teclado** (Espacio, F, Flechas, M)
- **Limpieza automatica** de archivos temporales
- **Zero config** - Solo apunta al video y listo

---

## Requisitos del Sistema

| Requisito | Descripcion |
|-----------|-------------|
| **Python 3.10+** | Usa sintaxis moderna (type hints) |
| **FFmpeg** | Solo si usas subtitulos `.srt` |
| **tkinter** | Solo para modo `--gui` (viene con Python en la mayoria de sistemas) |
| **Red Local** | Wi-Fi o Ethernet (no requiere Internet) |

### Instalacion de dependencias

```bash
# Debian/Ubuntu/Mint
sudo apt install ffmpeg python3-tk

# Fedora
sudo dnf install ffmpeg python3-tkinter

# macOS (Homebrew)
brew install ffmpeg python-tk

# Windows
# FFmpeg: choco install ffmpeg
# tkinter viene incluido con Python
```

---

## Instalacion

### Opcion 1: Descarga directa

```bash
curl -O https://raw.githubusercontent.com/FxxMorgan/LAN-Caster/main/lancaster.py
chmod +x lancaster.py
```

### Opcion 2: Clonar repositorio

```bash
git clone https://github.com/FxxMorgan/LAN-Caster.git
cd LAN-Caster
```

---

## Uso

### Basico (linea de comandos)

```bash
python3 lancaster.py "MiPelicula.mp4"
```

### Modo GUI (selector de archivos)

```bash
python3 lancaster.py --gui
```

Se abrira un dialogo para seleccionar el video graficamente. Util cuando el nombre del archivo es muy largo.

### Con puerto personalizado

```bash
python3 lancaster.py "MiPelicula.mp4" -p 9000
python3 lancaster.py --gui -p 9000
```

### Ignorar subtitulos

```bash
python3 lancaster.py "MiPelicula.mp4" --no-subs
```

### Ejemplo de salida

```
[GUI]  Abriendo selector de archivos...
[INFO] Video detectado: MiPelicula.mp4
[INFO] Subtitulo detectado: MiPelicula.srt
[PROC] Convirtiendo SRT a VTT...
[OK]   Conversion completada
[HTML] Generando reproductor web...
[OK]   Reproductor generado

==================================================
  LAN-Caster esta listo!
==================================================

  Red Local:  http://192.168.1.15:8000

  Presiona Ctrl+C para detener
==================================================
```

---

## Opciones de linea de comandos

| Opcion | Descripcion |
|--------|-------------|
| `video` | Ruta al archivo de video (opcional con --gui) |
| `-p, --port` | Puerto del servidor (default: 8000) |
| `--gui` | Abrir selector de archivos grafico |
| `--no-subs` | Ignorar subtitulos aunque existan |

---

## Atajos de Teclado (en el reproductor)

| Tecla | Accion |
|-------|--------|
| `Espacio` | Play / Pause |
| `F` | Pantalla completa |
| `<-` | Retroceder 10s |
| `->` | Adelantar 10s |
| `M` | Silenciar/Activar audio |

---

## Formatos Soportados

### Video (dependiente del navegador cliente)

| Formato | Chrome | Firefox | Safari | Smart TV |
|---------|--------|---------|--------|----------|
| `.mp4` (H.264) | OK | OK | OK | OK |
| `.mp4` (H.265) | Parcial | No | OK | Parcial |
| `.webm` (VP8/VP9) | OK | OK | No | Parcial |
| `.mkv` | Parcial | Parcial | No | Parcial |

**Recomendacion:** Usa `.mp4` con codec H.264 para maxima compatibilidad.

### Subtitulos

| Formato | Soporte |
|---------|---------|
| `.vtt` (WebVTT) | Nativo HTML5 |
| `.srt` (SubRip) | Convertido automaticamente |

---

## Estructura del Proyecto

```
LAN-Caster/
├── lancaster.py    # Script principal
├── readme.md       # Documentacion
└── LICENSE         # Licencia MIT
```

---

## Troubleshooting

### El video no carga en mi TV

1. Verifica que el formato sea `.mp4` H.264
2. H.265/HEVC no funciona en la mayoria de navegadores
3. Intenta con un archivo de prueba mas pequenio

### Los subtitulos no aparecen

1. El archivo `.srt` debe tener el mismo nombre que el video
2. Verifica que FFmpeg este instalado: `ffmpeg -version`
3. El encoding del `.srt` debe ser UTF-8

### Puerto en uso

```bash
python3 lancaster.py video.mp4 -p 9000
```

### Error "tkinter no disponible"

```bash
# Linux
sudo apt install python3-tk
```

### No encuentro la IP correcta

```bash
# Linux
ip addr | grep inet

# macOS  
ifconfig | grep "inet "

# Windows
ipconfig
```

---

## Roadmap

- [ ] Soporte para playlist (multiples archivos)
- [ ] Bandera `--hard-sub` para quemar subtitulos
- [ ] Codigo QR en terminal para acceso rapido
- [ ] Deteccion automatica de dispositivos en red (mDNS)

---

## Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## Licencia

Este proyecto esta bajo la Licencia **MIT**. Sientete libre de usarlo, modificarlo y compartirlo.

---

<p align="center">
  <i>"A veces la mejor solucion no es la mas compleja, sino la que funciona con lo que tienes a mano."</i>
</p>
