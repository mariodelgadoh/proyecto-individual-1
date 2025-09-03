import pygame
import sys
import time
import random

# Inicializar Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 1000, 800
DARK_BG = (48, 56, 62)
YELLOW_PEG = (255, 197, 56)
BLUE_HINT = (64, 185, 255)
DARK_HOLE = (35, 42, 48)
LIGHT_RING = (75, 85, 96)
HOVER_RING = (100, 110, 125)
SELECT_RING = (255, 255, 255)
VALID_RING = (76, 175, 80)
WHITE = (255, 255, 255)
RED = (244, 67, 54)

# Fuentes
pygame.font.init()
FONT_LIGHT = pygame.font.Font(None, 32)
FONT_MEDIUM = pygame.font.Font(None, 40)
FONT_LARGE = pygame.font.Font(None, 56)

# Coordenadas de las posiciones en el tablero triangular (15 posiciones)
POSITIONS = {
    1: (500, 150),   # Fila 1
    2: (450, 220), 3: (550, 220),   # Fila 2  
    4: (400, 290), 5: (500, 290), 6: (600, 290),   # Fila 3
    7: (350, 360), 8: (450, 360), 9: (550, 360), 10: (650, 360),   # Fila 4
    11: (300, 430), 12: (400, 430), 13: (500, 430), 14: (600, 430), 15: (700, 430)   # Fila 5
}

# Movimientos posibles
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

class Queue:
    """Implementación simple de una cola (queue)"""
    def __init__(self):
        self.items = []
    
    def enqueue(self, item):
        self.items.insert(0, item)
    
    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.pop()
    
    def is_empty(self):
        return len(self.items) == 0

