import sys
import time
from typing import List, Tuple, Set, Dict, Optional

class Comesolo:
    """
    Clase principal que implementa el juego Comesolo (Solitario de Clavijas)
    en modo consola, utilizando algoritmos de búsqueda similares al 8-puzzle.
    """
    
    def __init__(self, posicion_vacia: int = None):
        """
        Inicializa el juego con una posición vacía específica.
        
        Args:
            posicion_vacia (int): Posición inicial vacía (1-15). Si es None,
                                se pedirá al usuario.
        """
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
        
        # Estado del juego
        self.tablero = None
        self.posicion_vacia = posicion_vacia
        self.movimientos_realizados = 0
        self.tiempo_inicio = None
        self.tiempo_transcurrido = 0
        self.juego_terminado = False
        self.ganado = False
        
        # Sistema de resolución
        self.arbol_busqueda = {}
        self.nodo_numero = 0
        self.nodo_objetivo = -100
        self.solucion_pasos = []
        
        # Inicializar el juego
        if posicion_vacia is not None:
            self.inicializar_juego(posicion_vacia)
    
    def inicializar_juego(self, posicion_vacia: int):
        """
        Configura el juego con una posición inicial vacía.
        
        Args:
            posicion_vacia (int): Posición inicial vacía (1-15)
        """
        self.posicion_vacia = posicion_vacia
        
        # Estado inicial: todas las posiciones ocupadas excepto una vacía
        self.tablero = [1] * 16  # Índice 0 no se usa, posiciones 1-15
        self.tablero[posicion_vacia] = 0
        self.tablero[0] = -1  # Marcador para ignorar índice 0
        
        # Reiniciar contadores y estado del juego
        self.movimientos_realizados = 0
        self.tiempo_inicio = time.time()
        self.tiempo_transcurrido = 0
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
        print("        " + ("○" if tablero[1] == 0 else "●"))
        
        # Fila 2 (posiciones 2-3)
        print("       " + ("○ " if tablero[2] == 0 else "● ") + 
                    ("○" if tablero[3] == 0 else "●"))
        
        # Fila 3 (posiciones 4-6)
        print("      " + ("○ " if tablero[4] == 0 else "● ") + 
                    ("○ " if tablero[5] == 0 else "● ") + 
                    ("○" if tablero[6] == 0 else "●"))
        
        # Fila 4 (posiciones 7-10)
        print("     " + ("○ " if tablero[7] == 0 else "● ") + 
                ("○ " if tablero[8] == 0 else "● ") + 
                ("○ " if tablero[9] == 0 else "● ") + 
                ("○" if tablero[10] == 0 else "●"))
        
        # Fila 5 (posiciones 11-15)
        print("    " + ("○ " if tablero[11] == 0 else "● ") + 
                ("○ " if tablero[12] == 0 else "● ") + 
                ("○ " if tablero[13] == 0 else "● ") + 
                ("○ " if tablero[14] == 0 else "● ") + 
                ("○" if tablero[15] == 0 else "●"))
        
        # Mostrar información del juego si es el tablero actual
        if tablero == self.tablero:
            fichas_restantes = sum(1 for i in range(1, 16) if tablero[i] == 1)
            print(f"\n   Fichas restantes: {fichas_restantes}")
            print(f"   Movimientos realizados: {self.movimientos_realizados}")
            
            if self.tiempo_inicio and not self.juego_terminado:
                self.tiempo_transcurrido = time.time() - self.tiempo_inicio
            
            minutos = int(self.tiempo_transcurrido // 60)
            segundos = int(self.tiempo_transcurrido % 60)
            print(f"   Tiempo: {minutos:02d}:{segundos:02d}")
            
            # Mostrar ejemplo del tablero con números
            if self.movimientos_realizados == 0:
                print(f"\n   EJEMPLO: Posición {self.posicion_vacia} está vacía (○)")
    
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
    
    def obtener_movimientos_desde_posicion(self, posicion: int) -> List[Tuple[int, int, int]]:
        """
        Obtiene todos los movimientos posibles desde una posición específica.
        
        Args:
            posicion (int): Posición desde la que se quiere mover
            
        Returns:
            List[Tuple[int, int, int]]: Lista de movimientos (desde, sobre, hasta)
        """
        movimientos = []
        
        # Verificar que haya una ficha en la posición
        if self.tablero and self.tablero[posicion] == 1:
            # Revisar todos los movimientos posibles desde esta posición
            for sobre, hasta in self.movimientos_posibles.get(posicion, []):
                # Verificar si el movimiento es válido
                if self.tablero[sobre] == 1 and self.tablero[hasta] == 0:
                    movimientos.append((posicion, sobre, hasta))
                    
        return movimientos
    
    def hacer_movimiento(self, desde: int, hasta: int) -> bool:
        """
        Realiza un movimiento si es válido.
        
        Args:
            desde (int): Posición de origen
            hasta (int): Posición de destino
            
        Returns:
            bool: True si el movimiento fue válido y se realizó, False en caso contrario
        """
        if self.juego_terminado:
            print("El juego ya ha terminado. Inicia uno nuevo.")
            return False
        
        print(f"\n🎯 INTENTANDO MOVIMIENTO: Ficha {desde} → Posición {hasta}")
        
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
            
            print(f"✅ MOVIMIENTO VÁLIDO:")
            print(f"   • Ficha {mov_desde} se mueve a posición {mov_hasta}")
            print(f"   • Elimina ficha {mov_sobre}")
            
            # Realizar el movimiento
            self.tablero[mov_desde] = 0  # Quitar ficha original
            self.tablero[mov_sobre] = 0   # Eliminar ficha saltada
            self.tablero[mov_hasta] = 1   # Colocar ficha en destino
            
            self.movimientos_realizados += 1
            self.verificar_fin_juego()
            
            # Mostrar estado del tablero
            fichas_restantes = sum(1 for i in range(1, 16) if self.tablero[i] == 1)
            print(f"   • Fichas restantes: {fichas_restantes}")
            
            return True
        else:
            print(f"❌ MOVIMIENTO NO VÁLIDO: No existe ruta de {desde} a {hasta}")
            if movimientos_validos:
                print("   Movimientos válidos desde esta posición:")
                for mov_desde, mov_sobre, mov_hasta in movimientos_validos:
                    print(f"   • Saltar ficha {mov_sobre} → posición {mov_hasta}")
            else:
                print("   No hay movimientos válidos desde esta posición.")
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
            self.tiempo_transcurrido = time.time() - self.tiempo_inicio
            posicion_final = next(i for i in range(1, 16) if self.tablero[i] == 1)
            print(f"\n🎉 ¡FELICIDADES! ¡GANASTE!")
            print(f"   • Ficha final en posición: {posicion_final}")
            print(f"   • Movimientos realizados: {self.movimientos_realizados}")
            print(f"   • Tiempo: {int(self.tiempo_transcurrido//60):02d}:{int(self.tiempo_transcurrido%60):02d}")
            return
        
        # Verificar si hay movimientos disponibles
        movimientos_disponibles = self.generar_movimientos(self.tablero)
        if not movimientos_disponibles:
            self.juego_terminado = True
            self.ganado = False
            self.tiempo_transcurrido = time.time() - self.tiempo_inicio
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
                print(f'🎯 Objetivo encontrado a profundidad {profundidad_actual}')
        
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
            List[List[int]: Secuencia de estados que llevan a la solución
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
            
        print(f"\n🤖 INICIANDO RESOLUCIÓN AUTOMÁTICA...")
        print("-" * 40)
        
        # Buscar solución desde el estado actual
        solucion = self.buscar_solucion(25)
        
        if solucion and len(solucion) > 1:
            # Verificar que sea solución completa
            estado_final = solucion[-1]
            fichas_finales = sum(1 for i in range(1, 16) if estado_final[i] == 1)
            
            if fichas_finales == 1:
                print(f"✅ Solución encontrada con {len(solucion) - 1} movimientos")
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
                
                # Mostrar todos los tableros de la solución
                print(f"\n🎯 VISUALIZACIÓN DE LA SOLUCIÓN:")
                for i, estado in enumerate(solucion):
                    self.dibujar_tablero_solucion(estado, i, len(solucion)-1)
                    if i < len(solucion) - 1:
                        input("   Presiona Enter para ver el siguiente paso...")
                
                # Aplicar la solución al juego actual
                aplicar = input("\n¿Aplicar esta solución al juego? (s/n): ").lower()
                if aplicar == 's':
                    self.tablero = estado_final.copy()
                    self.movimientos_realizados += len(solucion) - 1
                    self.verificar_fin_juego()
            else:
                print(f"⚠️  Solución parcial: quedarán {fichas_finales} fichas")
        else:
            print("❌ No se encontró solución desde el estado actual")
    
    def verificar_solucion_existe(self):
        """Verifica si existe una solución para la posición inicial actual."""
        if not self.tablero:
            print("Primero inicializa el juego con una posición vacía.")
            return
            
        print("\n🔍 VERIFICANDO SI EXISTE SOLUCIÓN...")
        print("-" * 40)
        
        # Buscar solución completa
        solucion = self.buscar_solucion(25)
        
        if solucion and len(solucion) > 1:
            # Verificar que la última posición tenga solo una ficha
            estado_final = solucion[-1]
            fichas_finales = sum(1 for i in range(1, 16) if estado_final[i] == 1)
            
            if fichas_finales == 1:
                print(f"✅ ¡SOLUCIÓN EXISTE!")
                print(f"   Número de movimientos necesarios: {len(solucion) - 1}")
                posicion_final = next(i for i in range(1, 16) if estado_final[i] == 1)
                print(f"   Ficha final quedará en posición: {posicion_final}")
                
                # Mostrar el tablero final de la solución
                print(f"\n🎯 TABLERO FINAL DE LA SOLUCIÓN:")
                self.dibujar_tablero(estado_final)
            else:
                print(f"❌ NO HAY SOLUCIÓN PERFECTA")
                print(f"   Mejor resultado posible: {fichas_finales} fichas restantes")
        else:
            print(f"❌ NO HAY SOLUCIÓN desde la posición inicial {self.posicion_vacia}")
        
        print("-" * 40)


def mostrar_menu_principal():
    """Muestra el menú principal del juego."""
    print("\n" + "="*60)
    print("         COMESOLO (SOLITARIO DE CLAVIJAS) - CONSOLA")
    print("="*60)
    print("🎯 OBJETIVO: Eliminar todas las fichas excepto una")
    print("📋 REGLAS: Salta sobre una ficha adyacente a un espacio vacío")
    print("="*60)
    print("1. Iniciar nuevo juego")
    print("2. Verificar si existe solución")
    print("3. Resolver automáticamente")
    print("4. Mostrar tablero actual")
    print("5. Realizar movimiento")
    print("6. Salir")
    print("="*60)


def main():
    """Función principal del juego."""
    juego = Comesolo()
    
    while True:
        mostrar_menu_principal()
        
        try:
            opcion = int(input("Selecciona una opción: "))
        except ValueError:
            print("Por favor, ingresa un número válido.")
            continue
        
        if opcion == 1:
            # Iniciar nuevo juego
            try:
                pos_vacia = int(input("Ingresa la posición inicial vacía (1-15): "))
                if not 1 <= pos_vacia <= 15:
                    print("La posición debe estar entre 1 and 15.")
                    continue
                juego.inicializar_juego(pos_vacia)
                juego.dibujar_tablero()
            except ValueError:
                print("Por favor, ingresa un número válido.")
        
        elif opcion == 2:
            # Verificar si existe solución
            if juego.tablero is None:
                print("Primero inicia un juego con la opción 1.")
            else:
                juego.verificar_solucion_existe()
        
        elif opcion == 3:
            # Resolver automáticamente
            if juego.tablero is None:
                print("Primero inicia un juego con la opción 1.")
            else:
                juego.resolver_automaticamente()
                juego.dibujar_tablero()
        
        elif opcion == 4:
            # Mostrar tablero actual
            juego.dibujar_tablero()
        
        elif opcion == 5:
            # Realizar movimiento
            if juego.tablero is None:
                print("Primero inicia un juego con la opción 1.")
            elif juego.juego_terminado:
                print("El juego ya ha terminado. Inicia uno nuevo.")
            else:
                try:
                    desde = int(input("Posición de la ficha a mover: "))
                    hasta = int(input("Posición destino: "))
                    
                    if not 1 <= desde <= 15 or not 1 <= hasta <= 15:
                        print("Las posiciones deben estar entre 1 y 15.")
                        continue
                        
                    if juego.hacer_movimiento(desde, hasta):
                        juego.dibujar_tablero()
                except ValueError:
                    print("Por favor, ingresa números válidos.")
        
        elif opcion == 6:
            # Salir
            print("¡Gracias por jugar!")
            break
        
        else:
            print("Opción no válida. Por favor, selecciona una opción del 1 al 6.")


if __name__ == "__main__":
    main()