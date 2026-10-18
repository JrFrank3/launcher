import os
import sys
import re
import time
import ctypes
import threading
import subprocess
import zipfile
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import customtkinter as ctk
import gdown

ctk.set_appearance_mode("dark")

# ================= PALETAS DE COLORES =================
TEMAS = {
        "Violeta": {
        "tab_activa": "#DDD6FE",
        "btn_primario": "#7C3AED",
        "btn_hover": "#6D28D9",
        "borde_hover": "#A78BFA",
        "consola_txt": "#DDD6FE"
    },
    "Esmeralda": {
        "tab_activa": "#6EE7B7",
        "btn_primario": "#10B981",
        "btn_hover": "#059669",
        "borde_hover": "#34D399",
        "consola_txt": "#6EE7B7"
    },
    "Oro Ámbar": {
        "tab_activa": "#FDE68A",
        "btn_primario": "#D97706",
        "btn_hover": "#B45309",
        "borde_hover": "#FBBF24",
        "consola_txt": "#FDE68A"
    }
}

BG_DARK = "#060609"
BG_HEADER = "#0E0F14"
BG_CARD = "#13151E"
BG_CARD_HOVER = "#191C28"
BORDER_NORMAL = "#272A3A"

TAB_INACTIVA = "#27272A"
TAB_INACTIVA_HOVER = "#3F3F46"
TXT_TAB_ACTIVA = "#09090B"

TXT_BLANCO = "#FFFFFF"
TXT_PLATA = "#E2E8F0"
TXT_GRIS = "#94A3B8"

CARPETA_ICONOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iconos")
os.makedirs(CARPETA_ICONOS, exist_ok=True)


# ================= CAPTURADOR DE CONSOLA PARA BITÁCORA EN VIVO =================
class CapturadorConsola:
    def __init__(self, app, nombre_programa, barra=None, lbl_estado=None):
        self.app = app
        self.nombre = nombre_programa
        self.barra = barra
        self.lbl_estado = lbl_estado
        self.ultimo_porcentaje = -1

    def write(self, texto):
        if not texto:
            return
        texto_limpio = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', texto)

        for linea in texto_limpio.replace('\r', '\n').splitlines():
            linea_str = linea.strip()
            if not linea_str:
                continue

            match_pct = re.search(r'(\d+)%\|', linea_str)
            if match_pct:
                pct = int(match_pct.group(1))
                if pct != self.ultimo_porcentaje and (pct % 5 == 0 or pct == 100):
                    self.ultimo_porcentaje = pct
                    self.app.after(0, self.app.registrar_log, self.nombre, linea_str)
                    if self.barra:
                        self.app.after(0, lambda p=pct / 100.0: (self.barra.configure(mode="determinate"), self.barra.set(p)))
                    if self.lbl_estado:
                        self.app.after(0, lambda p=pct: self.lbl_estado.configure(text=f"Descargando... {p}%"))
            else:
                self.app.after(0, self.app.registrar_log, self.nombre, linea_str)

    def flush(self):
        pass


# ================= GENERADOR GRÁFICO DE ICONOS HD =================
def obtener_fuente(tamano):
    for fuente in ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"]:
        try:
            return ImageFont.truetype(fuente, tamano)
        except Exception:
            continue
    return ImageFont.load_default()


def generar_icono_programa(id_icono, estilo, sigla, color_hex):
    ruta_png = os.path.join(CARPETA_ICONOS, f"{id_icono}.png")
    if os.path.exists(ruta_png):
        img = Image.open(ruta_png).convert("RGBA")
        return ctk.CTkImage(light_image=img, dark_image=img, size=(54, 54))

    size = 128
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if estilo == "adobe":
        draw.rounded_rectangle([4, 4, 124, 124], radius=28, fill=color_hex)
        draw.rounded_rectangle([12, 12, 116, 116], radius=22, fill="#140A1E")
        fnt = obtener_fuente(54)
        bbox = draw.textbbox((0, 0), sigla, font=fnt)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size - w) / 2, (size - h) / 2 - 6), sigla, font=fnt, fill=color_hex)

    elif estilo == "chrome":
        draw.rounded_rectangle([4, 4, 124, 124], radius=28, fill="#1E202B")
        draw.pieslice([20, 20, 108, 108], start=210, end=330, fill="#EA4335")
        draw.pieslice([20, 20, 108, 108], start=330, end=90, fill="#FBBC05")
        draw.pieslice([20, 20, 108, 108], start=90, end=210, fill="#34A853")
        draw.ellipse([42, 42, 86, 86], fill="#FFFFFF")
        draw.ellipse([48, 48, 80, 80], fill="#4285F4")

    elif estilo == "brave":
        draw.rounded_rectangle([4, 4, 124, 124], radius=28, fill="#23120B")
        puntos = [(64, 16), (106, 32), (96, 84), (64, 112), (32, 84), (22, 32)]
        draw.polygon(puntos, fill="#FB542B", outline="#FF8A65")
        fnt = obtener_fuente(42)
        bbox = draw.textbbox((0, 0), "B", font=fnt)
        draw.text(((size - (bbox[2] - bbox[0])) / 2, 38), "B", font=fnt, fill="#FFFFFF")

    elif estilo == "winrar":
        draw.rounded_rectangle([4, 4, 124, 124], radius=28, fill="#1A1228")
        draw.rounded_rectangle([22, 24, 106, 48], radius=6, fill="#A855F7")
        draw.rounded_rectangle([22, 52, 106, 76], radius=6, fill="#3B82F6")
        draw.rounded_rectangle([22, 80, 106, 104], radius=6, fill="#10B981")
        draw.rectangle([54, 18, 74, 110], fill="#78350F")
        draw.rectangle([56, 56, 72, 72], fill="#FBBF24")

    elif estilo == "7zip":
        draw.rounded_rectangle([4, 4, 124, 124], radius=28, fill="#18181B", outline="#10B981", width=4)
        draw.rounded_rectangle([18, 30, 72, 98], radius=10, fill="#10B981")
        fnt7 = obtener_fuente(48)
        draw.text((32, 36), "7", font=fnt7, fill="#09090B")
        fntz = obtener_fuente(36)
        draw.text((78, 46), "ZIP", font=fntz, fill="#FFFFFF")

    elif estilo == "pdf":
        draw.rounded_rectangle([4, 4, 124, 124], radius=28, fill="#280D0D")
        draw.rounded_rectangle([28, 16, 100, 112], radius=8, fill="#EF4444")
        draw.polygon([(76, 16), (100, 40), (76, 40)], fill="#FCA5A5")
        fnt = obtener_fuente(28)
        draw.text((36, 58), "PDF", font=fnt, fill="#FFFFFF")

    elif estilo == "office":
        draw.rounded_rectangle([4, 4, 124, 124], radius=28, fill="#1F1209")
        draw.rounded_rectangle([44, 18, 108, 110], radius=12, fill=color_hex)
        draw.rounded_rectangle([18, 34, 72, 94], radius=10, fill="#FFFFFF")
        fnt = obtener_fuente(30)
        bbox = draw.textbbox((0, 0), sigla, font=fnt)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((45 - w / 2, 62 - h / 2 - 4), sigla, font=fnt, fill=color_hex)

    elif estilo == "autodesk":
        draw.rounded_rectangle([4, 4, 124, 124], radius=28, fill="#111827")
        draw.polygon([(16, 112), (52, 16), (112, 16), (76, 112)], fill=color_hex)
        draw.rounded_rectangle([16, 40, 112, 92], radius=10, fill="#090D16", outline=color_hex, width=3)
        fnt = obtener_fuente(34)
        bbox = draw.textbbox((0, 0), sigla, font=fnt)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size - w) / 2, (size - h) / 2 - 4), sigla, font=fnt, fill="#FFFFFF")

    elif estilo == "3d":
        draw.rounded_rectangle([4, 4, 124, 124], radius=28, fill="#14141F", outline=color_hex, width=4)
        draw.ellipse([20, 20, 108, 108], fill=color_hex)
        draw.ellipse([30, 30, 98, 98], fill="#14141F")
        fnt = obtener_fuente(32)
        bbox = draw.textbbox((0, 0), sigla, font=fnt)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size - w) / 2, (size - h) / 2 - 4), sigla, font=fnt, fill=color_hex)

    else:
        draw.rounded_rectangle([4, 4, 124, 124], radius=28, fill=color_hex)
        draw.rounded_rectangle([10, 10, 118, 118], radius=24, fill="#12131A")
        draw.ellipse([22, 22, 106, 106], fill=color_hex)
        fnt = obtener_fuente(36)
        bbox = draw.textbbox((0, 0), sigla, font=fnt)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size - w) / 2, (size - h) / 2 - 4), sigla, font=fnt, fill="#FFFFFF")
    
    img.save(ruta_png, "PNG")
    return ctk.CTkImage(light_image=img, dark_image=img, size=(54, 54))


