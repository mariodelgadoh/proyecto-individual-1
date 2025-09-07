import pygame
import sys
import time

# Inicializar Pygame
pygame.init()

# Constantes de colores y dimensiones
ANCHO, ALTO = 1000, 800
FONDO_OSCURO = (48, 56, 62)
CLAVIJA_AMARILLA = (255, 197, 56)
AZUL_PISTA = (64, 185, 255)
AGUJERO_OSCURO = (35, 42, 48)
ANILLO_CLARO = (75, 85, 96)
ANILLO_HOVER = (100, 110, 125)
ANILLO_SELECCIONADO = (255, 255, 255)
ANILLO_VALIDO = (76, 175, 80)
BLANCO = (255, 255, 255)
ROJO = (244, 67, 54)
NEGRO = (0, 0, 0)

# Configuración de fuentes
pygame.font.init()
FUENTE_CLARA = pygame.font.Font(None, 32)
FUENTE_MEDIANA = pygame.font.Font(None, 40)
FUENTE_GRANDE = pygame.font.Font(None, 56)
FUENTE_PEQUEÑA = pygame.font.Font(None, 24)

# Coordenadas de las posiciones en el tablero triangular (15 posiciones)
POSICIONES = {
    1: (500, 150),   # Fila 1
    2: (450, 220), 3: (550, 220),   # Fila 2  
    4: (400, 290), 5: (500, 290), 6: (600, 290),   # Fila 3
    7: (350, 360), 8: (450, 360), 9: (550, 360), 10: (650, 360),   # Fila 4
    11: (300, 430), 12: (400, 430), 13: (500, 430), 14: (600, 430), 15: (700, 430)   # Fila 5
}

# Movimientos posibles - cada entrada representa (ficha_saltada, destino)
MOVIMIENTOS_POSIBLES = {
    1: [(2, 4), (3, 6)],
    2: [(4, 7), (5, 9)],
    3: [(5, 8), (6, 10)],
    4: [(2, 1), (5, 6), (7, 11), (8, 13)],
    5: [(8, 12), (9, 14)],
    6: [(3, 1), (5, 4), (9, 13), (10, 15)],
    7: [(4, 2), (8, 9)],
    8: [(5, 3), (9, 10)],
    9: [(5, 2), (8, 7)],
    10: [(6, 3), (9, 8)],
    11: [(7, 4), (12, 13)],
    12: [(8, 5), (13, 14)],
    13: [(8, 4), (9, 6), (12, 11), (14, 15)],
    14: [(9, 5), (13, 12)],
    15: [(10, 6), (14, 13)]
}

class Cola:
    """
    Implementación simple de una cola (queue) para algoritmos de búsqueda.
    Utilizada en los algoritmos de búsqueda en anchura (BFS) para gestionar
    los nodos pendientes de exploración.
    """
    def __init__(self):
        self.elementos = []
    
    def encolar(self, elemento):
        """Añade un elemento al final de la cola"""
        self.elementos.insert(0, elemento)
    
    def desencolar(self):
        """Elimina y devuelve el primer elemento de la cola"""
        if self.esta_vacia():
            return None
        return self.elementos.pop()
    
    def esta_vacia(self):
        """Verifica si la cola está vacía"""
        return len(self.elementos) == 0

