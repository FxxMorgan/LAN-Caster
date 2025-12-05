#!/usr/bin/env python3
"""
LAN-Caster - Minimal Local Video Streamer
Tu propio servicio de streaming local, sin internet, directo al navegador de tu TV.
"""

import argparse
import http.server
import os
import shutil
import signal
import socket
import socketserver
import subprocess
import sys
from pathlib import Path

# Configuración
DEFAULT_PORT = 8000
SUPPORTED_VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mkv', '.avi', '.mov'}
SUPPORTED_SUB_EXTENSIONS = ['.srt', '.vtt']

# Archivos temporales generados
TEMP_FILES = []

# Colores ANSI para terminal
class Colors:
    INFO = '\033[94m'    # Azul
    OK = '\033[92m'      # Verde
    WARN = '\033[93m'    # Amarillo
    PROC = '\033[95m'    # Magenta
    RESET = '\033[0m'
    BOLD = '\033[1m'

def log(tag: str, message: str, color: str = Colors.INFO):
    """Imprime mensajes formateados en consola."""
    print(f"{color}[{tag}]{Colors.RESET} {message}")

def get_local_ip() -> str:
    """Obtiene la IP local del host en la red."""
    try:
        # Crear socket UDP para obtener IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # No envía datos, solo determina la interfaz
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def check_ffmpeg() -> bool:
    """Verifica si FFmpeg está instalado."""
    return shutil.which('ffmpeg') is not None

def find_subtitle(video_path: Path) -> Path | None:
    """Busca subtítulos con el mismo nombre que el video."""
    video_dir = video_path.parent
    video_stem = video_path.stem
    
    for ext in SUPPORTED_SUB_EXTENSIONS:
        sub_path = video_dir / f"{video_stem}{ext}"
        if sub_path.exists():
            return sub_path
    return None

def convert_srt_to_vtt(srt_path: Path, output_dir: Path) -> Path | None:
    """Convierte SRT a VTT usando FFmpeg."""
    vtt_path = output_dir / f"{srt_path.stem}.vtt"
    
    try:
        result = subprocess.run(
            ['ffmpeg', '-y', '-i', str(srt_path), str(vtt_path)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            TEMP_FILES.append(vtt_path)
            return vtt_path
        else:
            log("ERR", f"Error en FFmpeg: {result.stderr}", Colors.WARN)
            return None
    except Exception as e:
        log("ERR", f"Error ejecutando FFmpeg: {e}", Colors.WARN)
        return None

def generate_html(video_path: Path, subtitle_path: Path | None, output_dir: Path) -> Path:
    """Genera el archivo HTML del reproductor."""
    video_name = video_path.name
    subtitle_track = ""
    
    if subtitle_path:
        sub_name = subtitle_path.name
        subtitle_track = f'''
        <track src="{sub_name}" kind="subtitles" srclang="es" label="Español" default>'''
    
    html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎬 LAN-Caster</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ width: 100%; height: 100%; background: #000; overflow: hidden; }}
        video {{ width: 100%; height: 100%; }}
        
        /* ESTILOS DE SUBTÍTULOS PARA TV */
        video::cue {{
            background: rgba(0, 0, 0, 0.6); /* Fondo semi-transparente */
            color: #ffffff;
            /* Usamos vh (viewport height) para que sea proporcional al tamaño de la TV */
            font-size: 4.5vh; 
            font-family: Arial, Helvetica, sans-serif;
            text-shadow: 2px 2px 4px #000000; /* Sombra para mejor lectura */
            line-height: normal;
        }}
    </style>
</head>
<body>
    <video width="100%" height="100%" controls autoplay>
        <source src="{video_name}">{subtitle_track}
        Tu navegador no soporta video HTML5.
    </video>
    
    <script>
        const video = document.querySelector('video');
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'f' || e.key === 'F') {{
                document.fullscreenElement ? document.exitFullscreen() : video.requestFullscreen();
            }}
            if (e.key === ' ') {{
                e.preventDefault();
                video.paused ? video.play() : video.pause();
            }}
            if (e.key === 'ArrowRight') video.currentTime += 10;
            if (e.key === 'ArrowLeft') video.currentTime -= 10;
            if (e.key === 'm' || e.key === 'M') video.muted = !video.muted;
        }});
    </script>