# ================= CATÁLOGO DE PROGRAMAS =================
# NOTA: En los programas "gdrive", puedes añadir opcionalmente:
#   "ejecutable": "Set-up.exe" (si sabes el nombre exacto, si no lo pones, el programa lo busca solo)
#   "parametros": "--silent"   (si quieres que corra con algún parámetro especial; si lo dejas vacío "", abre el instalador normal)
CATALOGO = {
    "Todos": [],
    "Básicos": [
        {
            "id": "winrar", "estilo": "winrar", "sigla": "RAR", "color": "#A855F7",
            "nombre": "WinRAR (64 bits)",
            "desc": "Compresor y descompresor esencial para archivos .RAR y .ZIP.",
            "tipo": "url_directa",
            "url": "https://www.rarlab.com/rar/winrar-x64-701es.exe",
            "archivo": "WinRAR_Setup.exe",
            "parametros": "/S"
        },
        {
            "id": "7zip", "estilo": "7zip", "sigla": "7z", "color": "#10B981",
            "nombre": "7-Zip (64 bits)",
            "desc": "Gestor de archivos comprimidos ultraligero (.7z, .zip, .rar, .iso).",
            "tipo": "url_directa",
            "url": "https://www.7-zip.org/a/7z2408-x64.exe",
            "archivo": "7Zip_Setup.exe",
            "parametros": "/S"
        },
        {
            "id": "nitropdf", "estilo": "pdf", "sigla": "PDF", "color": "#EF4444",
            "nombre": "Nitro PDF Pro",
            "desc": "Suite avanzada para editar, convertir, firmar y crear archivos PDF.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_NITRO/view?usp=sharing",
            "archivo_salida": "NitroPDF_Pro.zip",
            "parametros": ""
        }
    ],
    "Navegadores": [
        {
            "id": "chrome", "estilo": "chrome", "sigla": "Cr", "color": "#3B82F6",
            "nombre": "Google Chrome",
            "desc": "Navegador oficial de Google. Descarga directa e instalación automática.",
            "tipo": "url_directa",
            "url": "https://dl.google.com/chrome/install/standalonesetup64.exe",
            "archivo": "ChromeStandaloneSetup64.exe",
            "parametros": "/silent /install"
        },
        {
            "id": "brave", "estilo": "brave", "sigla": "Br", "color": "#FB542B",
            "nombre": "Brave Browser",
            "desc": "Navegador rápido con bloqueador nativo de anuncios y rastreadores.",
            "tipo": "url_directa",
            "url": "https://laptop-updates.brave.com/latest/winx64",
            "archivo": "BraveSetup.exe",
            "parametros": "/silent /install"
        },
        {
            "id": "firefox", "estilo": "firefox", "sigla": "Fx", "color": "#FF9900",
            "nombre": "Mozilla Firefox",
            "desc": "Navegador web rápido y seguro.",
            "tipo": "url_directa",
            "url": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=es-ES",
            "archivo": "Firefox Setup.exe",
            "parametros": "/S"
        },
        {
            "id": "edge", "estilo": "edge", "sigla": "Ed", "color": "#0078D4",
            "nombre": "Microsoft Edge",
            "desc": "Navegador web de Microsoft con rendimiento y seguridad.",
            "tipo": "url_directa",
            "url": "https://go.microsoft.com/fwlink/?linkid=2137983",
            "archivo": "MicrosoftEdgeSetup.exe",
            "parametros": "/silent /install"
        },
        {
            "id": "opera", "estilo": "opera", "sigla": "Op", "color": "#FF1B2D",
            "nombre": "Opera Browser",
            "desc": "Navegador web rápido y seguro con funciones integradas.",
            "tipo": "url_directa",
            "url": "https://get.geo.opera.com/ftp/pub/opera/latest/desktop/",
            "archivo": "OperaSetup.exe",
            "parametros": "/silent /install"
        }
    ],
    "Adobe": [
        {
            "id": "photoshop", "estilo": "adobe", "sigla": "Ps", "color": "#31A8FF",
            "nombre": "Adobe Photoshop 2026",
            "desc": "Descarga, extrae e inicia automáticamente el instalador de Photoshop.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/1_9PF43525plue8RYBOZG68AmAlK3D8Gt/view?usp=sharing",
            "archivo_salida": "Adobe_Photoshop_2026.iso",
            "parametros": ""
        },
        {
            "id": "illustrator", "estilo": "adobe", "sigla": "Ai", "color": "#FF9A00",
            "nombre": "Adobe Illustrator 2026",
            "desc": "Diseño vectorial de logotipos, iconos, tipografías e ilustraciones.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/12-AJEm13oXlKpmLHaM4gZMdGU4LOqZGP/view?usp=sharing",
            "archivo_salida": "Adobe_Illustrator_2026.zip",
            "parametros": ""
        },
        {
            "id": "premiere", "estilo": "adobe", "sigla": "Pr", "color": "#9999FF",
            "nombre": "Adobe Premiere Pro 2026",
            "desc": "Edición de video profesional para cine, televisión y creadores.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_PREMIERE/view?usp=sharing",
            "archivo_salida": "Adobe_Premiere_2026.zip",
            "parametros": ""
        },
        {
            "id": "aftereffects", "estilo": "adobe", "sigla": "Ae", "color": "#D291FF",
            "nombre": "Adobe After Effects 2026",
            "desc": "Creación de efectos visuales cinematográficos y Motion Graphics.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/1Cm2QJZqqqNZWLr93ve5lJffRIMWljt6p/view?usp=sharing",
            "archivo_salida": "Adobe_AfterEffects_2026.iso",
            "parametros": ""
        },
        {
            "id": "indesign", "estilo": "adobe", "sigla": "Id", "color": "#FF3366",
            "nombre": "Adobe InDesign 2026",
            "desc": "Diseño editorial y maquetación profesional para libros y revistas.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_INDESIGN/view?usp=sharing",
            "archivo_salida": "Adobe_InDesign_2026.zip",
            "parametros": ""
        },
        {
            "id": "lightroom", "estilo": "adobe", "sigla": "Lr", "color": "#31A8FF",
            "nombre": "Adobe Lightroom Classic",
            "desc": "Revelado digital avanzado y catalogación fotográfica en formato RAW.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_LIGHTROOM/view?usp=sharing",
            "archivo_salida": "Adobe_Lightroom_Classic.zip",
            "parametros": ""
        },
        {
            "id": "acrobat", "estilo": "pdf", "sigla": "Ac", "color": "#ED2224",
            "nombre": "Adobe Acrobat Pro DC",
            "desc": "Herramienta oficial de Adobe para edición y gestión total de PDFs.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_ACROBAT/view?usp=sharing",
            "archivo_salida": "Adobe_Acrobat_Pro.zip",
            "parametros": ""
        },
        {
            "id": "audition", "estilo": "adobe", "sigla": "Au", "color": "#00E4BB",
            "nombre": "Adobe Audition 2026",
            "desc": "Descarga, descomprime e inicia automáticamente el instalador de Audition.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/1j6SVa4DzrOQvT5Rl-3TJysIv4E-ZFawR/view?usp=sharing",
            "archivo_salida": "Adobe_Audition_2026.zip",
            "ejecutable": "Set-up.exe",
            "parametros": ""
        },
        {
            "id": "mediaencoder", "estilo": "adobe", "sigla": "Me", "color": "#A855F7",
            "nombre": "Adobe Media Encoder 2026",
            "desc": "Renderizado y compresión rápida de video para Premiere y After Effects.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_ENCODER/view?usp=sharing",
            "archivo_salida": "Adobe_MediaEncoder_2026.zip",
            "parametros": ""
        },
        {
            "id": "animate", "estilo": "adobe", "sigla": "An", "color": "#FF6B00",
            "nombre": "Adobe Animate 2026",
            "desc": "Animación vectorial 2D interactiva para web, series y videojuegos.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_ANIMATE/view?usp=sharing",
            "archivo_salida": "Adobe_Animate_2026.zip",
            "parametros": ""
        }
    ],
    "Autodesk & 3D": [
        {
            "id": "autocad", "estilo": "autodesk", "sigla": "CAD", "color": "#E51050",
            "nombre": "Autodesk AutoCAD 2026",
            "desc": "Diseño CAD 2D y modelado 3D de precisión para arquitectura e ingeniería.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_AUTOCAD/view?usp=sharing",
            "archivo_salida": "Autodesk_AutoCAD_2026.iso",
            "parametros": ""
        },
        {
            "id": "revit", "estilo": "autodesk", "sigla": "RVT", "color": "#2B579A",
            "nombre": "Autodesk Revit 2026",
            "desc": "Modelado de información de construcción (BIM) para arquitectura e ingeniería.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_REVIT/view?usp=sharing",
            "archivo_salida": "Autodesk_Revit_2026.iso",
            "parametros": ""
        },
        {
            "id": "civil3d", "estilo": "autodesk", "sigla": "C3D", "color": "#0078D4",
            "nombre": "AutoCAD Civil 3D 2026",
            "desc": "Diseño y documentación para ingeniería civil, topografía y obras viales.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_CIVIL3D/view?usp=sharing",
            "archivo_salida": "Autodesk_Civil3D_2026.iso",
            "parametros": ""
        },
        {
            "id": "3dsmax", "estilo": "autodesk", "sigla": "MAX", "color": "#00849B",
            "nombre": "Autodesk 3ds Max 2026",
            "desc": "Modelado 3D, animación, simulación y renderizado fotorrealista.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_3DSMAX/view?usp=sharing",
            "archivo_salida": "Autodesk_3dsMax_2026.iso",
            "parametros": ""
        },
        {
            "id": "maya", "estilo": "autodesk", "sigla": "MYA", "color": "#10989B",
            "nombre": "Autodesk Maya 2026",
            "desc": "Animación 3D profesional, modelado, simulación y efectos visuales para cine.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_MAYA/view?usp=sharing",
            "archivo_salida": "Autodesk_Maya_2026.iso",
            "parametros": ""
        },
        {
            "id": "inventor", "estilo": "autodesk", "sigla": "INV", "color": "#D97706",
            "nombre": "Autodesk Inventor Pro 2026",
            "desc": "Diseño mecánico 3D, simulación de productos y creación de herramientas.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_INVENTOR/view?usp=sharing",
            "archivo_salida": "Autodesk_Inventor_2026.iso",
            "parametros": ""
        },
        {
            "id": "cinema4d", "estilo": "3d", "sigla": "C4D", "color": "#3B82F6",
            "nombre": "Maxon Cinema 4D 2026",
            "desc": "Modelado 3D, animación, simulación y Motion Graphics de alto rendimiento.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_CINEMA4D/view?usp=sharing",
            "archivo_salida": "Cinema4D_2026.zip",
            "parametros": ""
        },
        {
            "id": "blender", "estilo": "3d", "sigla": "BL", "color": "#F5792A",
            "nombre": "Blender 3D (64 bits)",
            "desc": "Suite libre de creación 3D: modelado, rigging, animación, escultura y render.",
            "tipo": "url_directa",
            "url": "https://mirror.clarkson.edu/blender/release/Blender4.2/blender-4.2.3-windows-x64.msi",
            "archivo": "Blender_Setup.msi",
            "parametros": "/quiet /norestart"
        }
    ],
    "Office": [
        {
            "id": "office2024", "estilo": "office", "sigla": "24", "color": "#EA580C",
            "nombre": "Microsoft Office 2024 LTSC",
            "desc": "Última versión corporativa 2024: Word, Excel, PowerPoint, Outlook y Access.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_OFFICE2024/view?usp=sharing",
            "archivo_salida": "Office_2024_LTSC.zip",
            "parametros": ""
        },
        {
            "id": "office2022", "estilo": "office", "sigla": "22", "color": "#E11D48",
            "nombre": "Microsoft Office 2022 ProPlus",
            "desc": "Suite ofimática completa edición 2022 lista para entornos profesionales.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_OFFICE2022/view?usp=sharing",
            "archivo_salida": "Office_2022_ProPlus.zip",
            "parametros": ""
        },
        {
            "id": "office2021", "estilo": "office", "sigla": "21", "color": "#D97706",
            "nombre": "Microsoft Office 2021 LTSC",
            "desc": "Versión corporativa estable de largo soporte (Word, Excel, PowerPoint).",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_OFFICE2021/view?usp=sharing",
            "archivo_salida": "Office_2021_LTSC.zip",
            "parametros": ""
        },
        {
            "id": "office2019", "estilo": "office", "sigla": "19", "color": "#B45309",
            "nombre": "Microsoft Office 2019 ProPlus",
            "desc": "Versión clásica de alto rendimiento compatible con equipos modernos y anteriores.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_OFFICE2019/view?usp=sharing",
            "archivo_salida": "Office_2019_ProPlus.zip",
            "parametros": ""
        },
        {
            "id": "office365", "estilo": "office", "sigla": "365", "color": "#EA580C",
            "nombre": "Microsoft Office 365 ProPlus",
            "desc": "Suite conectada: Word, Excel, PowerPoint, Outlook, Access y OneNote.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_OFFICE365/view?usp=sharing",
            "archivo_salida": "Office_365_ProPlus.zip",
            "parametros": ""
        },
        {
            "id": "word_excel", "estilo": "office", "sigla": "W", "color": "#2563EB",
            "nombre": "Office Esencial (Word, Excel, PPT)",
            "desc": "Instalación ligera únicamente con los tres programas principales.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_OFFICE_BASICO/view?usp=sharing",
            "archivo_salida": "Office_Esencial.zip",
            "parametros": ""
        },
        {
            "id": "project", "estilo": "office", "sigla": "Pj", "color": "#16A34A",
            "nombre": "Microsoft Project Pro 2024",
            "desc": "Administración profesional de proyectos, recursos, presupuestos y Gantt.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_PROJECT/view?usp=sharing",
            "archivo_salida": "Project_Pro_2024.zip",
            "parametros": ""
        },
        {
            "id": "visio", "estilo": "office", "sigla": "Vs", "color": "#7C3AED",
            "nombre": "Microsoft Visio Pro 2024",
            "desc": "Creación de diagramas de flujo, planos de red y mapas de ingeniería.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_VISIO/view?usp=sharing",
            "archivo_salida": "Visio_Pro_2024.zip",
            "parametros": ""
        },
        {
            "id": "officescrub", "estilo": "util", "sigla": "DEL", "color": "#EF4444",
            "nombre": "Limpiar / Desinstalar Office",
            "desc": "Remueve por completo versiones antiguas o conflictos de licencias previas.",
            "tipo": "gdrive",
            "valor": "https://drive.google.com/file/d/PEGA_AQUI_TU_LINK_DE_DESINSTALADOR/view?usp=sharing",
            "archivo_salida": "Office_Uninstaller.zip",
            "parametros": ""
        }
    ],
    "Utilidades": [
        {
            "id": "vlc", "estilo": "util", "sigla": "VLC", "color": "#F97316",
            "nombre": "VLC Media Player",
            "desc": "Reproductor multimedia universal para todos los formatos de video y audio.",
            "tipo": "url_directa",
            "url": "https://download.videolan.org/pub/videolan/vlc/3.0.21/win64/vlc-3.0.21-win64.exe",
            "archivo": "VLC_Setup.exe",
            "parametros": "/S"
        },
        {
            "id": "anydesk", "estilo": "util", "sigla": "AD", "color": "#EF4444",
            "nombre": "AnyDesk",
            "desc": "Software ultrarrápido de asistencia remota para soporte técnico.",
            "tipo": "url_directa",
            "url": "https://download.anydesk.com/AnyDesk.exe",
            "archivo": "AnyDesk.exe",
            "parametros": "--install \"C:\\Program Files (x86)\\AnyDesk\" --start-with-win --silent"
        },
        {
            "id": "teamviewer", "estilo": "util", "sigla": "TV", "color": "#14B8A6",
            "nombre": "TeamViewer",
            "desc": "Acceso y soporte remoto seguro para equipos de escritorio.",
            "tipo": "url_directa",
            "url": "https://download.teamviewer.com/download/TeamViewer_Setup_x64.exe",
            "archivo": "TeamViewer_Setup.exe",
            "parametros": "/S"
        }
    ],
    "Drivers & Sistema": [
        {
            "id": "vcredist", "estilo": "util", "sigla": "C++", "color": "#10B981",
            "nombre": "Visual C++ 2015-2022 (x64)",
            "desc": "Librerías de ejecución esenciales para programas de diseño y juegos.",
            "tipo": "url_directa",
            "url": "https://aka.ms/vs/17/release/vc_redist.x64.exe",
            "archivo": "vc_redist.x64.exe",
            "parametros": "/install /quiet /norestart"
        },
        {
            "id": "directx", "estilo": "util", "sigla": "DX", "color": "#8B5CF6",
            "nombre": "DirectX End-User Runtime",
            "desc": "Librerías gráficas indispensables para juegos y programas 3D.",
            "tipo": "url_directa",
            "url": "https://download.microsoft.com/download/1/7/1/1718CCC4-6315-4D8E-9543-8E28A4E18C4C/dxwebsetup.exe",
            "archivo": "dxwebsetup.exe",
            "parametros": "/Q"
        }
    ]
}