class Comesolo:
    """Clase principal que gestiona la lógica del juego Comesolo (Solitario de Clavijas)"""
    
    def __init__(self, b):
        # Inicialización del estado del juego
        self.raiz = b  # Estado inicial del tablero
        # Árbol de búsqueda para algoritmos de resolución
        self.arbol_busqueda = {0: [set(), b, -1]}  # {id: [hijos, estado, padre]}
        self.nodo_numero = 1  # Contador de nodos en el árbol
        self.nodo_objetivo = -100  # ID del nodo que contiene la solución
        
        # Estado del juego
        self.modo_seleccion = True  # Si estamos seleccionando la posición inicial
        self.posicion_inicial_vacia = None  # Posición inicial vacía
        self.movimientos_jugador = 0  # Contador de movimientos del jugador
        self.tiempo_inicio = None  # Tiempo de inicio del juego
        self.tiempo_transcurrido = 0  # Tiempo transcurrido
        self.juego_terminado = False  # Si el juego ha terminado
        self.ganado = False  # Si el jugador ha ganado
        
        # Estado de selección de fichas
        self.ficha_seleccionada = None  # Ficha actualmente seleccionada
        self.movimientos_validos = []  # Movimientos válidos desde la ficha seleccionada
        self.pista_mostrada = None  # Pista actualmente mostrada
        
        # Sistema de resolución automática
        self.solucion_pasos = []  # Pasos de la solución encontrada
        self.resolviendo = False  # Si se está resolviendo automáticamente
        self.paso_solucion_actual = 0  # Paso actual de la solución
        self.tiempo_ultimo_paso = 0  # Tiempo del último paso de resolución
        
        # Interfaz de usuario
        self.posicion_hover = None  # Posición bajo el cursor
        self.mensaje_resolucion = ""  # Mensaje de estado de resolución
        self.solucion_existe = None  # Si existe solución para la configuración actual
    
    def establecer_posicion_inicial(self, posicion_vacia):
        """Establece la posición inicial vacía y configura el juego"""
        self.posicion_inicial_vacia = posicion_vacia
        self.modo_seleccion = False
        
        # Estado inicial: todas las posiciones ocupadas excepto una vacía
        self.raiz = [1] * 16  # Índice 0 no se usa, posiciones 1-15
        self.raiz[posicion_vacia] = 0
        self.raiz[0] = -1  # Marcador para ignorar índice 0
        
        # Reiniciar árbol de búsqueda
        self.arbol_busqueda = {0: [set(), self.raiz.copy(), -1]}
        self.nodo_numero = 1
        self.nodo_objetivo = -100
        
        # Reiniciar contadores y estado del juego
        self.movimientos_jugador = 0
        self.tiempo_inicio = time.time()
        self.tiempo_transcurrido = 0
        self.juego_terminado = False
        self.ganado = False
        self.ficha_seleccionada = None
        self.movimientos_validos = []
        self.pista_mostrada = None
        self.solucion_pasos = []
        self.resolviendo = False
        self.mensaje_resolucion = ""
        self.solucion_existe = None
        
        print(f"\n{'='*60}")
        print(f"JUEGO INICIADO - Posición inicial vacía: {posicion_vacia}")
        print(f"{'='*60}")
        
        # Verificar inmediatamente si existe solución
        self.verificar_solucion_existe()
    
    def verificar_solucion_existe(self):
        """Verifica si existe una solución para la posición inicial actual"""
        print("\n🔍 VERIFICANDO SI EXISTE SOLUCIÓN...")
        print("-" * 40)
        
        # Buscar solución completa
        solucion = self.buscar_solucion(25)  # Mayor profundidad para buscar solución completa
        
        if solucion and len(solucion) > 1:
            # Verificar que la última posición tenga solo una ficha
            estado_final = solucion[-1]
            fichas_finales = sum(1 for i in range(1, 16) if estado_final[i] == 1)
            
            if fichas_finales == 1:
                self.solucion_existe = True
                posicion_final = next(i for i in range(1, 16) if estado_final[i] == 1)
                print(f"✅ ¡SOLUCIÓN ENCONTRADA!")
                print(f"   Número de movimientos necesarios: {len(solucion) - 1}")
                print(f"   Ficha final quedará en posición: {posicion_final}")
                print("\n📋 SECUENCIA DE SOLUCIÓN:")
                print("-" * 40)
                
                # Mostrar la secuencia de solución paso a paso
                for i in range(1, len(solucion)):
                    estado_anterior = solucion[i-1]
                    estado_actual = solucion[i]
                    
                    # Encontrar el movimiento realizado
                    desde = sobre = hasta = None
                    
                    for pos in range(1, 16):
                        if estado_anterior[pos] == 1 and estado_actual[pos] == 0:
                            if desde is None:
                                desde = pos
                            else:
                                sobre = pos
                        elif estado_anterior[pos] == 0 and estado_actual[pos] == 1:
                            hasta = pos
                    
                    if desde and sobre and hasta:
                        print(f"   Paso {i}: Ficha {desde} salta sobre ficha {sobre} → posición {hasta}")
                
            else:
                self.solucion_existe = False
                print(f"❌ NO HAY SOLUCIÓN PERFECTA")
                print(f"   Mejor resultado posible: {fichas_finales} fichas restantes")
        else:
            self.solucion_existe = False
            print(f"❌ NO HAY SOLUCIÓN desde la posición inicial {self.posicion_inicial_vacia}")
        
        print("-" * 40)
    
    def generar_movimientos(self, b):
        """Genera todos los movimientos posibles desde un estado dado del tablero"""
        lista_movimientos = []
        
        # Para cada posición en el tablero
        for desde in range(1, 16):
            if b[desde] == 1:  # Si hay ficha en esta posición
                # Revisar todos los movimientos posibles desde esta posición
                for sobre, hasta in MOVIMIENTOS_POSIBLES.get(desde, []):
                    # Verificar si el movimiento es válido
                    if b[sobre] == 1 and b[hasta] == 0:
                        # Crear nuevo estado aplicando el movimiento
                        nuevo_estado = b.copy()
                        nuevo_estado[desde] = 0  # Quitar ficha de origen
                        nuevo_estado[sobre] = 0  # Eliminar ficha saltada
                        nuevo_estado[hasta] = 1  # Colocar ficha en destino
                        lista_movimientos.append(nuevo_estado)
                        
        return lista_movimientos
    
    def generar_arbol(self, profundidad):
        """Genera el árbol de búsqueda hasta la profundidad especificada usando BFS"""
        profundidad_actual = 0
        self.nodo_objetivo = -100
        objetivo_encontrado = False
        
        # Expandir el árbol nivel por nivel (BFS)
        while profundidad_actual < profundidad and not objetivo_encontrado:
            arbol_nuevo = dict()
            
            # Expandir cada nodo en el nivel actual
            for id in self.arbol_busqueda:
                if len(self.arbol_busqueda[id][0]) < 1 and not objetivo_encontrado:
                    # Generar movimientos desde este estado
                    lista_movimientos = self.generar_movimientos(self.arbol_busqueda[id][1])
                    
                    for movimiento in lista_movimientos:
                        # Evitar retroceder al estado padre (evitar ciclos)
                        if profundidad_actual > 0 and movimiento == self.arbol_busqueda[self.arbol_busqueda[id][2]][1]:
                            continue
                            
                        # Añadir nuevo nodo al árbol
                        self.arbol_busqueda[id][0].add(self.nodo_numero)
                        arbol_nuevo[self.nodo_numero] = [set(), movimiento, id]
                        
                        # Verificar si es estado objetivo (solo una ficha)
                        if sum(1 for i in range(1, 16) if movimiento[i] == 1) == 1:
                            self.nodo_objetivo = self.nodo_numero
                            objetivo_encontrado = True
                            break
                            
                        self.nodo_numero += 1
                        if self.nodo_numero > 15000:  # Límite de seguridad aumentado
                            break
            
            # Agregar nuevos nodos al árbol principal
            for key in arbol_nuevo:
                self.arbol_busqueda[key] = arbol_nuevo[key]
                
            profundidad_actual += 1
            if objetivo_encontrado:
                print(f'🎯 Objetivo encontrado a profundidad {profundidad_actual}')
        
        return self.nodo_objetivo
    
    def imprimir_solucion(self):
        """Reconstruye e imprime la solución desde el nodo objetivo hasta la raíz"""
        if self.nodo_objetivo < -1:
            return []
            
        solucion = []
        nodo_actual = self.nodo_objetivo
        
        # Reconstruir el camino desde el objetivo hasta la raíz
        while nodo_actual != -1:
            solucion.append(self.arbol_busqueda[nodo_actual][1])
            nodo_actual = self.arbol_busqueda[nodo_actual][2]

        # Invertir para tener la secuencia correcta (raíz -> objetivo)
        solucion.reverse()
        return solucion
    
    def buscar_solucion(self, max_profundidad=20):
        """Busca una solución usando el mismo enfoque que 8-puzzle (BFS)"""
        # Reiniciar el árbol de búsqueda con el estado actual
        self.arbol_busqueda = {0: [set(), self.raiz.copy(), -1]}
        self.nodo_numero = 1
        self.nodo_objetivo = -100
        
        # Generar árbol hasta la profundidad máxima
        self.generar_arbol(max_profundidad)
        
        # Devolver la solución si se encontró
        return self.imprimir_solucion()
    
    def obtener_movimientos_desde_posicion(self, posicion):
        """Obtiene todos los movimientos posibles desde una posición específica"""
        movimientos = []
        
        # Verificar que haya una ficha en la posición
        if self.raiz and self.raiz[posicion] == 1:
            # Revisar todos los movimientos posibles desde esta posición
            for sobre, hasta in MOVIMIENTOS_POSIBLES.get(posicion, []):
                # Verificar si el movimiento es válido
                if self.raiz[sobre] == 1 and self.raiz[hasta] == 0:
                    movimientos.append((posicion, sobre, hasta))
                    
        return movimientos
    
    def obtener_destinos_validos(self):
        """Obtiene solo las posiciones de destino válidas para la ficha seleccionada"""
        destinos = []
        
        if self.ficha_seleccionada and self.movimientos_validos:
            for desde, sobre, hasta in self.movimientos_validos:
                destinos.append(hasta)
                
        return destinos
    
    def hacer_movimiento(self, desde, hasta):
        """Realiza un movimiento si es válido"""
        if self.resolviendo:
            return False
        
        print(f"\n🎯 INTENTANDO MOVIMIENTO: Ficha {desde} → Posición {hasta}")
        
        # Verificar si el movimiento está en la lista de movimientos válidos
        movimiento_valido = None
        for mov_desde, mov_sobre, mov_hasta in self.movimientos_validos:
            if mov_desde == desde and mov_hasta == hasta:
                movimiento_valido = (mov_desde, mov_sobre, mov_hasta)
                break
        
        if movimiento_valido:
            mov_desde, mov_sobre, mov_hasta = movimiento_valido
            
            print(f"✅ MOVIMIENTO VÁLIDO:")
            print(f"   • Ficha {mov_desde} se mueve a posición {mov_hasta}")
            print(f"   • Elimina ficha {mov_sobre}")
            print(f"   • Estado antes: Pos{mov_desde}={self.raiz[mov_desde]}, Pos{mov_sobre}={self.raiz[mov_sobre]}, Pos{mov_hasta}={self.raiz[mov_hasta]}")
            
            # Realizar el movimiento
            self.raiz[mov_desde] = 0  # Quitar ficha original
            self.raiz[mov_sobre] = 0   # Eliminar ficha saltada
            self.raiz[mov_hasta] = 1   # Colocar ficha en destino
            
            print(f"   • Estado después: Pos{mov_desde}={self.raiz[mov_desde]}, Pos{mov_sobre}={self.raiz[mov_sobre]}, Pos{mov_hasta}={self.raiz[mov_hasta]}")
            
            self.movimientos_jugador += 1
            self.verificar_fin_juego()
            
            # Mostrar estado del tablero
            fichas_restantes = sum(1 for i in range(1, 16) if self.raiz[i] == 1)
            print(f"   • Fichas restantes: {fichas_restantes}")
            
            return True
        else:
            print(f"❌ MOVIMIENTO NO VÁLIDO: No existe ruta de {desde} a {hasta}")
            return False
    
    def verificar_fin_juego(self):
        """Verifica si el juego ha terminado (victoria o sin movimientos)"""
        if not self.raiz:
            return
            
        # Contar fichas restantes
        fichas_restantes = sum(1 for i in range(1, 16) if self.raiz[i] == 1)
        
        # Verificar victoria (solo una ficha)
        if fichas_restantes == 1:
            self.juego_terminado = True
            self.ganado = True
            self.tiempo_transcurrido = time.time() - self.tiempo_inicio
            posicion_final = next(i for i in range(1, 16) if self.raiz[i] == 1)
            print(f"\n🎉 ¡FELICIDADES! ¡GANASTE!")
            print(f"   • Ficha final en posición: {posicion_final}")
            print(f"   • Movimientos realizados: {self.movimientos_jugador}")
            print(f"   • Tiempo: {int(self.tiempo_transcurrido//60):02d}:{int(self.tiempo_transcurrido%60):02d}")
            return
        
        # Verificar si hay movimientos disponibles
        movimientos_disponibles = self.generar_movimientos(self.raiz)
        if not movimientos_disponibles:
            self.juego_terminado = True
            self.ganado = False
            self.tiempo_transcurrido = time.time() - self.tiempo_inicio
            print(f"\n🔚 JUEGO TERMINADO")
            print(f"   • Fichas restantes: {fichas_restantes}")
            print(f"   • Movimientos realizados: {self.movimientos_jugador}")
            print(f"   • No hay más movimientos posibles")
    
    def obtener_pista(self):
        """Obtiene una pista usando el árbol de búsqueda"""
        if not self.raiz or self.resolviendo:
            return None
            
        # Buscar solución con profundidad limitada
        objetivo = self.generar_arbol(5)
        if objetivo > 0:
            # Reconstruir el primer movimiento de la solución
            camino = []
            nodo_actual = objetivo
            while nodo_actual != -1:
                camino.append(self.arbol_busqueda[nodo_actual][1])
                nodo_actual = self.arbol_busqueda[nodo_actual][2]
            
            camino.reverse()
            
            if len(camino) > 1:
                # Encontrar la diferencia entre el estado actual y el primer paso
                estado_actual = camino[0]
                primer_paso = camino[1]
                
                # Encontrar qué ficha se movió
                for i in range(1, 16):
                    if estado_actual[i] == 1 and primer_paso[i] == 0:
                        desde = i
                    elif estado_actual[i] == 0 and primer_paso[i] == 1:
                        hasta = i
                
                # Encontrar qué ficha se saltó
                for sobre in range(1, 16):
                    if estado_actual[sobre] == 1 and primer_paso[sobre] == 0 and sobre != desde:
                        return (desde, sobre, hasta)
        
        return None
    
    def resolver_automaticamente(self):
        """Inicia la resolución automática usando el árbol de búsqueda"""
        if not self.juego_terminado:
            self.resolviendo = True
            self.ficha_seleccionada = None
            self.movimientos_validos = []
            self.pista_mostrada = None
            
            print(f"\n🤖 INICIANDO RESOLUCIÓN AUTOMÁTICA...")
            print("-" * 40)
            
            # Buscar solución desde el estado actual
            solucion = self.buscar_solucion(25)
            
            if solucion and len(solucion) > 1:
                # Verificar que sea solución completa
                estado_final = solucion[-1]
                fichas_finales = sum(1 for i in range(1, 16) if estado_final[i] == 1)
                
                if fichas_finales == 1:
                    self.solucion_pasos = solucion[1:]  # Saltar el estado actual
                    self.mensaje_resolucion = f"Solución encontrada ({len(self.solucion_pasos)} movimientos)"
                    print(f"✅ Solución encontrada con {len(self.solucion_pasos)} movimientos")
                    
                    self.paso_solucion_actual = 0
                    self.tiempo_ultimo_paso = time.time()
                else:
                    self.mensaje_resolucion = "Solución parcial encontrada"
                    print(f"⚠️  Solución parcial: quedaran {fichas_finales} fichas")
                    self.solucion_pasos = solucion[1:]
                    self.paso_solucion_actual = 0
                    self.tiempo_ultimo_paso = time.time()
            else:
                self.mensaje_resolucion = "No se encontró solución"
                print("❌ No se encontró solución desde el estado actual")
                self.resolviendo = False
    
    def actualizar_resolucion_automatica(self):
        """Actualiza la resolución automática paso a paso"""
        if self.resolviendo and self.solucion_pasos and time.time() - self.tiempo_ultimo_paso > 1.0:
            if self.paso_solucion_actual < len(self.solucion_pasos):
                # Aplicar el siguiente paso de la solución
                estado_anterior = self.raiz.copy()
                self.raiz = self.solucion_pasos[self.paso_solucion_actual].copy()
                
                # Encontrar qué movimiento se hizo
                desde = sobre = hasta = None
                for pos in range(1, 16):
                    if estado_anterior[pos] == 1 and self.raiz[pos] == 0:
                        if desde is None:
                            desde = pos
                        else:
                            sobre = pos
                    elif estado_anterior[pos] == 0 and self.raiz[pos] == 1:
                        hasta = pos
                
                if desde and sobre and hasta:
                    print(f"🤖 Paso {self.paso_solucion_actual + 1}: Ficha {desde} salta sobre {sobre} → {hasta}")
                
                self.movimientos_jugador += 1
                self.paso_solucion_actual += 1
                self.tiempo_ultimo_paso = time.time()
                
                if self.paso_solucion_actual >= len(self.solucion_pasos):
                    self.resolviendo = False
                    self.verificar_fin_juego()
            else:
                self.resolviendo = False
    
    def reiniciar_seleccion(self):
        """Reinicia el juego al modo de selección de posición inicial"""
        self.modo_seleccion = True
        self.posicion_inicial_vacia = None
        self.raiz = None
        self.arbol_busqueda = {0: [set(), None, -1]}
        self.nodo_numero = 1
        self.nodo_objetivo = -100
        self.movimientos_jugador = 0
        self.tiempo_inicio = None
        self.tiempo_transcurrido = 0
        self.juego_terminado = False
        self.ganado = False
        self.ficha_seleccionada = None
        self.movimientos_validos = []
        self.pista_mostrada = None
        self.solucion_pasos = []
        self.resolviendo = False
        self.mensaje_resolucion = ""
        self.solucion_existe = None
        print(f"\n🔄 REINICIANDO JUEGO...")
        print("Selecciona una nueva posición inicial vacía")