</body>
</html>'''
    
    html_path = output_dir / "index.html"
    html_path.write_text(html_content, encoding='utf-8')
    TEMP_FILES.append(html_path)
    return html_path

def cleanup():
    """Elimina archivos temporales automáticamente."""
    if TEMP_FILES:
        log("CLEAN", "Eliminando archivos temporales...", Colors.PROC)
        for temp_file in TEMP_FILES:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    log("DEL", f"  → {temp_file.name}", Colors.OK)
            except Exception as e:
                log("ERR", f"No se pudo eliminar {temp_file}: {e}", Colors.WARN)

def signal_handler(sig, frame):
    """Manejador de señales para Ctrl+C."""
    print("\n")
    log("SRV", "Deteniendo servidor...", Colors.WARN)
    cleanup()
    log("BYE", "¡Hasta pronto! 👋", Colors.OK)
    sys.exit(0)

class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Handler HTTP silencioso (sin logs por cada request)."""
    def log_message(self, format, *args):
        # Solo loguear errores graves
        if args and '404' in str(args[0]):
            log("404", f"No encontrado: {args[0]}", Colors.WARN)

def run_server(directory: Path, port: int):
    """Ejecuta el servidor HTTP Multihilo."""
    os.chdir(directory)
    
    # IMPORTANTE: Usamos ThreadingTCPServer en lugar de TCPServer simple
    # Esto evita que la TV corte la conexión si pide video y subtítulos a la vez
    with socketserver.ThreadingTCPServer(("", port), QuietHTTPHandler) as httpd:
        httpd.allow_reuse_address = True
        local_ip = get_local_ip()
        
        print()
        print(f"{Colors.BOLD}{'='*50}{Colors.RESET}")
        print(f"{Colors.OK}  📺 LAN-Caster está listo!{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*50}{Colors.RESET}")
        print()
        print(f"  {Colors.INFO}Red Local:{Colors.RESET}  http://{local_ip}:{port}")
        print(f"  {Colors.WARN}Presiona Ctrl+C para detener{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*50}{Colors.RESET}")
        print()
        
        httpd.serve_forever()

def main():
    parser = argparse.ArgumentParser(
        description='🎬 LAN-Caster - Streaming local de video a tu TV',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('video', help='Ruta al archivo de video')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
                        help=f'Puerto del servidor (default: {DEFAULT_PORT})')
    parser.add_argument('--no-subs', action='store_true',
                        help='Ignorar subtítulos aunque existan')
    
    args = parser.parse_args()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    video_path = Path(args.video).resolve()
    
    if not video_path.exists():
        log("ERR", f"El archivo no existe: {video_path}", Colors.WARN)
        sys.exit(1)
    
    # Validación laxa de extensiones
    if video_path.suffix.lower() not in SUPPORTED_VIDEO_EXTENSIONS:
        log("WARN", f"Extensión '{video_path.suffix}' no estándar, pero intentando...", Colors.INFO)
    
    log("INFO", f"Video detectado: {video_path.name}", Colors.OK)
    
    work_dir = video_path.parent
    subtitle_path = None
    
    if not args.no_subs:
        found_sub = find_subtitle(video_path)
        if found_sub:
            log("INFO", f"Subtítulo detectado: {found_sub.name}", Colors.OK)
            if found_sub.suffix.lower() == '.srt':
                if not check_ffmpeg():
                    log("WARN", "Falta FFmpeg. Subtítulos no se convertirán.", Colors.WARN)
                else:
                    log("PROC", "Convirtiendo SRT a VTT...", Colors.PROC)
                    subtitle_path = convert_srt_to_vtt(found_sub, work_dir)
                    if subtitle_path: log("OK", "Conversión completada ✓", Colors.OK)
            elif found_sub.suffix.lower() == '.vtt':
                subtitle_path = found_sub
    
    log("HTML", "Generando reproductor web...", Colors.PROC)
    generate_html(video_path, subtitle_path, work_dir)
    log("OK", "Reproductor generado ✓", Colors.OK)
    
    try:
        run_server(work_dir, args.port)
    except OSError as e:
        if "Address already in use" in str(e):
            log("ERR", f"Puerto {args.port} ocupado. Usa otro con -p XXXX", Colors.WARN)
        else:
            log("ERR", f"Error servidor: {e}", Colors.WARN)
        cleanup()
        sys.exit(1)

if __name__ == '__main__':
    main()