# ================= CLASE PRINCIPAL DE LA APLICACIÓN =================
class WorkstationLauncherPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.tema_actual = "Violeta"
        self.categoria_actual = "Todos"
        self.cache_iconos = {}
        self.seleccionados = {}
        self.vars_check = {}
        self.title("Auto Instalador Workstation Software Pro . JrFrank 2026")
        self.geometry("1920x1220")
        self.minsize(1100, 720)
        self.configure(fg_color=BG_DARK)
        self.cargar_todos_los_iconos()

        # ================= 1. CABECERA SUPERIOR =================
        self.header = ctk.CTkFrame(self, fg_color=BG_HEADER, corner_radius=0, height=78)
        self.header.pack(fill="x", side="top")

        brand_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        brand_frame.pack(side="left", padx=26, pady=12)

        ctk.CTkLabel(
            brand_frame,
            text="WORKSTATION SOFTWARE PRO - JRFRANK",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=TXT_BLANCO
        ).pack(anchor="w")

        self.lbl_sub = ctk.CTkLabel(
            brand_frame,
            text="EJECUCIÓN AUTOMÁTICA DE INSTALADORES",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEMAS[self.tema_actual]["tab_activa"]
        )
        self.lbl_sub.pack(anchor="w")

        right_controls = ctk.CTkFrame(self.header, fg_color="transparent")
        right_controls.pack(side="right", padx=26)

        self.entry_buscar = ctk.CTkEntry(
            right_controls,
            placeholder_text="Buscar programa (ej. Photoshop, Word, RAR)...",
            width=290,
            height=36,
            corner_radius=8,
            fg_color="#181924",
            border_color="#2E3244",
            text_color=TXT_BLANCO,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.entry_buscar.pack(side="left", padx=(0, 12))
        self.entry_buscar.bind("<KeyRelease>", self.filtrar_busqueda)

        self.btn_lote = ctk.CTkButton(
            right_controls,
            text="Instalar Seleccionados (0)",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=TEMAS[self.tema_actual]["btn_primario"],
            hover_color=TEMAS[self.tema_actual]["btn_hover"],
            text_color=TXT_BLANCO,
            command=self.instalar_seleccionados
        )
        self.btn_lote.pack(side="left", padx=(0, 12))

        self.selector_tema = ctk.CTkSegmentedButton(
            right_controls,
            values=list(TEMAS.keys()),
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=TAB_INACTIVA,
            selected_color=TEMAS[self.tema_actual]["btn_primario"],
            selected_hover_color=TEMAS[self.tema_actual]["btn_hover"],
            unselected_color=TAB_INACTIVA,
            unselected_hover_color=TAB_INACTIVA_HOVER,
            text_color=TXT_BLANCO,
            command=self.cambiar_tema
        )
        self.selector_tema.set(self.tema_actual)
        self.selector_tema.pack(side="left")

        # ================= 2. BARRA DE PESTAÑAS =================
        self.nav_bar = ctk.CTkFrame(self, fg_color=BG_HEADER, corner_radius=0)
        self.nav_bar.pack(fill="x", side="top")

        self.nav_inner = ctk.CTkFrame(self.nav_bar, fg_color="transparent")
        self.nav_inner.pack(side="left", padx=22, pady=(4, 14))

        self.botones_nav = {}
        for cat in CATALOGO.keys():
            if cat == "Todos":
                total = sum(len(v) for k, v in CATALOGO.items() if k != "Todos")
            else:
                total = len(CATALOGO[cat])
            btn = ctk.CTkButton(
                self.nav_inner,
                text=f"{cat}  ({total})",
                width=135,  # Reducido de 155 a 135 para acomodar la pestaña Autodesk & 3D
                height=38,
                corner_radius=15,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                fg_color=TAB_INACTIVA,
                hover_color=TAB_INACTIVA_HOVER,
                text_color=TXT_BLANCO,
                command=lambda c=cat: self.mostrar_categoria(c)
            )
            btn.pack(side="left", padx=5)
            self.botones_nav[cat] = btn

        btn_carpeta_iconos = ctk.CTkButton(
            self.nav_bar,
            text="Carpeta de Iconos",
            width=145,
            height=34,
            corner_radius=10,
            fg_color="#1E202E",
            hover_color="#2E3247",
            text_color=TXT_PLATA,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=lambda: os.startfile(CARPETA_ICONOS) if os.name == "nt" else None
        )
        btn_carpeta_iconos.pack(side="right", padx=26, pady=(4, 14))

        self.linea_divisoria = ctk.CTkFrame(self, fg_color=TEMAS[self.tema_actual]["btn_primario"], height=2)
        self.linea_divisoria.pack(fill="x", side="top")

        # ================= 3. ÁREA DE TARJETAS (3 COLUMNAS) =================
        self.scroll_area = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_DARK,
            scrollbar_button_color=TAB_INACTIVA,
            scrollbar_button_hover_color=TEMAS[self.tema_actual]["tab_activa"]
        )
        self.scroll_area.pack(fill="both", expand=True, padx=22, pady=12)

        for col in range(5):
            self.scroll_area.grid_columnconfigure(col, weight=1, uniform="col")

        # ================= 4. BITÁCORA INFERIOR EN VIVO =================
        self.log_panel = ctk.CTkFrame(
            self,
            fg_color=BG_HEADER,
            border_color=BORDER_NORMAL,
            border_width=1,
            height=165,
            corner_radius=12
        )
        self.log_panel.pack(fill="x", side="bottom", padx=26, pady=(2, 16))

        log_top = ctk.CTkFrame(self.log_panel, fg_color="transparent")
        log_top.pack(fill="x", padx=16, pady=(8, 2))

        ctk.CTkLabel(
            log_top,
            text="BITÁCORA DE CONSOLA, EXTRACCIÓN Y AUTO-INSTALACIÓN",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TXT_BLANCO
        ).pack(side="left")

        btn_limpiar_log = ctk.CTkButton(
            log_top,
            text="Limpiar consola",
            width=105,
            height=24,
            corner_radius=6,
            fg_color="#1E202E",
            hover_color="#2E3247",
            text_color=TXT_GRIS,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            command=self.limpiar_consola
        )
        btn_limpiar_log.pack(side="right")

        self.consola = ctk.CTkTextbox(
            self.log_panel,
            height=240,
            fg_color="#040407",
            text_color=TEMAS[self.tema_actual]["consola_txt"],
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=8
        )
        self.consola.pack(fill="both", expand=True, padx=12, pady=(2, 10))
        self.consola.configure(state="disabled")

        self.registrar_log("SISTEMA", "Selecciona un programa para descargarlo e iniciar su instalación automáticamente.")
        self.mostrar_categoria("Todos")

    def cargar_todos_los_iconos(self):
        for lista in CATALOGO.values():
            for item in lista:
                clave = item["id"]
                self.cache_iconos[clave] = generar_icono_programa(
                    clave, item["estilo"], item["sigla"], item["color"]
                )

    def limpiar_consola(self):
        self.consola.configure(state="normal")
        self.consola.delete("1.0", "end")
        self.consola.configure(state="disabled")
        self.registrar_log("SISTEMA", "Consola limpiada.")

    def registrar_log(self, origen, texto):
        hora = time.strftime("%H:%M:%S")
        linea = f"[{hora}]  {origen:<26} »  {texto}\n"
        self.consola.configure(state="normal")
        self.consola.insert("end", linea)
        self.consola.see("end")
        self.consola.configure(state="disabled")

    def cambiar_tema(self, nuevo_tema):
        self.tema_actual = nuevo_tema
        t = TEMAS[nuevo_tema]
        self.lbl_sub.configure(text_color=t["tab_activa"])
        self.linea_divisoria.configure(fg_color=t["btn_primario"])
        self.btn_lote.configure(fg_color=t["btn_primario"], hover_color=t["btn_hover"])
        self.selector_tema.configure(selected_color=t["btn_primario"], selected_hover_color=t["btn_hover"])
        self.consola.configure(text_color=t["consola_txt"])
        self.mostrar_categoria(self.categoria_actual)

    def actualizar_contador_lote(self, item, var):
        if var.get():
            self.seleccionados[item["id"]] = item
        else:
            self.seleccionados.pop(item["id"], None)
        self.btn_lote.configure(text=f"Instalar Seleccionados ({len(self.seleccionados)})")

    def filtrar_busqueda(self, _event=None):
        termino = self.entry_buscar.get().strip().lower()
        if not termino:
            self.mostrar_categoria(self.categoria_actual)
            return

        resultados = []
        for lista in CATALOGO.values():
            for item in lista:
                if termino in item["nombre"].lower() or termino in item["desc"].lower():
                    resultados.append(item)

        self.renderizar_tarjetas(f"Resultados para: '{self.entry_buscar.get()}'", resultados)

    def mostrar_categoria(self, categoria):
        self.categoria_actual = categoria
        t = TEMAS[self.tema_actual]

        # Colorear pestañas
        for cat, btn in self.botones_nav.items():
            if cat == categoria:
                btn.configure(fg_color=t["tab_activa"], text_color=TXT_TAB_ACTIVA, hover_color=t["tab_activa"])
            else:
                btn.configure(fg_color=TAB_INACTIVA, text_color=TXT_BLANCO, hover_color=TAB_INACTIVA_HOVER)

        # LÓGICA PARA LA PESTAÑA "TODOS"
        if categoria == "Todos":
            lista_total = []
            for cat_nombre, cat_lista in CATALOGO.items():
                if cat_nombre != "Todos":
                    lista_total.extend(cat_lista)
            self.renderizar_tarjetas("Todos los Programas Disponibles", lista_total)
        else:
            self.renderizar_tarjetas(categoria, CATALOGO.get(categoria, []))

    def renderizar_tarjetas(self, titulo_seccion, lista_programas):
        for widget in self.scroll_area.winfo_children():
            widget.destroy()

        header_sec = ctk.CTkFrame(self.scroll_area, fg_color="transparent")
        header_sec.grid(row=0, column=0, columnspan=5, sticky="ew", padx=8, pady=(4, 12))

        ctk.CTkLabel(
            header_sec,
            text=titulo_seccion,
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=TXT_BLANCO
        ).pack(side="left")

        ctk.CTkLabel(
            header_sec,
            text=f"   •   {len(lista_programas)} programas disponibles",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=TEMAS[self.tema_actual]["tab_activa"]
        ).pack(side="left", pady=(4, 0))

        for idx, item in enumerate(lista_programas):
            fila = (idx // 5) + 1
            col = idx % 5
            self.crear_tarjeta_programa(item, fila, col)
    def crear_tarjeta_programa(self, item, fila, col):
        t = TEMAS[self.tema_actual]

        card = ctk.CTkFrame(
            self.scroll_area,
            fg_color=BG_CARD,
            border_color=BORDER_NORMAL,
            border_width=1,
            corner_radius=14
        )
        card.grid(row=fila, column=col, padx=10, pady=10, sticky="nsew")

        def on_enter(_e, c=card):
            c.configure(border_color=TEMAS[self.tema_actual]["borde_hover"], fg_color=BG_CARD_HOVER)

        def on_leave(_e, c=card):
            c.configure(border_color=BORDER_NORMAL, fg_color=BG_CARD)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(16, 10))

        lbl_icono = ctk.CTkLabel(top, text="", image=self.cache_iconos[item["id"]])
        lbl_icono.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(
            top,
            text=item["nombre"],
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=TXT_BLANCO,
            anchor="w",
            justify="left",
            wraplength=220
        ).pack(side="left", fill="x", expand=True)

        var_chk = self.vars_check.get(item["id"])
        if var_chk is None:
            var_chk = ctk.BooleanVar(value=item["id"] in self.seleccionados)
            self.vars_check[item["id"]] = var_chk

        chk = ctk.CTkCheckBox(
            top,
            text="",
            variable=var_chk,
            width=24,
            height=24,
            corner_radius=5,
            fg_color=t["btn_primario"],
            hover_color=t["btn_hover"],
            border_color="#475569",
            command=lambda i=item, v=var_chk: self.actualizar_contador_lote(i, v)
        )
        chk.pack(side="right", padx=(4, 0))

        ctk.CTkLabel(
            card,
            text=item["desc"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TXT_PLATA,
            anchor="w",
            justify="left",
            wraplength=335
        ).pack(fill="x", padx=16, pady=(0, 14))

        barra = ctk.CTkProgressBar(
            card,
            height=6,
            corner_radius=3,
            fg_color="#232634",
            progress_color=t["tab_activa"]
        )
        barra.pack(fill="x", padx=16, pady=(0, 12))
        barra.set(0)

        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", side="bottom", padx=16, pady=(0, 16))

        if item["tipo"] == "gdrive":
            origen_txt = "Auto-Install (Drive)"
        elif item["tipo"] == "url_directa":
            origen_txt = "Auto-Install (Web)"
        else:
            origen_txt = "Comando Sistema"

        lbl_estado = ctk.CTkLabel(
            footer,
            text=origen_txt,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TXT_GRIS
        )
        lbl_estado.pack(side="left")

        btn_accion = ctk.CTkButton(
            footer,
            text="Instalar",
            width=115,
            height=34,
            corner_radius=5,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=t["btn_primario"],
            hover_color=t["btn_hover"],
            text_color=TXT_BLANCO
        )
        btn_accion.configure(
            command=lambda i=item, b=btn_accion, e=lbl_estado, p=barra: self.iniciar_instalacion_individual(i, b, e, p)
        )
        btn_accion.pack(side="right")

    def iniciar_instalacion_individual(self, item, boton, lbl_estado, barra):
        t = TEMAS[self.tema_actual]
        boton.configure(state="disabled", text="Instalando...", fg_color=TAB_INACTIVA)
        lbl_estado.configure(text="Conectando...", text_color=t["tab_activa"])
        barra.configure(mode="indeterminate")
        barra.start()

        threading.Thread(
            target=self.ejecutar_descarga_o_comando,
            args=(item, boton, lbl_estado, barra),
            daemon=True
        ).start()

    def instalar_seleccionados(self):
        if not self.seleccionados:
            self.registrar_log("AVISO", "Marca al menos una casilla en las tarjetas para instalar en lote.")
            return

        cola = list(self.seleccionados.values())
        self.btn_lote.configure(state="disabled", text=f"Instalando ({len(cola)})...")
        self.registrar_log("LOTE", f"Iniciando cola de instalación para {len(cola)} programas...")

        def correr_cola():
            for item in cola:
                self.ejecutar_descarga_o_comando(item)
            self.after(0, lambda: self.btn_lote.configure(
                state="normal",
                text=f"Instalar Seleccionados ({len(self.seleccionados)})"
            ))
            self.after(0, self.registrar_log, "LOTE", "¡Todos los programas seleccionados fueron procesados!")

        threading.Thread(target=correr_cola, daemon=True).start()

    # ================= BUSCADOR Y EJECUTOR AUTOMÁTICO DE INSTALADORES =================
    def ejecutar_archivo_instalador(self, ruta_ejecutable, parametros="", nombre_prog="Programa"):
        """
        Ejecuta un archivo .exe, .msi o .bat solicitando permisos de administrador si es necesario,
        y espera a que termine la instalación.
        """
        carpeta_trabajo = os.path.dirname(ruta_ejecutable)
        nombre_exe = os.path.basename(ruta_ejecutable)
        self.after(0, self.registrar_log, nombre_prog, f"Iniciando instalador: {nombre_exe}...")

        if ruta_ejecutable.lower().endswith(".msi"):
            args = f'/i "{ruta_ejecutable}" {parametros}'.strip()
            cmd = f'msiexec {args}'
            subprocess.run(cmd, cwd=carpeta_trabajo, shell=True, check=True)
        else:
            if parametros:
                cmd = f'"{ruta_ejecutable}" {parametros}'
                subprocess.run(cmd, cwd=carpeta_trabajo, shell=True, check=True)
            else:
                # Si no tiene parámetros silenciosos (como el autoplay.exe o Set-up.exe de Adobe),
                # lo lanza con elevación de Administrador (UAC) y espera a que el instalador abra/termine
                try:
                    proc = subprocess.Popen(
                        [ruta_ejecutable],
                        cwd=carpeta_trabajo,
                        shell=True
                    )
                    proc.wait()
                except OSError:
                    # Fallback con ShellExecute 'runas' si requiere elevación explícita UAC
                    ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", ruta_ejecutable, parametros, carpeta_trabajo, 1
                    )

        self.after(0, self.registrar_log, nombre_prog, f"Instalador ({nombre_exe}) ejecutado correctamente.")

    def buscar_y_ejecutar_en_carpeta(self, carpeta_raiz, item):
        """
        Busca automáticamente el instalador (.exe / .msi) dentro de la carpeta descomprimida
        priorizando nombres típicos como autoplay.exe, Set-up.exe, setup.exe, install.exe, etc.
        """
        nombre_prog = item["nombre"]
        parametros = item.get("parametros", "")
        exe_especifico = item.get("ejecutable", "").lower()

        candidatos = []
        for raiz, _dirs, archivos in os.walk(carpeta_raiz):
            for archivo in archivos:
                lower = archivo.lower()
                # Ignorar desinstaladores o archivos auxiliares de crash/reporte
                if any(palabra in lower for palabra in ["unins", "crash", "helper", "vc_redist", "dxsetup"]):
                    continue
                if lower.endswith((".exe", ".msi", ".bat", ".cmd")):
                    ruta_completa = os.path.join(raiz, archivo)
                    profundidad = raiz[len(carpeta_raiz):].count(os.sep)
                    candidatos.append((profundidad, lower, ruta_completa))

        if not candidatos:
            raise RuntimeError(f"No se encontró ningún archivo instalador (.exe/.msi) dentro de {carpeta_raiz}")

        # Orden de prioridad para encontrar el instalador principal automáticamente
        nombres_prioritarios = [
            exe_especifico,
            "autoplay.exe",     # Muy común en instaladores de Adobe / Repacks
            "set-up.exe",       # Instalador oficial de Adobe Creative Cloud
            "setup.exe",        # Instalador estándar de Office y Windows
            "install.exe",
            "instalador.exe",
            "autorun.exe",
            "start.exe"
        ]

        instalador_elegido = None

        # 1. Buscar coincidencia con los nombres prioritarios (en las carpetas más superficiales primero)
        candidatos.sort(key=lambda x: x[0])
        for nombre_prio in nombres_prioritarios:
            if not nombre_prio:
                continue
            for _prof, nombre_arch, ruta in candidatos:
                if nombre_arch == nombre_prio:
                    instalador_elegido = ruta
                    break
            if instalador_elegido:
                break

        # 2. Si no se llama setup.exe ni Set-up.exe, tomar el primer .exe principal de menor profundidad
        if not instalador_elegido:
            instalador_elegido = candidatos[0][2]

        self.ejecutar_archivo_instalador(instalador_elegido, parametros, nombre_prog)

    def procesar_archivo_descargado(self, ruta_archivo, item, lbl_estado=None):
        """
        Detecta automáticamente por la firma interna (magic bytes) si el archivo descargado
        es un .ZIP, .RAR, .7Z o un .EXE directo, lo extrae con la herramienta adecuada
        y ejecuta el instalador automáticamente.
        """
        nombre = item["nombre"]
        escritorio = os.path.join(os.path.expanduser("~"), "Desktop")

        # 1. Leer los primeros 8 bytes del archivo para saber su formato real
        with open(ruta_archivo, "rb") as f:
            cabecera = f.read(8)

        es_zip = cabecera.startswith(b"PK")
        es_rar = cabecera.startswith(b"Rar!")
        es_7z = cabecera.startswith(b"7z\xbc\xaf\x27\x1c")
        es_exe = cabecera.startswith(b"MZ")
        es_html = cabecera.lstrip().lower().startswith((b"<!doctype", b"<html"))
        es_iso = ruta_archivo.lower().endswith(".iso")

        # Si Google Drive devolvió una página web de bloqueo en vez del archivo
        if es_html:
            raise RuntimeError("Google Drive bloqueó la descarga o el archivo requiere permisos públicos.")
        
        # CASO A: Imagen ISO
        if es_iso:
            if lbl_estado:
                self.after(0, lambda: lbl_estado.configure(text="Montando ISO...", text_color="#FBBF24"))
            self.after(0, self.registrar_log, nombre, f"Montando imagen ISO virtualmente: {os.path.basename(ruta_archivo)}...")

            # Comando de PowerShell para montar la ISO de forma silenciosa y obtener su letra de unidad
            cmd_montar = f'powershell -Command "$mount = Mount-DiskImage -ImagePath \'{ruta_archivo}\' -PassThru; (Get-DiskImage -ImagePath \'{ruta_archivo}\' | Get-Volume).DriveLetter"'
            resultado = subprocess.run(cmd_montar, capture_output=True, text=True, shell=True)
            letra_unidad = resultado.stdout.strip()

            if not letra_unidad:
                raise RuntimeError("No se pudo montar la imagen ISO en Windows.")

            ruta_iso_montada = f"{letra_unidad}:\\"
            self.after(0, self.registrar_log, nombre, f"ISO montada en la unidad virtual: {ruta_iso_montada}")

            if lbl_estado:
                self.after(0, lambda: lbl_estado.configure(text="Instalando...", text_color="#38BDF8"))

            # Buscar y ejecutar el instalador dentro de la unidad virtual de la ISO
            try:
                self.buscar_y_ejecutar_en_carpeta(ruta_iso_montada, item)
            finally:
                # Desmontar la ISO de Windows al terminar la instalación
                cmd_desmontar = f'powershell -Command "Dismount-DiskImage -ImagePath \'{ruta_archivo}\'"'
                subprocess.run(cmd_desmontar, shell=True, capture_output=True)

            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
            return
        
        # CASO A: El archivo descargado ya es un ejecutable (.exe) directo aunque tenga otro nombre
        if es_exe and not (es_zip or es_rar or es_7z):
            ruta_exe = ruta_archivo
            if not ruta_exe.lower().endswith(".exe"):
                ruta_exe = os.path.splitext(ruta_archivo)[0] + ".exe"
                if os.path.exists(ruta_exe):
                    os.remove(ruta_exe)
                os.rename(ruta_archivo, ruta_exe)

            if lbl_estado:
                self.after(0, lambda: lbl_estado.configure(text="Instalando...", text_color="#38BDF8"))
            self.ejecutar_archivo_instalador(ruta_exe, item.get("parametros", ""), nombre)
            return

        # CASO B: Es un archivo comprimido (.ZIP, .RAR o .7Z)
        if es_zip or es_rar or es_7z:
            nombre_carpeta = os.path.splitext(os.path.basename(ruta_archivo))[0]
            carpeta_extraida = os.path.join(escritorio, nombre_carpeta)
            os.makedirs(carpeta_extraida, exist_ok=True)

            formato_real = "ZIP" if es_zip else ("RAR" if es_rar else "7Z")
            if lbl_estado:
                self.after(0, lambda: lbl_estado.configure(text=f"Extrayendo... {formato_real}...", text_color="#FBBF24"))
            self.after(0, self.registrar_log, nombre, f"Formato detectado: {formato_real}. Extrayendo en: {carpeta_extraida}...")

            # Si es .ZIP estándar, usar zipfile de Python
            if es_zip:
                with zipfile.ZipFile(ruta_archivo, "r") as zf:
                    zf.extractall(carpeta_extraida)
            else:
                # Si es .RAR o .7Z, buscar WinRAR, 7-Zip o usar el extractor nativo 'tar' de Windows 10/11
                rutas_extractores = [
                    r"C:\Program Files\WinRAR\WinRAR.exe",
                    r"C:\Program Files (x86)\WinRAR\WinRAR.exe",
                    r"C:\Program Files\7-Zip\7z.exe",
                    r"C:\Program Files (x86)\7-Zip\7z.exe"
                ]
                extractor_encontrado = next((p for p in rutas_extractores if os.path.exists(p)), None)

                if extractor_encontrado and "winrar" in extractor_encontrado.lower():
                    cmd_ext = f'"{extractor_encontrado}" x -y "{ruta_archivo}" "{carpeta_extraida}\\"'
                    subprocess.run(cmd_ext, shell=True, check=True)
                elif extractor_encontrado and "7z" in extractor_encontrado.lower():
                    cmd_ext = f'"{extractor_encontrado}" x "{ruta_archivo}" -o"{carpeta_extraida}" -y'
                    subprocess.run(cmd_ext, shell=True, check=True)
                else:
                    # Extractor nativo integrado en Windows 10/11 (soporta .rar, .7z y .zip)
                    cmd_ext = f'tar -xf "{ruta_archivo}" -C "{carpeta_extraida}"'
                    subprocess.run(cmd_ext, shell=True, check=True)

            # Borrar el archivo comprimido después de extraerlo para liberar espacio
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)

            if lbl_estado:
                self.after(0, lambda: lbl_estado.configure(text="Instalando...", text_color="#38BDF8"))

            # Buscar y ejecutar automáticamente el setup.exe / Set-up.exe / autoplay.exe
            self.buscar_y_ejecutar_en_carpeta(carpeta_extraida, item)
            return

        # CASO C: Si es un instalador .msi directo
        if ruta_archivo.lower().endswith(".msi"):
            if lbl_estado:
                self.after(0, lambda: lbl_estado.configure(text="Instalando...", text_color="#38BDF8"))
            self.ejecutar_archivo_instalador(ruta_archivo, item.get("parametros", ""), nombre)
            return

        raise RuntimeError(f"Formato desconocido (Cabecera: {cabecera}). Asegúrate de subir archivos .zip, .rar, .7z o .exe.")

    def ejecutar_descarga_o_comando(self, item, boton=None, lbl_estado=None, barra=None):
        nombre = item["nombre"]
        try:
            # ================= OPCIÓN 1: GOOGLE DRIVE =================
            if item["tipo"] == "gdrive":
                escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
                destino = os.path.join(escritorio, item["archivo_salida"])
                enlace = item["valor"]

                coincidencia = re.search(r"/d/([a-zA-Z0-9_-]+)", enlace)
                if coincidencia:
                    file_id = coincidencia.group(1)
                elif "id=" in enlace:
                    file_id = enlace.split("id=")[1].split("&")[0]
                else:
                    file_id = enlace.strip()

                url_limpia = f"https://drive.google.com/uc?id={file_id}"
                self.after(0, self.registrar_log, nombre, "Conectando con Drive...")

                capturador = CapturadorConsola(self, nombre, barra, lbl_estado)
                old_stdout, old_stderr = sys.stdout, sys.stderr
                sys.stdout, sys.stderr = capturador, capturador

                try:
                    archivo = gdown.download(url_limpia, destino, quiet=False)
                finally:
                    sys.stdout, sys.stderr = old_stdout, old_stderr

                if not archivo or not os.path.exists(destino):
                    raise RuntimeError("Verifica que el link de Drive sea público ('Cualquier persona con el enlace').")

                # Extraer e iniciar el instalador automáticamente
                self.procesar_archivo_descargado(destino, item, lbl_estado)

            # ================= OPCIÓN 2: URL DIRECTA / MEDIAFIRE =================
            elif item["tipo"] == "url_directa":
                carpeta_temp = os.environ.get("TEMP", os.path.expanduser("~"))
                ruta_archivo = os.path.join(carpeta_temp, item["archivo"])
                url = item["url"]

                self.after(0, self.registrar_log, nombre, f"From (original): {url}")
                self.after(0, self.registrar_log, nombre, f"To: {ruta_archivo}")

                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                )
                with urllib.request.urlopen(req) as respuesta, open(ruta_archivo, "wb") as archivo_local:
                    total_bytes = int(respuesta.info().get("Content-Length", 0))
                    descargado_bytes = 0
                    bloque = 65536
                    ultimo_pct = -1

                    while True:
                        buffer = respuesta.read(bloque)
                        if not buffer:
                            break
                        archivo_local.write(buffer)
                        descargado_bytes += len(buffer)

                        if total_bytes > 0:
                            pct = int((descargado_bytes * 100) / total_bytes)
                            if pct != ultimo_pct and (pct % 10 == 0 or pct == 100):
                                ultimo_pct = pct
                                llenos = int(pct / 4)
                                barra_txt = f"{pct}%|{'█' * llenos}{'░' * (25 - llenos)}| {descargado_bytes / (1024*1024):.1f}MB / {total_bytes / (1024*1024):.1f}MB"
                                self.after(0, self.registrar_log, nombre, barra_txt)
                                if barra:
                                    self.after(0, lambda p=pct / 100.0: (barra.configure(mode="determinate"), barra.set(p)))
                                if lbl_estado:
                                    self.after(0, lambda p=pct: lbl_estado.configure(text=f"Descargando... {p}%"))

                # Extraer (si es .zip) e iniciar el instalador automáticamente
                self.procesar_archivo_descargado(ruta_archivo, item, lbl_estado)

            # ================= OPCIÓN 3: COMANDO INTERNO =================
            elif item["tipo"] == "comando":
                self.after(0, self.registrar_log, nombre, f"Ejecutando: {item['valor']}")
                subprocess.run(item["valor"], shell=True, check=True)
                self.after(0, self.registrar_log, nombre, "¡Proceso completado!")

            if lbl_estado:
                self.after(0, lambda: lbl_estado.configure(text="Instalado...", text_color="#34D399"))

        except Exception as err:
            self.after(0, self.registrar_log, nombre, f"ERROR: {str(err)}")
            if lbl_estado:
                self.after(0, lambda: lbl_estado.configure(text="Error", text_color="#F87171"))

        finally:
            if boton and barra:
                def restaurar():
                    barra.stop()
                    barra.configure(mode="determinate")
                    barra.set(1)
                    boton.configure(
                        state="normal",
                        text="Instalar",
                        fg_color=TEMAS[self.tema_actual]["btn_primario"]
                    )
                self.after(0, restaurar)
