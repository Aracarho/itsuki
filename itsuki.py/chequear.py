import memoria

historial = memoria.obtener_historial_reciente(20)
print(f"Mensajes guardados: {len(historial)}\n")
for rol, contenido in historial:
    print(f"[{rol}] {contenido}")