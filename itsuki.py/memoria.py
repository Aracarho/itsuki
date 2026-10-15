import sqlite3
from datetime import datetime, date

DB_PATH = "itsuki_memoria.db"


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def inicializar():
    conn = conectar()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS estado (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            afecto INTEGER NOT NULL DEFAULT 78,
            dias_sin_interactuar INTEGER NOT NULL DEFAULT 0,
            honestidad_score INTEGER NOT NULL DEFAULT 90,
            ultima_interaccion TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rol TEXT NOT NULL,
            contenido TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS modo_actividad (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            modo TEXT NOT NULL DEFAULT 'ninguno',
            desde TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS compromisos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT NOT NULL,
            fecha_creado TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'pendiente',
            fecha_resuelto TEXT
        )
    """)
    conn.execute("""
        INSERT OR IGNORE INTO estado (id, afecto, dias_sin_interactuar, honestidad_score, ultima_interaccion)
        VALUES (1, 78, 0, 90, NULL)
    """)
    conn.execute("""
        INSERT OR IGNORE INTO modo_actividad (id, modo, desde) VALUES (1, 'ninguno', NULL)
    """)
    conn.commit()
    conn.close()


def calcular_modo(afecto, dias_sin_interactuar, honestidad_score):
    if dias_sin_interactuar >= 3 or honestidad_score < 50:
        return "intensa"
    if dias_sin_interactuar >= 1 or honestidad_score < 70:
        return "alerta"
    if afecto > 70:
        return "dulce"
    return "neutral"


def cargar_estado():
    conn = conectar()
    fila = conn.execute(
        "SELECT afecto, dias_sin_interactuar, honestidad_score, ultima_interaccion FROM estado WHERE id = 1"
    ).fetchone()
    conn.close()
    afecto, dias_sin_interactuar, honestidad_score, ultima_interaccion = fila

    if ultima_interaccion:
        ultima_fecha = datetime.fromisoformat(ultima_interaccion).date()
        dias_reales = (date.today() - ultima_fecha).days
        dias_sin_interactuar = max(dias_sin_interactuar, dias_reales)
        afecto = max(20, afecto - 5 * dias_reales)

    modo = calcular_modo(afecto, dias_sin_interactuar, honestidad_score)
    return {
        "afecto": afecto,
        "dias_sin_interactuar": dias_sin_interactuar,
        "honestidad_score": honestidad_score,
        "modo_actual": modo,
    }


def guardar_interaccion():
    estado = cargar_estado()
    nuevo_afecto = min(100, estado["afecto"] + 2)
    conn = conectar()
    conn.execute(
        "UPDATE estado SET afecto = ?, dias_sin_interactuar = 0, ultima_interaccion = ? WHERE id = 1",
        (nuevo_afecto, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def guardar_mensaje(rol, contenido):
    conn = conectar()
    conn.execute(
        "INSERT INTO mensajes (rol, contenido, timestamp) VALUES (?, ?, ?)",
        (rol, contenido, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def obtener_historial_reciente(limite=10):
    conn = conectar()
    filas = conn.execute(
        "SELECT rol, contenido FROM mensajes ORDER BY id DESC LIMIT ?", (limite,)
    ).fetchall()
    conn.close()
    return list(reversed(filas))


def activar_modo(modo):
    conn = conectar()
    conn.execute(
        "UPDATE modo_actividad SET modo = ?, desde = ? WHERE id = 1",
        (modo, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def desactivar_modo():
    conn = conectar()
    conn.execute("UPDATE modo_actividad SET modo = 'ninguno', desde = NULL WHERE id = 1")
    conn.commit()
    conn.close()


def obtener_modo_activo():
    conn = conectar()
    fila = conn.execute("SELECT modo, desde FROM modo_actividad WHERE id = 1").fetchone()
    conn.close()
    modo, desde = fila
    minutos = 0
    if desde:
        minutos = round((datetime.now() - datetime.fromisoformat(desde)).total_seconds() / 60)
    return modo, desde, minutos


def registrar_compromiso(texto):
    conn = conectar()
    conn.execute(
        "INSERT INTO compromisos (texto, fecha_creado, estado) VALUES (?, ?, 'pendiente')",
        (texto, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def resolver_compromiso(id_compromiso, estado):
    conn = conectar()
    conn.execute(
        "UPDATE compromisos SET estado = ?, fecha_resuelto = ? WHERE id = ?",
        (estado, datetime.now().isoformat(), id_compromiso),
    )
    conn.commit()
    conn.close()


def obtener_compromisos_pendientes():
    conn = conectar()
    filas = conn.execute(
        "SELECT id, texto, fecha_creado FROM compromisos WHERE estado = 'pendiente' ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return filas