# Crear instancia del juego
juego = Comesolo(None)

# Configurar ventana
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Comesolo (Solitario de Clavijas) - Basado en 8-puzzle")

# Botones modernos para la interfaz
ancho_boton, alto_boton = 150, 50
espaciado_botones = 20
boton_y = 550

# Definir rectángulos para los botones
nuevo_btn = pygame.Rect((ANCHO - 3 * ancho_boton - 2 * espaciado_botones) // 2, boton_y, ancho_boton, alto_boton)
resolver_btn = pygame.Rect(nuevo_btn.right + espaciado_botones, boton_y, ancho_boton, alto_boton)
salir_btn = pygame.Rect(resolver_btn.right + espaciado_botones, boton_y, ancho_boton, alto_boton)

def obtener_posicion_desde_coord(x, y):
    """Convierte coordenadas de pantalla a posición del tablero"""
    for pos, (px, py) in POSICIONES.items():
        # Calcular distancia entre el punto clickeado y la posición
        if ((x - px) ** 2 + (y - py) ** 2) ** 0.5 <= 35:
            return pos
    return None

def dibujar_boton_moderno(rect, color, texto, hover=False, activo=True):
    """Dibuja un botón con estilo moderno"""
    if not activo:
        color = (color[0] // 3, color[1] // 3, color[2] // 3)
    elif hover:
        color = tuple(min(c + 30, 255) for c in color)
    
    # Dibujar el botón con bordes redondeados
    pygame.draw.rect(pantalla, color, rect, border_radius=25)
    color_borde = tuple(min(c + 40, 255) for c in color)
    pygame.draw.rect(pantalla, color_borde, rect, width=2, border_radius=25)
    
    # Dibujar el texto del botón
    color_texto = BLANCO if activo else (120, 120, 120)
    texto_boton = FUENTE_CLARA.render(texto, True, color_texto)
    rect_texto = texto_boton.get_rect(center=rect.center)
    pantalla.blit(texto_boton, rect_texto)

def dibujar_clavija_moderna(x, y, radio, tiene_ficha, estado, pos_num):
    """Dibuja una ficha con el estilo moderno y número"""
    if tiene_ficha:
        # Dibujar efectos según el estado de la ficha
        if estado == 'selected':
            pygame.draw.circle(pantalla, ANILLO_SELECCIONADO, (x, y), radio + 8, 4)
        elif estado == 'valid_move':
            pygame.draw.circle(pantalla, ANILLO_VALIDO, (x, y), radio + 8, 4)
        elif estado == 'hint_from':
            pygame.draw.circle(pantalla, ANILLO_CLARO, (x, y), radio + 5, 3)
            pygame.draw.circle(pantalla, AZUL_PISTA, (x, y), radio)
            return
        elif estado == 'hint_over':
            # Efecto de pulso para la pista
            pulso = int(5 + 3 * abs(pygame.time.get_ticks() / 300 % 2 - 1))
            pygame.draw.circle(pantalla, AZUL_PISTA, (x, y), radio + pulso, 3)
        
        # Dibujar la ficha normal
        pygame.draw.circle(pantalla, ANILLO_CLARO, (x, y), radio + 5, 3)
        pygame.draw.circle(pantalla, CLAVIJA_AMARILLA, (x, y), radio)
        
        # Dibujar número en la ficha
        texto_numero = FUENTE_PEQUEÑA.render(str(pos_num), True, NEGRO)
        rect_numero = texto_numero.get_rect(center=(x, y))
        pantalla.blit(texto_numero, rect_numero)
        
    else:
        # Dibujar un hueco vacío
        if estado == 'hint_to':
            pygame.draw.circle(pantalla, AZUL_PISTA, (x, y), radio + 5, 4)
        elif estado == 'valid_move':
            pygame.draw.circle(pantalla, ANILLO_VALIDO, (x, y), radio + 8, 5)
        
        pygame.draw.circle(pantalla, ANILLO_CLARO, (x, y), radio + 5, 3)
        pygame.draw.circle(pantalla, AGUJERO_OSCURO, (x, y), radio)
        
        # Dibujar número en el hueco vacío
        texto_numero = FUENTE_PEQUEÑA.render(str(pos_num), True, BLANCO)
        rect_numero = texto_numero.get_rect(center=(x, y))
        pantalla.blit(texto_numero, rect_numero)

def dibujar_tablero():
    """Dibuja el tablero completo con el diseño moderno"""
    # Limpiar la pantalla
    pantalla.fill(FONDO_OSCURO)
    
    # Determinar el título según el estado del juego
    if juego.modo_seleccion:
        titulo = "Selecciona posición inicial vacía"
        color_titulo = BLANCO
    elif juego.juego_terminado:
        if juego.ganado:
            titulo = "¡PERFECTO!"
            color_titulo = ANILLO_VALIDO
        else:
            titulo = "Juego Terminado"
            color_titulo = ROJO
    elif juego.resolviendo:
        titulo = "Resolviendo..."
        color_titulo = AZUL_PISTA
    else:
        titulo = "Comesolo (Solitario de Clavijas)"
        color_titulo = BLANCO
    
    # Dibujar título
    texto_titulo = FUENTE_GRANDE.render(titulo, True, color_titulo)
    rect_titulo = texto_titulo.get_rect(center=(ANCHO // 2, 60))
    pantalla.blit(texto_titulo, rect_titulo)
    
    # Mostrar mensaje de resolución si existe
    if juego.mensaje_resolucion:
        texto_mensaje = FUENTE_CLARA.render(juego.mensaje_resolucion, True, AZUL_PISTA)
        rect_mensaje = texto_mensaje.get_rect(center=(ANCHO // 2, 100))
        pantalla.blit(texto_mensaje, rect_mensaje)
    
    # Obtener destinos válidos para resaltar
    destinos_validos = juego.obtener_destinos_validos() if juego.ficha_seleccionada else []
    
    # Dibujar todas las posiciones del tablero
    for pos in range(1, 16):
        x, y = POSICIONES[pos]
        tiene_ficha = not juego.modo_seleccion and juego.raiz and juego.raiz[pos] == 1
        
        estado = 'normal'
        
        # Modo selección: todas las posiciones tienen ficha
        if juego.modo_seleccion:
            tiene_ficha = True
        # Mostrar pista si está activa
        elif juego.pista_mostrada:
            desde, sobre, hasta = juego.pista_mostrada
            if pos == desde:
                estado = 'hint_from'
            elif pos == sobre:
                estado = 'hint_over'
            elif pos == hasta:
                estado = 'hint_to'
        # Resaltar ficha seleccionada
        elif juego.ficha_seleccionada == pos:
            estado = 'selected'
        # Resaltar destinos válidos
        elif pos in destinos_validos:
            estado = 'valid_move'
        
        # Detectar hover
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if ((mouse_x - x) ** 2 + (mouse_y - y) ** 2) ** 0.5 <= 35:
            juego.posicion_hover = pos
        
        # Dibujar la clavija/hueco
        dibujar_clavija_moderna(x, y, 25, tiene_ficha, estado, pos)
    
    # Dibujar información del juego si no estamos en modo selección
    if not juego.modo_seleccion:
        info_y = 620
        if juego.raiz:
            # Contar fichas restantes
            fichas_restantes = sum(1 for i in range(1, 16) if juego.raiz[i] == 1)
            
            # Mostrar contador de movimientos
            texto_movimientos = FUENTE_MEDIANA.render(f"Movimientos: {juego.movimientos_jugador}", True, BLANCO)
            rect_movimientos = texto_movimientos.get_rect(center=(ANCHO // 4, info_y))
            pantalla.blit(texto_movimientos, rect_movimientos)
            
            # Mostrar contador de fichas
            texto_clavijas = FUENTE_MEDIANA.render(f"Fichas: {fichas_restantes}", True, BLANCO)
            rect_clavijas = texto_clavijas.get_rect(center=(ANCHO // 2, info_y))
            pantalla.blit(texto_clavijas, rect_clavijas)
            
            # Actualizar y mostrar tiempo
            if juego.tiempo_inicio and not juego.juego_terminado:
                juego.tiempo_transcurrido = time.time() - juego.tiempo_inicio
            
            minutos = int(juego.tiempo_transcurrido // 60)
            segundos = int(juego.tiempo_transcurrido % 60)
            texto_tiempo = FUENTE_MEDIANA.render(f"Tiempo: {minutos:02d}:{segundos:02d}", True, BLANCO)
            rect_tiempo = texto_tiempo.get_rect(center=(3 * ANCHO // 4, info_y))
            pantalla.blit(texto_tiempo, rect_tiempo)
        
        # Mostrar información de la ficha seleccionada
        if juego.ficha_seleccionada and juego.movimientos_validos:
            instruccion = f"Ficha {juego.ficha_seleccionada} seleccionada - {len(juego.movimientos_validos)} movimientos posibles"
        elif juego.ficha_seleccionada:
            instruccion = f"Ficha {juego.ficha_seleccionada} seleccionada - Sin movimientos válidos"
        elif not juego.juego_terminado and not juego.resolviendo:
            instruccion = "Haz clic en una ficha amarilla para seleccionarla"
        else:
            instruccion = ""
        
        if instruccion:
            texto_instruccion = FUENTE_CLARA.render(instruccion, True, (200, 200, 200))
            rect_instruccion = texto_instruccion.get_rect(center=(ANCHO // 2, 500))
            pantalla.blit(texto_instruccion, rect_instruccion)
        
        # Detectar hover sobre botones
        posicion_raton = pygame.mouse.get_pos()
        
        # Dibujar botones
        dibujar_boton_moderno(nuevo_btn, (70, 130, 180), "Nuevo", nuevo_btn.collidepoint(posicion_raton))
        
        resolver_activo = not juego.juego_terminado
        dibujar_boton_moderno(resolver_btn, (156, 39, 176), "Resolver",
                            resolver_btn.collidepoint(posicion_raton), resolver_activo)
        
        dibujar_boton_moderno(salir_btn, (244, 67, 54), "Salir", salir_btn.collidepoint(posicion_raton))

# Bucle principal del juego
ejecutando = True
reloj = pygame.time.Clock()

# Mensaje de bienvenida en consola
print("=" * 60)
print("         COMESOLO (SOLITARIO DE CLAVIJAS) - BASADO EN 8-PUZZLE")
print("=" * 60)
print("🎯 OBJETIVO: Eliminar todas las fichas excepto una")
print("📋 REGLAS: Salta sobre una ficha adyacente a un espacio vacío")
print("=" * 60)
print("📖 INSTRUCCIONES:")
print("1. Haz clic en una posición para comenzar (será la posición vacía)")
print("2. Selecciona fichas y muévelas a posiciones válidas (verdes)")
print("3. Usa 'Resolver' para ver la solución usando el algoritmo de 8-puzzle")
print("4. El programa verificará automáticamente si existe solución")
print("=" * 60)

# Bucle principal del juego
while ejecutando:
    # Procesar eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            
            # Modo selección de posición inicial vacía
            if juego.modo_seleccion:
                posicion_clic = obtener_posicion_desde_coord(x, y)
                if posicion_clic:
                    juego.establecer_posicion_inicial(posicion_clic)
            
            # Modo juego normal
            else:
                # Botón "Nuevo"
                if nuevo_btn.collidepoint(x, y):
                    juego.reiniciar_seleccion()
                
                # Botón "Resolver"
                elif resolver_btn.collidepoint(x, y) and not juego.juego_terminado:
                    juego.resolver_automaticamente()
                
                # Botón "Salir"
                elif salir_btn.collidepoint(x, y):
                    print(f"\n👋 ¡Gracias por jugar!")
                    ejecutando = False
                
                # Interacción con el tablero
                else:
                    posicion_clic = obtener_posicion_desde_coord(x, y)
                    if posicion_clic and not juego.resolviendo and not juego.juego_terminado:
                        juego.pista_mostrada = None
                        
                        # Si no hay ficha seleccionada
                        if juego.ficha_seleccionada is None:
                            # Seleccionar una ficha
                            if juego.raiz[posicion_clic] == 1:
                                juego.ficha_seleccionada = posicion_clic
                                juego.movimientos_validos = juego.obtener_movimientos_desde_posicion(posicion_clic)
                                print(f"\n👆 FICHA {posicion_clic} SELECCIONADA")
                                if juego.movimientos_validos:
                                    print(f"   Movimientos disponibles: {len(juego.movimientos_validos)}")
                                    for i, (desde, sobre, hasta) in enumerate(juego.movimientos_validos, 1):
                                        print(f"   {i}. Saltar ficha {sobre} → posición {hasta}")
                                else:
                                    print("   ❌ Sin movimientos válidos")
                            else:
                                print(f"\n❌ No hay ficha en posición {posicion_clic}")
                        else:
                            # Ya hay una ficha seleccionada
                            if posicion_clic == juego.ficha_seleccionada:
                                # Deseleccionar
                                print(f"\n↩️  Ficha {juego.ficha_seleccionada} deseleccionada")
                                juego.ficha_seleccionada = None
                                juego.movimientos_validos = []
                            elif juego.raiz[posicion_clic] == 1:
                                # Seleccionar otra ficha
                                juego.ficha_seleccionada = posicion_clic
                                juego.movimientos_validos = juego.obtener_movimientos_desde_posicion(posicion_clic)
                                print(f"\n👆 FICHA {posicion_clic} SELECCIONADA")
                                if juego.movimientos_validos:
                                    print(f"   Movimientos disponibles: {len(juego.movimientos_validos)}")
                                    for i, (desde, sobre, hasta) in enumerate(juego.movimientos_validos, 1):
                                        print(f"   {i}. Saltar ficha {sobre} → posición {hasta}")
                                else:
                                    print("   ❌ Sin movimientos válidos")
                            else:
                                # Intentar mover a una posición vacía
                                if juego.hacer_movimiento(juego.ficha_seleccionada, posicion_clic):
                                    juego.ficha_seleccionada = None
                                    juego.movimientos_validos = []
    
    # Actualizar resolución automática si está activa
    if juego.resolviendo:
        juego.actualizar_resolucion_automatica()
    
    # Dibujar el tablero y actualizar la pantalla
    dibujar_tablero()
    pygame.display.flip()
    reloj.tick(60)  # Limitar a 60 FPS

# Salir del juego
pygame.quit()
sys.exit()