class pegsolitaire():
    def __init__(self, b):
        self.root = b
        self.stree = {0: [set(), b, -1]}  # {id: [hijos, estado, padre]}
        self.nnodes = 1
        self.gnode = -100
        self.modo_seleccion = True
        self.posicion_inicial_vacia = None
        self.movimientos_jugador = 0
        self.start_time = None
        self.elapsed_time = 0
        self.juego_terminado = False
        self.ganado = False
        self.ficha_seleccionada = None
        self.movimientos_validos = []
        self.pista_mostrada = None
        self.solucion_pasos = []
        self.resolviendo = False
        self.paso_solucion_actual = 0
        self.tiempo_ultimo_paso = 0
        self.hover_pos = None
        self.mensaje_resolucion = ""
    
    def establecer_posicion_inicial(self, posicion_vacia):
        """Establece la posición inicial vacía y configura el juego"""
        self.posicion_inicial_vacia = posicion_vacia
        self.modo_seleccion = False
        
        # Estado inicial: todas las posiciones ocupadas excepto una vacía
        self.root = [1] * 16  # Índice 0 no se usa, posiciones 1-15
        self.root[posicion_vacia] = 0
        self.root[0] = -1  # Marcador para ignorar índice 0
        
        # Reiniciar árbol de búsqueda
        self.stree = {0: [set(), self.root.copy(), -1]}
        self.nnodes = 1
        self.gnode = -100
        
        self.movimientos_jugador = 0
        self.start_time = time.time()
        self.elapsed_time = 0
        self.juego_terminado = False
        self.ganado = False
        self.ficha_seleccionada = None
        self.movimientos_validos = []
        self.pista_mostrada = None
        self.solucion_pasos = []
        self.resolviendo = False
        self.mensaje_resolucion = ""
    
    def genmoves(self, b):
        """Genera todos los movimientos posibles desde un estado dado (similar a 8-puzzle)"""
        lmov = []
        for desde in range(1, 16):
            if b[desde] == 1:  # Si hay ficha en esta posición
                for sobre, hasta in MOVIMIENTOS_POSIBLES.get(desde, []):
                    if b[sobre] == 1 and b[hasta] == 0:
                        nuevo_estado = b.copy()
                        nuevo_estado[desde] = 0
                        nuevo_estado[sobre] = 0
                        nuevo_estado[hasta] = 1
                        lmov.append(nuevo_estado)
        return lmov
    
    def gentree(self, sdepth):
        """Genera el árbol de búsqueda hasta la profundidad especificada (similar a 8-puzzle)"""
        depth = 0
        self.gnode = -100
        gfound = False
        
        while depth < sdepth and not gfound:
            ntree = dict()
            for id in self.stree:
                if len(self.stree[id][0]) < 1 and not gfound:
                    lmov = self.genmoves(self.stree[id][1])
                    for mv in lmov:
                        # Evitar retroceder al estado padre
                        if depth > 0 and mv == self.stree[self.stree[id][2]][1]:
                            continue
                            
                        self.stree[id][0].add(self.nnodes)
                        ntree[self.nnodes] = [set(), mv, id]
                        
                        # Verificar si es estado objetivo (solo una ficha)
                        if sum(1 for i in range(1, 16) if mv[i] == 1) == 1:
                            self.gnode = self.nnodes
                            gfound = True
                            break
                            
                        self.nnodes += 1
                        if self.nnodes > 10000:  # Límite de seguridad
                            break
            
            # Agregar nuevos nodos al árbol
            for key in ntree:
                self.stree[key] = ntree[key]
                
            depth += 1
            if gfound:
                print(f'Objetivo encontrado a profundidad {depth}')
        
        return self.gnode
    
    def printsolution(self):
        """Reconstruye e imprime la solución desde el nodo objetivo"""
        if self.gnode < -1:
            print('No se encontró solución...')
            return []
            
        sol = []
        cnode = self.gnode
        while cnode != -1:
            sol.append(self.stree[cnode][1])
            cnode = self.stree[cnode][2]

        sol.reverse()
        return sol
    
    def buscar_solucion(self, max_profundidad=20):
        """Busca una solución usando el mismo enfoque que 8-puzzle"""
        self.gentree(max_profundidad)
        return self.printsolution()
    
    def obtener_movimientos_desde_posicion(self, posicion):
        """Obtiene todos los movimientos posibles desde una posición específica"""
        movimientos = []
        if self.root and self.root[posicion] == 1:
            for sobre, hasta in MOVIMIENTOS_POSIBLES.get(posicion, []):
                if self.root[sobre] == 1 and self.root[hasta] == 0:
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
            
        for sobre, _ in MOVIMIENTOS_POSIBLES.get(desde, []):
            if self.root[sobre] == 1 and self.root[hasta] == 0:
                # Verificar que el movimiento sea válido
                nuevo_estado = self.root.copy()
                nuevo_estado[desde] = 0
                nuevo_estado[sobre] = 0
                nuevo_estado[hasta] = 1
                
                self.root = nuevo_estado
                self.movimientos_jugador += 1
                self.verificar_fin_juego()
                return True
        return False
    
    def verificar_fin_juego(self):
        """Verifica si el juego ha terminado"""
        if not self.root:
            return
            
        fichas_restantes = sum(1 for i in range(1, 16) if self.root[i] == 1)
        
        if fichas_restantes == 1:
            self.juego_terminado = True
            self.ganado = True
            self.elapsed_time = time.time() - self.start_time
            print(f"¡Felicidades! Ganaste con {fichas_restantes} ficha restante en {self.movimientos_jugador} movimientos")
            return
        
        movimientos_disponibles = self.genmoves(self.root)
        if not movimientos_disponibles:
            self.juego_terminado = True
            self.ganado = False
            self.elapsed_time = time.time() - self.start_time
            print(f"Juego terminado. Fichas restantes: {fichas_restantes}")
    
    def obtener_pista(self):
        """Obtiene una pista usando el árbol de búsqueda"""
        if not self.root or self.resolviendo:
            return None
            
        # Buscar solución con profundidad limitada
        objetivo = self.gentree(5)
        if objetivo > 0:
            # Reconstruir el primer movimiento de la solución
            camino = []
            cnode = objetivo
            while cnode != -1:
                camino.append(self.stree[cnode][1])
                cnode = self.stree[cnode][2]
            
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
        if not self.resolviendo and not self.juego_terminado:
            self.resolviendo = True
            self.ficha_seleccionada = None
            self.movimientos_validos = []
            self.pista_mostrada = None
            
            # Buscar solución
            solucion = self.buscar_solucion(20)
            
            if solucion and len(solucion) > 1:
                self.solucion_pasos = solucion[1:]  # Saltar el estado actual
                self.mensaje_resolucion = f"Solución encontrada ({len(self.solucion_pasos)} movimientos)"
                print(f"Solución encontrada con {len(self.solucion_pasos)} movimientos")
                
                self.paso_solucion_actual = 0
                self.tiempo_ultimo_paso = time.time()
            else:
                self.mensaje_resolucion = "No se encontró solución completa"
                print("No se encontró solución completa")
                self.resolviendo = False
    
    def actualizar_resolucion_automatica(self):
        """Actualiza la resolución automática paso a paso"""
        if self.resolviendo and self.solucion_pasos and time.time() - self.tiempo_ultimo_paso > 1.0:
            if self.paso_solucion_actual < len(self.solucion_pasos):
                # Aplicar el siguiente paso de la solución
                self.root = self.solucion_pasos[self.paso_solucion_actual].copy()
                self.movimientos_jugador += 1
                
                self.paso_solucion_actual += 1
                self.tiempo_ultimo_paso = time.time()
                
                if self.paso_solucion_actual >= len(self.solucion_pasos):
                    self.resolviendo = False
                    self.verificar_fin_juego()
            else:
                self.resolviendo = False
    
    def reiniciar_seleccion(self):
        """Reinicia el juego al modo de selección"""
        self.modo_seleccion = True
        self.posicion_inicial_vacia = None
        self.root = None
        self.stree = {0: [set(), None, -1]}
        self.nnodes = 1
        self.gnode = -100
        self.movimientos_jugador = 0
        self.start_time = None
        self.elapsed_time = 0
        self.juego_terminado = False
        self.ganado = False
        self.ficha_seleccionada = None
        self.movimientos_validos = []
        self.pista_mostrada = None
        self.solucion_pasos = []
        self.resolviendo = False
        self.mensaje_resolucion = ""

