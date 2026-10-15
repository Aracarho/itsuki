import os
import json
import memoria

with open("apps.json", "r", encoding="utf-8") as f:
    APPS = json.load(f)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "abrir_aplicacion",
            "description": "Abre una aplicación, juego o archivo en la PC de Gus. Usar solo cuando Gus pida explícitamente que se abra algo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre de la app/juego/archivo, en minúsculas"}
                },
                "required": ["nombre"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "activar_modo",
            "description": "Activa un modo de actividad: trabajo, escuela o gaming. Usar cuando Gus diga explícitamente que va a entrar en ese modo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "modo": {"type": "string", "enum": ["trabajo", "escuela", "gaming"]}
                },
                "required": ["modo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "desactivar_modo",
            "description": "Desactiva el modo de actividad actual. Usar cuando Gus diga que terminó o que ya paró.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_compromiso",
            "description": "Registra algo verificable que Gus dijo que va a hacer o que ya hizo (tareas, entrenamiento, horarios, planes), para poder verificarlo después.",
            "parameters": {
                "type": "object",
                "properties": {
                    "texto": {"type": "string", "description": "El compromiso, resumido en pocas palabras"}
                },
                "required": ["texto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_compromisos_pendientes",
            "description": "Devuelve la lista real de compromisos pendientes de Gus. Usar SIEMPRE antes de acusarlo de contradicción, nunca inventar.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "resolver_compromiso",
            "description": "Marca un compromiso pendiente como cumplido o incumplido.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_compromiso": {"type": "integer"},
                    "estado": {"type": "string", "enum": ["cumplido", "incumplido"]}
                },
                "required": ["id_compromiso", "estado"]
            }
        }
    },
]


def abrir_aplicacion(nombre):
    clave = nombre.lower().strip()
    ruta = APPS.get(clave)
    if not ruta:
        disponibles = ", ".join(APPS.keys()) if APPS else "ninguna configurada todavía"
        return {"exito": False, "mensaje": f"No tengo configurada una app llamada '{nombre}'. Las que conozco: {disponibles}"}
    try:
        os.startfile(ruta)
        return {"exito": True, "mensaje": f"Se abrió {nombre} correctamente"}
    except Exception as e:
        return {"exito": False, "mensaje": f"Error al intentar abrir {nombre}: {e}"}


def activar_modo(modo):
    memoria.activar_modo(modo)
    return {"exito": True, "mensaje": f"Modo '{modo}' activado"}


def desactivar_modo():
    memoria.desactivar_modo()
    return {"exito": True, "mensaje": "Modo desactivado"}


def registrar_compromiso(texto):
    memoria.registrar_compromiso(texto)
    return {"exito": True, "mensaje": "Compromiso registrado"}


def consultar_compromisos_pendientes():
    pendientes = memoria.obtener_compromisos_pendientes()
    lista = [{"id": p[0], "texto": p[1], "fecha": p[2]} for p in pendientes]
    return {"exito": True, "compromisos": lista}


def resolver_compromiso(id_compromiso, estado):
    memoria.resolver_compromiso(id_compromiso, estado)
    return {"exito": True, "mensaje": f"Compromiso #{id_compromiso} marcado como {estado}"}


FUNCIONES = {
    "abrir_aplicacion": abrir_aplicacion,
    "activar_modo": activar_modo,
    "desactivar_modo": desactivar_modo,
    "registrar_compromiso": registrar_compromiso,
    "consultar_compromisos_pendientes": consultar_compromisos_pendientes,
    "resolver_compromiso": resolver_compromiso,
}


def ejecutar(nombre_funcion, argumentos):
    funcion = FUNCIONES.get(nombre_funcion)
    if not funcion:
        return {"exito": False, "mensaje": f"Función desconocida: {nombre_funcion}"}
    return funcion(**argumentos)