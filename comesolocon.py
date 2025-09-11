import sys
from typing import List, Tuple
import time

class Comesolo:
    """
    Clase principal que implementa el juego Comesolo (Solitario de Clavijas)
    en modo consola, utilizando algoritmos de búsqueda similares al 8-puzzle.
    """
    
    def __init__(self, posicion_vacia: str = None):
        """
        Inicializa el juego con una posición vacía específica.
        
        Args:
            posicion_vacia (str): Posición inicial vacía (ej: 'a1', 'b3', 'c5'). Si es None,
                                se pedirá al usuario.
        """
        # Mapeo de posiciones a números (1-15)
        self.posiciones = {
            'a1': 1, 'a2': 2, 'b2': 3, 'a3': 4, 'b3': 5, 'c3': 6,
            'a4': 7, 'b4': 8, 'c4': 9, 'd4': 10, 'a5': 11, 'b5': 12,
            'c5': 13, 'd5': 14, 'e5': 15
        }
        
        # Mapeo inverso de números a posiciones
        self.numeros_a_posiciones = {v: k for k, v in self.posiciones.items()}
        
        # Movimientos posibles - cada entrada representa (ficha_saltada, destino)
        self.movimientos_posibles = {
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
        
        # Reiniciar completamente el estado del juego
        self.reiniciar_completamente()
        
        # Si se proporciona posición inicial, inicializar el juego
        if posicion_vacia is not None:
            self.inicializar_juego(posicion_vacia)
    
    def reiniciar_completamente(self):
        """Reinicia completamente todos los datos del juego a su estado inicial."""
        # Estado del juego
        self.tablero = None
        self.posicion_vacia = None
        self.movimientos_realizados = 0
        self.juego_terminado = False
        self.ganado = False
        
        # Sistema de resolución
        self.arbol_busqueda = {}
        self.nodo_numero = 0
        self.nodo_objetivo = -100
        self.solucion_pasos = []
    
    def convertir_a_numero(self, posicion: str) -> int:
        """Convierte una posición en formato letra+número a número interno (1-15)."""
        if posicion.lower() in self.posiciones:
            return self.posiciones[posicion.lower()]
        raise ValueError(f"Posición '{posicion}' no válida")
    
    def convertir_a_posicion(self, numero: int) -> str:
        """Convierte un número interno (1-15) a formato letra+número."""
        if 1 <= numero <= 15:
            return self.numeros_a_posiciones[numero]
        raise ValueError(f"Número '{numero}' fuera de rango")
    
    def inicializar_juego(self, posicion_vacia: str):
        """
        Configura el juego con una posición inicial vacía.
        
        Args:
            posicion_vacia (str): Posición inicial vacía (ej: 'a1', 'b3', 'c5')
        """
        self.posicion_vacia = posicion_vacia
        pos_vacia_num = self.convertir_a_numero(posicion_vacia)
        
        # Estado inicial: todas las posiciones ocupadas excepto una vacía
        self.tablero = [1] * 16  # Índice 0 no se usa, posiciones 1-15
        self.tablero[pos_vacia_num] = 0
        self.tablero[0] = -1  # Marcador para ignorar índice 0
        
        # Reiniciar contadores y estado del juego
        self.movimientos_realizados = 0
        self.juego_terminado = False
        self.ganado = False
        
        # Reiniciar sistema de resolución
        self.arbol_busqueda = {0: [set(), self.tablero.copy(), -1]}
        self.nodo_numero = 1
        self.nodo_objetivo = -100
        self.solucion_pasos = []
        
        print(f"\n{'='*60}")
        print(f"JUEGO INICIADO - Posición inicial vacía: {posicion_vacia}")
        print(f"{'='*60}")
    
    def dibujar_tablero(self, tablero=None):
        """
        Dibuja el tablero actual en la consola con formato triangular equilátero.
        
        Args:
            tablero (List[int]): Tablero a dibujar. Si es None, usa self.tablero
        """
        if tablero is None:
            tablero = self.tablero
            
        if tablero is None:
            print("Tablero no inicializado. Primero selecciona una posición vacía.")
            return
        
        print("\n   TABLERO:")
        print("   " + "=" * 35)
        
        # Dibujar el tablero triangular con formato de triángulo equilátero
        # Fila 1 (posición 1)
        print("        " + ("○" if tablero[1] == 0 else "●") + "       |||        a1")
        
        # Fila 2 (posiciones 2-3)
        print("       " + ("○ " if tablero[2] == 0 else "● ") + 
                    ("○" if tablero[3] == 0 else "●") + "      |||       a2 b2")
        
        # Fila 3 (posiciones 4-6)
        print("      " + ("○ " if tablero[4] == 0 else "● ") + 
                    ("○ " if tablero[5] == 0 else "● ") + 
                    ("○" if tablero[6] == 0 else "●") + "     |||      a3 b3 c3")
        
        # Fila 4 (posiciones 7-10)
        print("     " + ("○ " if tablero[7] == 0 else "● ") + 
                ("○ " if tablero[8] == 0 else "● ") + 
                ("○ " if tablero[9] == 0 else "● ") + 
                ("○" if tablero[10] == 0 else "●") + "    |||     a4 b4 c4 d4")
        
        # Fila 5 (posiciones 11-15)
        print("    " + ("○ " if tablero[11] == 0 else "● ") + 
                ("○ " if tablero[12] == 0 else "● ") + 
                ("○ " if tablero[13] == 0 else "● ") + 
                ("○ " if tablero[14] == 0 else "● ") + 
                ("○" if tablero[15] == 0 else "●") + "   |||    a5 b5 c5 d5 e5")
        
        # Mostrar información del juego si es el tablero actual
        if tablero == self.tablero:
            fichas_restantes = sum(1 for i in range(1, 16) if tablero[i] == 1)
            print(f"\n   Fichas restantes: {fichas_restantes}")
            print(f"   Movimientos realizados: {self.movimientos_realizados}")
    
    def generar_movimientos(self, tablero: List[int]) -> List[List[int]]:
        """
        Genera todos los movimientos posibles desde un estado dado del tablero.
        
        Args:
            tablero (List[int]): Estado actual del tablero
            
        Returns:
            List[List[int]]: Lista de nuevos estados posibles
        """
        lista_movimientos = []
        
        # Para cada posición en el tablero
        for desde in range(1, 16):
            if tablero[desde] == 1:  # Si hay ficha en esta posición
                # Revisar todos los movimientos posibles desde esta posición
                for sobre, hasta in self.movimientos_posibles.get(desde, []):
                    # Verificar si el movimiento es válido
                    if tablero[sobre] == 1 and tablero[hasta] == 0:
                        # Crear nuevo estado aplicando el movimiento
                        nuevo_estado = tablero.copy()
                        nuevo_estado[desde] = 0  # Quitar ficha de origen
                        nuevo_estado[sobre] = 0  # Eliminar ficha saltada
                        nuevo_estado[hasta] = 1  # Colocar ficha en destino
                        lista_movimientos.append(nuevo_estado)
                        
        return lista_movimientos
    
    def obtener_movimientos_desde_posicion(self, posicion: str) -> List[Tuple[str, str, str]]:
        """
        Obtiene todos los movimientos posibles desde una posición específica.
        
        Args:
            posicion (str): Posición desde la que se quiere mover (ej: 'a1', 'b3')
            
        Returns:
            List[Tuple[str, str, str]]: Lista de movimientos (desde, sobre, hasta)
        """
        movimientos = []
        
        # Convertir posición a número interno
        try:
            pos_num = self.convertir_a_numero(posicion)
        except ValueError:
            return []
        
        # Verificar que haya una ficha en la posición
        if self.tablero and self.tablero[pos_num] == 1:
            # Revisar todos los movimientos posibles desde esta posición
            for sobre_num, hasta_num in self.movimientos_posibles.get(pos_num, []):
                # Verificar si el movimiento es válido
                if self.tablero[sobre_num] == 1 and self.tablero[hasta_num] == 0:
                    desde_str = self.convertir_a_posicion(pos_num)
                    sobre_str = self.convertir_a_posicion(sobre_num)
                    hasta_str = self.convertir_a_posicion(hasta_num)
                    movimientos.append((desde_str, sobre_str, hasta_str))
                    
        return movimientos
    
    def hacer_movimiento(self, desde: str, hasta: str) -> bool:
        """
        Realiza un movimiento si es válido.
        
        Args:
            desde (str): Posición de origen (ej: 'a1', 'b3')
            hasta (str): Posición de destino (ej: 'a1', 'b3')
            
        Returns:
            bool: True si el movimiento fue válido y se realizó, False en caso contrario
        """
        if self.juego_terminado:
            print("El juego ya ha terminado. Inicia uno nuevo.")
            return False
        
        print(f"\nINTENTANDO MOVIMIENTO: Ficha {desde} → Posición {hasta}")
        
        # Convertir posiciones a números internos
        try:
            desde_num = self.convertir_a_numero(desde)
            hasta_num = self.convertir_a_numero(hasta)
        except ValueError as e:
            print(f"Error: {e}")
            return False
        
        # Obtener movimientos válidos desde la posición
        movimientos_validos = self.obtener_movimientos_desde_posicion(desde)
        
        # Verificar si el movimiento está en la lista de movimientos válidos
        movimiento_valido = None
        for mov_desde, mov_sobre, mov_hasta in movimientos_validos:
            if mov_desde == desde and mov_hasta == hasta:
                movimiento_valido = (mov_desde, mov_sobre, mov_hasta)
                break
        
        if movimiento_valido:
            mov_desde, mov_sobre, mov_hasta = movimiento_valido
            
            print(f"MOVIMIENTO VÁLIDO:")
            print(f"   • Ficha {mov_desde} se mueve a posición {mov_hasta}")
            print(f"   • Elimina ficha {mov_sobre}")
            
            # Convertir a números para realizar el movimiento
            mov_desde_num = self.convertir_a_numero(mov_desde)
            mov_sobre_num = self.convertir_a_numero(mov_sobre)
            mov_hasta_num = self.convertir_a_numero(mov_hasta)
            
            # Realizar el movimiento
            self.tablero[mov_desde_num] = 0  # Quitar ficha original
            self.tablero[mov_sobre_num] = 0   # Eliminar ficha saltada
            self.tablero[mov_hasta_num] = 1   # Colocar ficha en destino
            
            self.movimientos_realizados += 1
            
            # Mostrar el tablero actualizado después del movimiento
            print("\nTABLERO ACTUALIZADO:")
            self.dibujar_tablero()
            
            self.verificar_fin_juego()
            
            return True
        else:
            print(f"MOVIMIENTO NO VÁLIDO: No existe ruta de {desde} a {hasta}")
            return False
    
    def verificar_fin_juego(self):
        """Verifica si el juego ha terminado (victoria o sin movimientos)."""
        if not self.tablero:
            return
            
        # Contar fichas restantes
        fichas_restantes = sum(1 for i in range(1, 16) if self.tablero[i] == 1)
        
        # Verificar victoria (solo una ficha)
        if fichas_restantes == 1:
            self.juego_terminado = True
            self.ganado = True
            posicion_final_num = next(i for i in range(1, 16) if self.tablero[i] == 1)
            posicion_final = self.convertir_a_posicion(posicion_final_num)
            print(f"\n¡FELICIDADES! ¡GANASTE!")
            print(f"   • Ficha final en posición: {posicion_final}")
            print(f"   • Movimientos realizados: {self.movimientos_realizados}")
            return
        
        # Verificar si hay movimientos disponibles
        movimientos_disponibles = self.generar_movimientos(self.tablero)
        if not movimientos_disponibles:
            self.juego_terminado = True
            self.ganado = False
            print(f"\n🔚 JUEGO TERMINADO")
            print(f"   • Fichas restantes: {fichas_restantes}")
            print(f"   • Movimientos realizados: {self.movimientos_realizados}")
            print(f"   • No hay más movimientos posibles")
    
    def generar_arbol(self, profundidad: int = 20) -> int:
        """
        Genera el árbol de búsqueda hasta la profundidad especificada usando BFS.
        
        Args:
            profundidad (int): Profundidad máxima de búsqueda
            
        Returns:
            int: ID del nodo objetivo si se encuentra, -100 en caso contrario
        """
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
                        if self.nodo_numero > 15000:  # Límite de seguridad
                            break
            
            # Agregar nuevos nodos al árbol principal
            for key in arbol_nuevo:
                self.arbol_busqueda[key] = arbol_nuevo[key]
                
            profundidad_actual += 1
            if objetivo_encontrado:
                print(f'Objetivo encontrado a profundidad {profundidad_actual}')
        
        return self.nodo_objetivo
    
    def imprimir_solucion(self) -> List[List[int]]:
        """
        Reconstruye la solución desde el nodo objetivo hasta la raíz.
        
        Returns:
            List[List[int]]: Lista de estados desde el inicio hasta la solución
        """
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
    
    def buscar_solucion(self, max_profundidad: int = 20) -> List[List[int]]:
        """
        Busca una solución usando BFS.
        
        Args:
            max_profundidad (int): Profundidad máxima de búsqueda
            
        Returns:
            List[List[int]]: Secuencia de estados que llevan a la solución
        """
        # Reiniciar el árbol de búsqueda con el estado actual
        self.arbol_busqueda = {0: [set(), self.tablero.copy(), -1]}
        self.nodo_numero = 1
        self.nodo_objetivo = -100
        
        # Generar árbol hasta la profundidad máxima
        self.generar_arbol(max_profundidad)
        
        # Devolver la solución si se encontró
        return self.imprimir_solucion()
    
    def dibujar_tablero_solucion(self, estado: List[int], paso: int, total_pasos: int):
        """
        Dibuja un tablero específico de la solución con información del paso.
        
        Args:
            estado (List[int]): Estado del tablero a dibujar
            paso (int): Número del paso actual
            total_pasos (int): Total de pasos en la solución
        """
        print(f"\n{'='*60}")
        print(f"PASO {paso}/{total_pasos}")
        print(f"{'='*60}")
        self.dibujar_tablero(estado)
        
        # Mostrar información adicional
        fichas_restantes = sum(1 for i in range(1, 16) if estado[i] == 1)
        print(f"   Fichas restantes: {fichas_restantes}")
    
    def resolver_automaticamente(self):
        """Inicia la resolución automática usando el árbol de búsqueda."""
        if not self.tablero:
            print("Primero inicializa el juego con una posición vacía.")
            return
            
        if self.juego_terminado:
            print("El juego ya ha terminado. Inicia uno nuevo.")
            return
            
        print(f"\nINICIANDO RESOLUCIÓN AUTOMÁTICA...")
        print("-" * 40)
        
        # Buscar solución desde el estado actual
        solucion = self.buscar_solucion(25)
        
        if solucion and len(solucion) > 1:
            # Verificar que sea solución completa
            estado_final = solucion[-1]
            fichas_finales = sum(1 for i in range(1, 16) if estado_final[i] == 1)
            
            if fichas_finales == 1:
                print(f"Solución encontrada con {len(solucion) - 1} movimientos")
                print("\nSECUENCIA DE SOLUCIÓN:")
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
                        desde_str = self.convertir_a_posicion(desde)
                        sobre_str = self.convertir_a_posicion(sobre)
                        hasta_str = self.convertir_a_posicion(hasta)
                        print(f"   Paso {i}: Ficha {desde_str} salta sobre ficha {sobre_str} → posición {hasta_str}")
                
                # Mostrar todos los tableros de la solución automáticamente
                print(f"\nVISUALIZACIÓN DE LA SOLUCIÓN:")
                for i, estado in enumerate(solucion):
                    self.dibujar_tablero_solucion(estado, i, len(solucion)-1)
                    if i < len(solucion) - 1:
                        # Pausa breve entre pasos en lugar de esperar entrada
                        time.sleep(1.5)
                
                # Aplicar la solución al juego actual automáticamente
                self.tablero = estado_final.copy()
                self.movimientos_realizados += len(solucion) - 1
                self.verificar_fin_juego()
                
                # Pausa antes de regresar al menú principal
                input("\nPresiona Enter para regresar al menú principal...")
                return True
            else:
                print(f"Solución parcial: quedarán {fichas_finales} fichas")
        else:
            print("No se encontró solución desde el estado actual")
        
        return False
    
    def verificar_solucion_existe(self):
        """Verifica si existe una solución para la posición inicial actual."""
        if not self.tablero:
            print("Primero inicializa el juego con una posición vacía.")
            return
            
        print("\nVERIFICANDO SI EXISTE SOLUCIÓN...")
        print("-" * 40)
        
        # Buscar solución completa
        solucion = self.buscar_solucion(25)
        
        if solucion and len(solucion) > 1:
            # Verificar que la última posición tenga solo una ficha
            estado_final = solucion[-1]
            fichas_finales = sum(1 for i in range(1, 16) if estado_final[i] == 1)
            
            if fichas_finales == 1:
                print(f"¡SOLUCIÓN EXISTE!")
                print(f"   Número de movimientos necesarios: {len(solucion) - 1}")
                posicion_final_num = next(i for i in range(1, 16) if estado_final[i] == 1)
                posicion_final = self.convertir_a_posicion(posicion_final_num)
                print(f"   Ficha final quedará en posición: {posicion_final}")
                
                # Mostrar el tablero final de la solución
                print(f"\nTABLERO FINAL DE LA SOLUCIÓN:")
                self.dibujar_tablero(estado_final)
            else:
                print(f"NO HAY SOLUCIÓN PERFECTA")
                print(f"   Mejor resultado posible: {fichas_finales} fichas restantes")
        else:
            print(f"NO HAY SOLUCIÓN desde la posición inicial {self.posicion_vacia}")
        
        print("-" * 40)


def mostrar_menu_principal():
    """Muestra el menú principal del juego."""
    print("\n" + "="*60)
    print("         COMESOLO (SOLITARIO DE CLAVIJAS) - CONSOLA")
    print("="*60)
    print("OBJETIVO: Eliminar todas las fichas excepto una")
    print("REGLAS: Salta sobre una ficha adyacente a un espacio vacío")
    print("="*60)
    print("1. Iniciar nuevo juego")
    print("2. Verificar si existe solución")
    print("3. Resolver automáticamente")
    print("4. Mostrar tablero actual")
    print("5. Realizar movimiento")
    print("6. Salir")
    print("0. Mostrar menú nuevamente")
    print("="*60)


def main():
    """Función principal del juego."""
    juego = None
    
    while True:
        # Mostrar el menú principal
        mostrar_menu_principal()
        
        try:
            opcion = input("\nSelecciona una opción: ").strip()
            
            if opcion == '0':
                continue
                
            opcion = int(opcion)
        except ValueError:
            print("Por favor, ingresa un número válido.")
            continue
        
        if opcion == 1:
            # Iniciar nuevo juego - siempre crea una nueva instancia limpia
            try:
                pos_vacia = input("Ingresa la posición inicial vacía (ej: a1, b3, c5): ").lower()
                posiciones_validas = ['a1', 'a2', 'b2', 'a3', 'b3', 'c3', 
                                     'a4', 'b4', 'c4', 'd4', 'a5', 'b5', 
                                     'c5', 'd5', 'e5']
                
                if pos_vacia not in posiciones_validas:
                    print("Posición no válida. Posiciones válidas:", ", ".join(posiciones_validas))
                    continue
                    
                # IMPORTANTE: Crear nueva instancia completamente limpia
                juego = Comesolo(pos_vacia)
                juego.dibujar_tablero()
                
                # Continuar jugando hasta que el juego termine
                while not juego.juego_terminado:
                    accion = input("\nPresiona Enter para continuar jugando, '0' para volver al menú: ").strip()
                    if accion == '0':
                        break
                    else:
                        # Pedir movimiento
                        try:
                            desde = input("Posición de la ficha a mover (ej: a1, b3) o '0' para menú: ").lower()
                            if desde == '0':
                                break
                                
                            hasta = input("Posición destino (ej: a1, b3): ").lower()
                            
                            if juego.hacer_movimiento(desde, hasta):
                                # El tablero ya se muestra dentro de hacer_movimiento()
                                pass
                        except Exception as e:
                            print(f"Error: {e}")
                
                # Si el juego terminó, reiniciar completamente para el siguiente juego
                if juego.juego_terminado:
                    print(f"\n{'='*60}")
                    if juego.ganado:
                        print("¡JUEGO COMPLETADO CON ÉXITO!")
                    else:
                        print("JUEGO TERMINADO - SIN MOVIMIENTOS DISPONIBLES")
                    print("Regresando al menú principal...")
                    print("(Toda la información del juego se ha reiniciado)")
                    print(f"{'='*60}")
                    
                    # IMPORTANTE: Reiniciar completamente el juego para empezar limpio
                    juego = None
                    input("\nPresiona Enter para continuar...")
                
            except Exception as e:
                print(f"Error: {e}")
        
        elif opcion == 2:
            # Verificar si existe solución
            if juego is None or juego.tablero is None:
                print("Primero inicia un juego con la opción 1.")
            else:
                juego.verificar_solucion_existe()
        
        elif opcion == 3:
            # Resolver automáticamente
            if juego is None or juego.tablero is None:
                print("Primero inicia un juego con la opción 1.")
            else:
                if juego.resolver_automaticamente():
                    # Si se resolvió con éxito, el juego terminó
                    print(f"\n{'='*60}")
                    print("¡JUEGO RESUELTO AUTOMÁTICAMENTE!")
                    print("Regresando al menú principal...")
                    print("(Toda la información del juego se ha reiniciado)")
                    print(f"{'='*60}")
                    
                    # IMPORTANTE: Reiniciar completamente el juego
                    juego = None
        
        elif opcion == 4:
            # Mostrar tablero actual
            if juego is None or juego.tablero is None:
                print("Primero inicia un juego con la opción 1.")
            else:
                juego.dibujar_tablero()
        
        elif opcion == 5:
            # Realizar movimiento
            if juego is None or juego.tablero is None:
                print("Primero inicia un juego con la opción 1.")
            elif juego.juego_terminado:
                print("El juego ya ha terminado. Inicia uno nuevo.")
            else:
                try:
                    desde = input("Posición de la ficha a mover (ej: a1, b3): ").lower()
                    hasta = input("Posición destino (ej: a1, b3): ").lower()
                    
                    if juego.hacer_movimiento(desde, hasta):
                        # El tablero ya se muestra dentro de hacer_movimiento()
                        pass
                        
                    # Si el juego terminó después del movimiento, reiniciar completamente
                    if juego.juego_terminado:
                        print(f"\n{'='*60}")
                        if juego.ganado:
                            print("¡JUEGO COMPLETADO CON ÉXITO!")
                        else:
                            print("JUEGO TERMINADO - SIN MOVIMIENTOS DISPONIBLES")
                        print("Regresando al menú principal...")
                        print("(Toda la información del juego se ha reiniciado)")
                        print(f"{'='*60}")
                        
                        # IMPORTANTE: Reiniciar completamente el juego
                        juego = None
                        input("\nPresiona Enter para continuar...")
                        
                except Exception as e:
                    print(f"Error: {e}")
        
        elif opcion == 6:
            # Salir
            print("¡Gracias por jugar!")
            break
        
        else:
            print("Opción no válida. Por favor, selecciona una opción del 0 al 6.")


if __name__ == "__main__":
    main()