# ================= VENTANA DE ACCESO / CONTRASEÑA =================
class VentanaLogin(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title("Acceso Protegido WSP . JrFrank 2026")
        self.geometry("420x260")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)
        
        # Centrar ventana en pantalla
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

        # Título y textos
        ctk.CTkLabel(
            self,
            text="ACCESO RESTRINGIDO",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=TXT_BLANCO
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            self,
            text="Ingresa la contraseña de seguridad para continuar:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TXT_PLATA
        ).pack(pady=(0, 15))

        # Campo de contraseña
        self.entry_pass = ctk.CTkEntry(
            self,
            placeholder_text="Contraseña...",
            show="*",
            width=280,
            height=38,
            corner_radius=8,
            fg_color="#181924",
            border_color="#2E3244",
            text_color=TXT_BLANCO,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.entry_pass.pack(pady=5)
        self.entry_pass.focus()
        self.entry_pass.bind("<Return>", lambda _e: self.verificar_password())

        # Botón de ingreso
        btn_ingresar = ctk.CTkButton(
            self,
            text="Desbloquear",
            width=280,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            text_color=TXT_BLANCO,
            command=self.verificar_password
        )
        btn_ingresar.pack(pady=12)

        # Etiqueta de error
        self.lbl_error = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#F87171"
        )
        self.lbl_error.pack()

    def verificar_password(self):
        # 🔑 AQUí CAMBIAS TU CONTRASEÑA
        CONTRASENA_CORRECTA = "JrFrank2026"
        
        if self.entry_pass.get() == CONTRASENA_CORRECTA:
            self.destroy()
            self.on_success()
        else:
            self.lbl_error.configure(text="Contraseña incorrecta. Acceso denegado.")
            self.entry_pass.delete(0, "end")
if __name__ == "__main__":
    def iniciar_sistema():
        app = WorkstationLauncherPro()
        app.mainloop()

    # Inicia primero la ventana de contraseña
    login = VentanaLogin(on_success=iniciar_sistema)
    login.mainloop()