# Crear instancia del juego
juego = pegsolitaire(None)

# Configurar ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Peg Solitaire - Basado en 8-puzzle")

# Botones modernos
button_width, button_height = 150, 50
button_spacing = 20
button_y = 550

nuevo_btn = pygame.Rect((WIDTH - 4 * button_width - 3 * button_spacing) // 2, button_y, button_width, button_height)
pista_btn = pygame.Rect(nuevo_btn.right + button_spacing, button_y, button_width, button_height)
resolver_btn = pygame.Rect(pista_btn.right + button_spacing, button_y, button_width, button_height)
salir_btn = pygame.Rect(resolver_btn.right + button_spacing, button_y, button_width, button_height)

def obtener_posicion_desde_coord(x, y):
    """Convierte coordenadas de pantalla a posición del tablero"""
    for pos, (px, py) in POSITIONS.items():
        if ((x - px) ** 2 + (y - py) ** 2) ** 0.5 <= 35:
            return pos
    return None

def dibujar_boton_moderno(rect, color, texto, hover=False, activo=True):
    """Dibuja un botón con estilo moderno"""
    if not activo:
        color = (color[0] // 3, color[1] // 3, color[2] // 3)
    elif hover:
        color = tuple(min(c + 30, 255) for c in color)
    
    pygame.draw.rect(screen, color, rect, border_radius=25)
    border_color = tuple(min(c + 40, 255) for c in color)
    pygame.draw.rect(screen, border_color, rect, width=2, border_radius=25)
    
    text_color = WHITE if activo else (120, 120, 120)
    button_text = FONT_LIGHT.render(texto, True, text_color)
    text_rect = button_text.get_rect(center=rect.center)
    screen.blit(button_text, text_rect)

def dibujar_peg_moderno(x, y, radio, tiene_ficha, estado, pos_num):
    """Dibuja una ficha con el estilo moderno"""
    if tiene_ficha:
        if estado == 'selected':
            pygame.draw.circle(screen, SELECT_RING, (x, y), radio + 8, 4)
        elif estado == 'valid_move':
            pygame.draw.circle(screen, VALID_RING, (x, y), radio + 8, 4)
        elif estado == 'hint_from':
            pygame.draw.circle(screen, LIGHT_RING, (x, y), radio + 5, 3)
            pygame.draw.circle(screen, BLUE_HINT, (x, y), radio)
            return
        elif estado == 'hint_over':
            pulse = int(5 + 3 * abs(pygame.time.get_ticks() / 300 % 2 - 1))
            pygame.draw.circle(screen, BLUE_HINT, (x, y), radio + pulse, 3)
        
        pygame.draw.circle(screen, LIGHT_RING, (x, y), radio + 5, 3)
        pygame.draw.circle(screen, YELLOW_PEG, (x, y), radio)
        
    else:
        if estado == 'hint_to':
            pygame.draw.circle(screen, BLUE_HINT, (x, y), radio + 5, 4)
        elif estado == 'valid_move':
            pygame.draw.circle(screen, VALID_RING, (x, y), radio + 8, 5)
        
        pygame.draw.circle(screen, LIGHT_RING, (x, y), radio + 5, 3)
        pygame.draw.circle(screen, DARK_HOLE, (x, y), radio)

def dibujar_tablero():
    """Dibuja el tablero con el diseño moderno"""
    screen.fill(DARK_BG)
    
    if juego.modo_seleccion:
        title = "Selecciona posición inicial"
        color_title = WHITE
    elif juego.juego_terminado:
        if juego.ganado:
            title = "¡PERFECTO!"
            color_title = VALID_RING
        else:
            title = "Juego Terminado"
            color_title = RED
    elif juego.resolviendo:
        title = "Resolviendo..."
        color_title = BLUE_HINT
    else:
        title = "Peg Solitaire"
        color_title = WHITE
    
    title_text = FONT_LARGE.render(title, True, color_title)
    title_rect = title_text.get_rect(center=(WIDTH // 2, 60))
    screen.blit(title_text, title_rect)
    
    if juego.mensaje_resolucion and juego.resolviendo:
        msg_text = FONT_LIGHT.render(juego.mensaje_resolucion, True, BLUE_HINT)
        msg_rect = msg_text.get_rect(center=(WIDTH // 2, 100))
        screen.blit(msg_text, msg_rect)
    
    destinos_validos = juego.obtener_destinos_validos() if juego.ficha_seleccionada else []
    
    for pos in range(1, 16):
        x, y = POSITIONS[pos]
        tiene_ficha = not juego.modo_seleccion and juego.root and juego.root[pos] == 1
        
        estado = 'normal'
        
        if juego.modo_seleccion:
            tiene_ficha = True
        elif juego.pista_mostrada:
            desde, sobre, hasta = juego.pista_mostrada
            if pos == desde:
                estado = 'hint_from'
            elif pos == sobre:
                estado = 'hint_over'
            elif pos == hasta:
                estado = 'hint_to'
        elif juego.ficha_seleccionada == pos:
            estado = 'selected'
        elif pos in destinos_validos:
            estado = 'valid_move'
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if ((mouse_x - x) ** 2 + (mouse_y - y) ** 2) ** 0.5 <= 35:
            juego.hover_pos = pos
        
        dibujar_peg_moderno(x, y, 25, tiene_ficha, estado, pos)
    
    if not juego.modo_seleccion:
        info_y = 620
        if juego.root:
            fichas_restantes = sum(1 for i in range(1, 16) if juego.root[i] == 1)
            
            moves_text = FONT_MEDIUM.render(f"Movimientos: {juego.movimientos_jugador}", True, WHITE)
            screen.blit(moves_text, (50, info_y))
            
            pegs_text = FONT_MEDIUM.render(f"Fichas: {fichas_restantes}", True, WHITE)
            screen.blit(pegs_text, (300, info_y))
            
            if juego.start_time and not juego.juego_terminado:
                juego.elapsed_time = time.time() - juego.start_time
            
            minutes = int(juego.elapsed_time // 60)
            seconds = int(juego.elapsed_time % 60)
            time_text = FONT_MEDIUM.render(f"Tiempo: {minutes:02d}:{seconds:02d}", True, WHITE)
            screen.blit(time_text, (550, info_y))
        
        if juego.ficha_seleccionada and destinos_validos:
            instruccion = f"Haz clic en una posición verde ({len(destinos_validos)} disponibles)"
        elif juego.ficha_seleccionada and not destinos_validos:
            instruccion = "Esta ficha no puede moverse - selecciona otra"
        elif not juego.juego_terminado and not juego.resolviendo:
            instruccion = "Haz clic en una ficha amarilla para seleccionarla"
        else:
            instruccion = ""
        
        if instruccion:
            inst_text = FONT_LIGHT.render(instruccion, True, (200, 200, 200))
            inst_rect = inst_text.get_rect(center=(WIDTH // 2, 500))
            screen.blit(inst_text, inst_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        
        dibujar_boton_moderno(nuevo_btn, (70, 130, 180), "Nuevo", nuevo_btn.collidepoint(mouse_pos))
        
        pista_activo = not juego.resolviendo and not juego.juego_terminado
        dibujar_boton_moderno(pista_btn, (255, 152, 0), "Pista", 
                            pista_btn.collidepoint(mouse_pos), pista_activo)
        
        resolver_activo = not juego.resolviendo and not juego.juego_terminado
        dibujar_boton_moderno(resolver_btn, (156, 39, 176), "Resolver",
                            resolver_btn.collidepoint(mouse_pos), resolver_activo)
        
        dibujar_boton_moderno(salir_btn, (244, 67, 54), "Salir", salir_btn.collidepoint(mouse_pos))

# Bucle principal
running = True
clock = pygame.time.Clock()

print("=" * 60)
print("         PEG SOLITAIRE - BASADO EN 8-PUZZLE")
print("=" * 60)
print("OBJETIVO: Eliminar todas las fichas excepto una")
print("REGLAS: Salta sobre una ficha adyacente a un espacio vacío")
print("=" * 60)
print("INSTRUCCIONES:")
print("1. Haz clic en una posición para comenzar (será la posición vacía)")
print("2. Selecciona fichas y muévelas a posiciones válidas (verdes)")
print("3. Usa 'Pista' para obtener ayuda")
print("4. Usa 'Resolver' para ver la solución usando el algoritmo de 8-puzzle")
print("=" * 60)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            
            if juego.modo_seleccion:
                pos_clickeada = obtener_posicion_desde_coord(x, y)
                if pos_clickeada:
                    juego.establecer_posicion_inicial(pos_clickeada)
                    print(f"\nPosición inicial vacía: {pos_clickeada}")
                    print("¡Juego iniciado!")
            
            else:
                if nuevo_btn.collidepoint(x, y):
                    juego.reiniciar_seleccion()
                    print("\nSelecciona nueva posición inicial")
                
                elif pista_btn.collidepoint(x, y) and not juego.resolviendo and not juego.juego_terminado:
                    pista = juego.obtener_pista()
                    if pista:
                        juego.pista_mostrada = pista
                        print(f"\nPista: Mover ficha {pista[0]} a posición {pista[2]}")
                    else:
                        print("\nNo hay pistas disponibles")
                
                elif resolver_btn.collidepoint(x, y) and not juego.resolviendo and not juego.juego_terminado:
                    print("\nBuscando solución con algoritmo de 8-puzzle...")
                    juego.resolver_automaticamente()
                
                elif salir_btn.collidepoint(x, y):
                    print("\n¡Gracias por jugar!")
                    running = False
                
                else:
                    pos_clickeada = obtener_posicion_desde_coord(x, y)
                    if pos_clickeada and not juego.resolviendo and not juego.juego_terminado:
                        juego.pista_mostrada = None
                        
                        if juego.ficha_seleccionada is None:
                            if juego.root[pos_clickeada] == 1:
                                juego.ficha_seleccionada = pos_clickeada
                                juego.movimientos_validos = juego.obtener_movimientos_desde_posicion(pos_clickeada)
                                if juego.movimientos_validos:
                                    print(f"\nFicha {pos_clickeada} seleccionada")
                                else:
                                    print(f"\nLa ficha {pos_clickeada} no puede moverse")
                        else:
                            if pos_clickeada == juego.ficha_seleccionada:
                                juego.ficha_seleccionada = None
                                juego.movimientos_validos = []
                                print("\nFicha deseleccionada")
                            elif juego.root[pos_clickeada] == 1:
                                juego.ficha_seleccionada = pos_clickeada
                                juego.movimientos_validos = juego.obtener_movimientos_desde_posicion(pos_clickeada)
                                if juego.movimientos_validos:
                                    print(f"\nFicha {pos_clickeada} seleccionada")
                                else:
                                    print(f"\nLa ficha {pos_clickeada} no puede moverse")
                            else:
                                if juego.hacer_movimiento(juego.ficha_seleccionada, pos_clickeada):
                                    print(f"\nMovimiento: {juego.ficha_seleccionada} → {pos_clickeada}")
                                    juego.ficha_seleccionada = None
                                    juego.movimientos_validos = []
                                    
                                    fichas_restantes = sum(1 for i in range(1, 16) if juego.root[i] == 1)
                                    if fichas_restantes > 1:
                                        movimientos_disponibles = len(juego.genmoves(juego.root))
                                        print(f"Fichas restantes: {fichas_restantes}")
                                else:
                                    print("\nMovimiento no válido")
    
    if juego.resolviendo:
        juego.actualizar_resolucion_automatica()
    
    dibujar_tablero()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()