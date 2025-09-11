import time # Para pausar el programa cuando muestra la solución paso a paso
from typing import List, Tuple # Para decir qué tipo de datos usan las funciones

# Clase principal que implementa el juego Comesolo.
class Comesolo:
    
    # Inicializa el juego con una posición vacía
    def __init__(self, posicion_vacia: str = None):

        # Diccionario que convierte posiciones del tablero (a1, b3, etc.) a números internos (1-15)
        self.posiciones = {
            'a1': 1, 'a2': 2, 'b2': 3, 'a3': 4, 'b3': 5, 'c3': 6,
            'a4': 7, 'b4': 8, 'c4': 9, 'd4': 10, 'a5': 11, 'b5': 12,
            'c5': 13, 'd5': 14, 'e5': 15
        }
        
        # Diccionario inverso que convierte números internos (1-15) a posiciones (a1, b3, etc.)
        self.numeros_a_posiciones = {v: k for k, v in self.posiciones.items()}
        
        # Define los movimientos válidos desde cada posición
        # Formato: posicion_origen: [(ficha_que_salta, posicion_destino)]
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
        
        # Limpia completamente todos los datos del juego
        self.reiniciar_completamente()
        
        # Si se da una posición inicial, configura el juego automáticamente
        if posicion_vacia is not None:
            self.inicializar_juego(posicion_vacia)

    # Reinicia completamente todos los datos del juego a su estado inicial
    def reiniciar_completamente(self):
        # Variables que controlan el estado actual del juego
        self.tablero = None  
        self.posicion_vacia = None  
        self.movimientos_realizados = 0  
        self.juego_terminado = False  
        self.ganado = False  
        
        # Variables para el algoritmo de búsqueda 
        self.arbol_busqueda = {}  # Diccionario que almacena todos los estados explorados
        self.nodo_numero = 0  # Contador que asigna ID único a cada estado
        self.nodo_objetivo = -100  # ID del estado objetivo (cuando solo queda 1 ficha)
        self.solucion_pasos = []  # Lista que almacena la secuencia de pasos de la solución
    
    # Convierte una posición en formato letra+número a su número interno (1-15)
    def convertir_a_numero(self, posicion: str) -> int:
        # Busca la posición en el diccionario
        if posicion.lower() in self.posiciones:
            return self.posiciones[posicion.lower()]
        raise ValueError(f"Posición '{posicion}' no válida")
    
    # Convierte un número interno (1-15) a su posición en formato letra+número
    def convertir_a_posicion(self, numero: int) -> str:
        # Verifica que el número esté en el rango válido
        if 1 <= numero <= 15:
            return self.numeros_a_posiciones[numero]
        raise ValueError(f"Número '{numero}' fuera de rango")
    
    # Configura el juego con una posición inicial vacía.
    def inicializar_juego(self, posicion_vacia: str):
        self.posicion_vacia = posicion_vacia

        # Convierte la posición vacía a número interno
        pos_vacia_num = self.convertir_a_numero(posicion_vacia)
        
        # Se crea el tablero inicial: todas las posiciones ocupadas (1) excepto la vacía (0)
        self.tablero = [1] * 16  # Se usa índices 1-15, el índice 0 no se usa
        self.tablero[pos_vacia_num] = 0  # Marca la posición vacía
        self.tablero[0] = -1  # Ignorar el índice 0
        
        # Reinicia todas las variables del juego
        self.movimientos_realizados = 0
        self.juego_terminado = False
        self.ganado = False
        
        # Se configura el árbol de búsqueda con el estado inicial
        # Formato: {id: [conjunto_hijos, estado_tablero, id_padre]}
        self.arbol_busqueda = {0: [set(), self.tablero.copy(), -1]}
        self.nodo_numero = 1  
        self.nodo_objetivo = -100  
        self.solucion_pasos = []
        
        print(f"\n{'='*60}")
        print(f"JUEGO INICIADO - Posición inicial vacía: {posicion_vacia}")
        print(f"{'='*60}")
    
    # Se dibuja el tablero en la consola con formato triangular
    def dibujar_tablero(self, tablero=None):

        # Si no se especifica tablero, usa el tablero actual del juego
        if tablero is None:
            tablero = self.tablero
            
        # Verifica que el tablero esté inicializado
        if tablero is None:
            print("Tablero no inicializado. Primero selecciona una posición vacía.")
            return
        
        print("\n   TABLERO:")
        print("   " + "=" * 35)
        
        # Se dibuja el tablero triangular fila por fila
        # ○ = posición vacía, ● = ficha presente
        
        # Fila 1: solo la posición a1
        print("        " + ("○" if tablero[1] == 0 else "●") + "       |||        a1")
        
        # Fila 2: posiciones a2 y b2
        print("       " + ("○ " if tablero[2] == 0 else "● ") + 
                    ("○" if tablero[3] == 0 else "●") + "      |||       a2 b2")
        
        # Fila 3: posiciones a3, b3 y c3
        print("      " + ("○ " if tablero[4] == 0 else "● ") + 
                    ("○ " if tablero[5] == 0 else "● ") + 
                    ("○" if tablero[6] == 0 else "●") + "     |||      a3 b3 c3")
        
        # Fila 4: posiciones a4, b4, c4 y d4
        print("     " + ("○ " if tablero[7] == 0 else "● ") + 
                ("○ " if tablero[8] == 0 else "● ") + 
                ("○ " if tablero[9] == 0 else "● ") + 
                ("○" if tablero[10] == 0 else "●") + "    |||     a4 b4 c4 d4")
        
        # Fila 5: posiciones a5, b5, c5, d5 y e5
        print("    " + ("○ " if tablero[11] == 0 else "● ") + 
                ("○ " if tablero[12] == 0 else "● ") + 
                ("○ " if tablero[13] == 0 else "● ") + 
                ("○ " if tablero[14] == 0 else "● ") + 
                ("○" if tablero[15] == 0 else "●") + "   |||    a5 b5 c5 d5 e5")
        
        if tablero == self.tablero:
            # Se cuenta cuántas fichas quedan en el tablero
            fichas_restantes = sum(1 for i in range(1, 16) if tablero[i] == 1)
            print(f"\n   Fichas restantes: {fichas_restantes}")
            print(f"   Movimientos realizados: {self.movimientos_realizados}")
    
    # Genera todos los movimientos posibles desde un estado dado del tablero.
    def generar_movimientos(self, tablero: List[int]) -> List[List[int]]:

        lista_movimientos = []
        
        # Revisa cada posición del tablero buscando fichas que se puedan mover
        for desde in range(1, 16):
            if tablero[desde] == 1:
                # Consulta todos los movimientos posibles desde esta posición
                for sobre, hasta in self.movimientos_posibles.get(desde, []):
                    if tablero[sobre] == 1 and tablero[hasta] == 0:
                        # Crea un nuevo estado aplicando este movimiento
                        nuevo_estado = tablero.copy()
                        nuevo_estado[desde] = 0  # Quita la ficha de la posición origen
                        nuevo_estado[sobre] = 0  # Elimina la ficha que fue saltada
                        nuevo_estado[hasta] = 1  # Coloca la ficha en la posición destino
                        lista_movimientos.append(nuevo_estado)
                        
        return lista_movimientos
    
    # Obtiene todos los movimientos posibles desde una posición específica
    def obtener_movimientos_desde_posicion(self, posicion: str) -> List[Tuple[str, str, str]]:
        movimientos = []
        # Se intenta convertir la posición a número interno
        try:
            pos_num = self.convertir_a_numero(posicion)
        except ValueError:
            return []  # Retorna lista vacía si la posición no es válida
        
        # Verifica que haya una ficha en esa posición
        if self.tablero and self.tablero[pos_num] == 1:
            # Revisa todos los movimientos posibles desde esta posición
            for sobre_num, hasta_num in self.movimientos_posibles.get(pos_num, []):
                # Verifica si el movimiento es válido en el estado actual
                if self.tablero[sobre_num] == 1 and self.tablero[hasta_num] == 0:
                    # Convierte los números de vuelta a posiciones legibles
                    desde_str = self.convertir_a_posicion(pos_num)
                    sobre_str = self.convertir_a_posicion(sobre_num)
                    hasta_str = self.convertir_a_posicion(hasta_num)
                    movimientos.append((desde_str, sobre_str, hasta_str))
                    
        return movimientos
    
    # Realiza un movimiento si es válido
    def hacer_movimiento(self, desde: str, hasta: str) -> bool:
        # Verifica que el juego no haya terminado
        if self.juego_terminado:
            print("El juego ya ha terminado. Inicia uno nuevo.")
            return False 
        
        print(f"\nINTENTANDO MOVIMIENTO: Ficha {desde} → Posición {hasta}")
        
        # Obtiene todos los movimientos válidos desde la posición de origen
        movimientos_validos = self.obtener_movimientos_desde_posicion(desde)
        
        # Busca si el movimiento solicitado está en la lista de movimientos válidos
        movimiento_valido = None
        for mov_desde, mov_sobre, mov_hasta in movimientos_validos:
            if mov_desde == desde and mov_hasta == hasta:
                movimiento_valido = (mov_desde, mov_sobre, mov_hasta)
                break
        
        # Si encontró el movimiento válido, lo ejecuta
        if movimiento_valido:
            mov_desde, mov_sobre, mov_hasta = movimiento_valido
            
            print(f"MOVIMIENTO VÁLIDO:")
            print(f"   • Ficha {mov_desde} se mueve a posición {mov_hasta}")
            print(f"   • Elimina ficha {mov_sobre}")
            
            # Convierte las posiciones a números para actualizar el tablero
            try:
                mov_desde_num = self.convertir_a_numero(mov_desde)
                mov_sobre_num = self.convertir_a_numero(mov_sobre)
                mov_hasta_num = self.convertir_a_numero(mov_hasta)
            except ValueError as e:
                print(f"Error en conversión: {e}")
                return False
            
            # Ejecuta el movimiento actualizando el tablero
            self.tablero[mov_desde_num] = 0  # Quita la ficha original
            self.tablero[mov_sobre_num] = 0   # Elimina la ficha saltada
            self.tablero[mov_hasta_num] = 1   # Coloca la ficha en su nueva posición
            
            # Incrementa el contador de movimientos
            self.movimientos_realizados += 1
            
            # Muestra el tablero actualizado
            print("\nTABLERO ACTUALIZADO:")
            self.dibujar_tablero()
            
            # Verifica si el juego terminó después de este movimiento
            self.verificar_fin_juego()
            
            return True
        else:
            print(f"MOVIMIENTO NO VÁLIDO: No existe ruta de {desde} a {hasta}")
            return False
    
    # Verifica si el juego ha terminado (victoria o sin movimientos)
    def verificar_fin_juego(self):
        # Verifica que el tablero esté inicializado
        if not self.tablero:
            return
        # Cuenta cuántas fichas quedan en el tablero
        fichas_restantes = sum(1 for i in range(1, 16) if self.tablero[i] == 1)
        
        # Verifica condición de victoria: solo queda una ficha
        if fichas_restantes == 1:
            self.juego_terminado = True
            self.ganado = True
            # Encuentra dónde está la ficha ganadora
            posicion_final_num = next(i for i in range(1, 16) if self.tablero[i] == 1)
            posicion_final = self.convertir_a_posicion(posicion_final_num)
            print(f"\n¡FELICIDADES! ¡GANASTE!")
            print(f"   • Ficha final en posición: {posicion_final}")
            print(f"   • Movimientos realizados: {self.movimientos_realizados}")
            return
        
        # Verifica si hay movimientos disponibles (si no hay, el juego termina sin victoria)
        movimientos_disponibles = self.generar_movimientos(self.tablero)
        if not movimientos_disponibles:
            self.juego_terminado = True
            self.ganado = False
            print(f"\nJUEGO TERMINADO")
            print(f"   • Fichas restantes: {fichas_restantes}")
            print(f"   • Movimientos realizados: {self.movimientos_realizados}")
            print(f"   • No hay más movimientos posibles")
    
    # Genera el árbol de búsqueda usando BFS hasta una profundidad dada usando BFS. este algoritmo es idéntico al del 8-puzzle visto en clase
    def generar_arbol(self, profundidad: int = 20) -> int:

        profundidad_actual = 0
        self.nodo_objetivo = -100  # Inicializa como "no encontrado"
        objetivo_encontrado = False
        
        # Expansión nivel por nivel 
        while profundidad_actual < profundidad and not objetivo_encontrado:
            arbol_nuevo = dict()  # Almacena los nuevos nodos de este nivel
            
            # Expande cada nodo en el nivel actual que no haya sido expandido
            for id in self.arbol_busqueda:
                # Si el nodo no tiene hijos (len() < 1) y no hemos encontrado objetivo
                if len(self.arbol_busqueda[id][0]) < 1 and not objetivo_encontrado:
                    # Genera todos los movimientos posibles desde este estado
                    lista_movimientos = self.generar_movimientos(self.arbol_busqueda[id][1])
                    
                    # Crea un nodo hijo para cada movimiento posible
                    for movimiento in lista_movimientos:
                        # Evita ciclos: no regresa al estado del nodo padre
                        if profundidad_actual > 0 and movimiento == self.arbol_busqueda[self.arbol_busqueda[id][2]][1]:
                            continue
                            
                        # Agrega el nuevo nodo al árbol
                        self.arbol_busqueda[id][0].add(self.nodo_numero)  # Agrega hijo al padre
                        arbol_nuevo[self.nodo_numero] = [set(), movimiento, id]  # [hijos, estado, padre]
                        
                        # Verifica si este estado es el objetivo (solo una ficha)
                        if sum(1 for i in range(1, 16) if movimiento[i] == 1) == 1:
                            self.nodo_objetivo = self.nodo_numero
                            objetivo_encontrado = True
                            break
                            
                        # Prepara el siguiente número de nodo
                        self.nodo_numero += 1
                        # Límite de seguridad para evitar que el programa use demasiada memoria
                        if self.nodo_numero > 15000:
                            break
            
            # Integra los nuevos nodos al árbol principal
            for key in arbol_nuevo:
                self.arbol_busqueda[key] = arbol_nuevo[key]
                
            profundidad_actual += 1
            # Si encontró el objetivo, informa en qué profundidad
            if objetivo_encontrado:
                print(f'Objetivo encontrado a profundidad {profundidad_actual}')
        
        return self.nodo_objetivo
    
    # Reconstruye e imprime la solución desde el nodo objetivo hasta la raíz es igual al del 8-puzzle que vimos en clase
    def imprimir_solucion(self) -> List[List[int]]:

        # Verifica que se haya encontrado una solución
        if self.nodo_objetivo < -1:
            return []
            
        solucion = []
        nodo_actual = self.nodo_objetivo
        
        # Reconstruye el camino desde el objetivo hasta la raíz siguiendo los padres
        while nodo_actual != -1:
            solucion.append(self.arbol_busqueda[nodo_actual][1])  # Agrega el estado
            nodo_actual = self.arbol_busqueda[nodo_actual][2]     # Va al padre

        # Invierte la lista para tener la secuencia correcta (inicio → objetivo)
        solucion.reverse()
        return solucion
    
    # Busca una solución usando BFS.
    def buscar_solucion(self, max_profundidad: int = 20) -> List[List[int]]:
        # Reinicia el árbol de búsqueda con el estado actual como raíz
        self.arbol_busqueda = {0: [set(), self.tablero.copy(), -1]}
        self.nodo_numero = 1
        self.nodo_objetivo = -100
        
        # Ejecuta el algoritmo de búsqueda
        self.generar_arbol(max_profundidad)
        
        # Retorna la solución reconstruida (o lista vacía si no se encontró)
        return self.imprimir_solucion()
    
    # Dibuja un tablero específico de la solución con información del paso
    def dibujar_tablero_solucion(self, estado: List[int], paso: int, total_pasos: int):
        print(f"\n{'='*60}")
        print(f"PASO {paso}/{total_pasos}")
        print(f"{'='*60}")
        self.dibujar_tablero(estado)
        
        # Calcula y muestra información adicional del paso
        fichas_restantes = sum(1 for i in range(1, 16) if estado[i] == 1)
        print(f"   Fichas restantes: {fichas_restantes}")
    
    # Realiza la resolución automática del juego usando el árbol de búsqueda
    def resolver_automaticamente(self):
        # Verifica que el juego esté inicializado
        if not self.tablero:
            print("Primero inicializa el juego con una posición vacía.")
            return
            
        # Verifica que el juego no haya terminado ya
        if self.juego_terminado:
            print("El juego ya ha terminado. Inicia uno nuevo.")
            return
            
        print(f"\nINICIANDO RESOLUCIÓN AUTOMÁTICA...")
        print("-" * 40)
        
        # Busca una solución desde el estado actual
        solucion = self.buscar_solucion(25)  # Busca hasta profundidad 25
        
        # Si encontró una solución y tiene más de un estado
        if solucion and len(solucion) > 1:
            # Verifica que sea una solución completa (solo una ficha al final)
            estado_final = solucion[-1]
            fichas_finales = sum(1 for i in range(1, 16) if estado_final[i] == 1)
            
            if fichas_finales == 1:
                print(f"Solución encontrada con {len(solucion) - 1} movimientos")
                print("\nSECUENCIA DE SOLUCIÓN:")
                print("-" * 40)
                
                # Analiza cada paso de la solución para mostrar los movimientos
                for i in range(1, len(solucion)):
                    estado_anterior = solucion[i-1]
                    estado_actual = solucion[i]
                    
                    # Encuentra qué movimiento se hizo comparando los dos estados
                    desde = sobre = hasta = None
                    
                    for pos in range(1, 16):
                        # Si una posición tenía ficha y ahora no la tiene
                        if estado_anterior[pos] == 1 and estado_actual[pos] == 0:
                            if desde is None:
                                desde = pos  # Primera posición vacía = origen
                            else:
                                sobre = pos  # Segunda posición vacía = ficha saltada
                        # Si una posición estaba vacía y ahora tiene ficha
                        elif estado_anterior[pos] == 0 and estado_actual[pos] == 1:
                            hasta = pos  # Posición que recibió la ficha = destino
                    
                    # Si encontró las tres posiciones, muestra el movimiento
                    if desde and sobre and hasta:
                        desde_str = self.convertir_a_posicion(desde)
                        sobre_str = self.convertir_a_posicion(sobre)
                        hasta_str = self.convertir_a_posicion(hasta)
                        print(f"   Paso {i}: Ficha {desde_str} salta sobre ficha {sobre_str} → posición {hasta_str}")
                
                # Muestra la visualización paso a paso de la solución
                print(f"\nVISUALIZACIÓN DE LA SOLUCIÓN:")
                for i, estado in enumerate(solucion):
                    self.dibujar_tablero_solucion(estado, i, len(solucion)-1)
                    if i < len(solucion) - 1:
                        # Pausa breve entre pasos para que se pueda seguir la secuencia
                        time.sleep(1.5)
                
                # Se actualiza el juego al estado final (ganado)
                self.tablero = estado_final.copy()
                self.movimientos_realizados += len(solucion) - 1
                self.verificar_fin_juego()
                
                # Espera confirmación del usuario antes de continuar
                input("\nPresiona Enter para regresar al menú principal...")
                return True
            else:
                print(f"Solución parcial: quedarán {fichas_finales} fichas")
        else:
            print("No se encontró solución desde el estado actual")
        
        return False
    
    # Verifica si existe una solución desde la posición inicial actual
    def verificar_solucion_existe(self):
        # Verifica que el juego esté inicializado
        if not self.tablero:
            print("Primero inicializa el juego con una posición vacía.")
            return
            
        print("\nVERIFICANDO SI EXISTE SOLUCIÓN...")
        print("-" * 40)
        
        # Busca una solución completa desde el estado actual
        solucion = self.buscar_solucion(25)
        
        # Analiza el resultado de la búsqueda
        if solucion and len(solucion) > 1:
            # Verifica que el último estado tenga solo una ficha
            estado_final = solucion[-1]
            fichas_finales = sum(1 for i in range(1, 16) if estado_final[i] == 1)
            
            if fichas_finales == 1:
                print(f"¡SOLUCIÓN EXISTE!")
                print(f"   Número de movimientos necesarios: {len(solucion) - 1}")
                # Encuentra dónde quedaría la ficha final
                posicion_final_num = next(i for i in range(1, 16) if estado_final[i] == 1)
                posicion_final = self.convertir_a_posicion(posicion_final_num)
                print(f"   Ficha final quedará en posición: {posicion_final}")
                
                # Muestra cómo se vería el tablero final
                print(f"\nTABLERO FINAL DE LA SOLUCIÓN:")
                self.dibujar_tablero(estado_final)
            else:
                print(f"NO HAY SOLUCIÓN PERFECTA")
                print(f"   Mejor resultado posible: {fichas_finales} fichas restantes")
        else:
            print(f"NO HAY SOLUCIÓN desde la posición inicial {self.posicion_vacia}")
        
        print("-" * 40)

# muestra el menú principal del juego
def mostrar_menu_principal():
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

# Función principal del juego
def main():
    # Variable que almacena la instancia actual del juego (None = no hay juego activo)
    juego = None

    # Bucle principal del programa que mantiene el menú activo
    while True:
        # Muestra el menú de opciones al usuario
        mostrar_menu_principal()
        
        # Intenta leer la opción del usuario y convertirla a número
        try:
            opcion = input("\nSelecciona una opción: ").strip()
            
            # Si ingresa 0, vuelve a mostrar el menú
            if opcion == '0':
                continue
                
            opcion = int(opcion)  # Convierte a entero para comparar
        except ValueError:
            print("Por favor, ingresa un número válido.")
            continue
        
        if opcion == 1:
            # OPCIÓN 1: Iniciar nuevo juego - siempre crea una nueva instancia limpia
            try:
                # Pide al usuario la posición inicial vacía
                pos_vacia = input("Ingresa la posición inicial vacía (ej: a1, b3, c5): ").lower()
                
                # Lista de todas las posiciones válidas en el tablero
                posiciones_validas = ['a1', 'a2', 'b2', 'a3', 'b3', 'c3', 
                                     'a4', 'b4', 'c4', 'd4', 'a5', 'b5', 
                                     'c5', 'd5', 'e5']
                
                # Verifica que la posición ingresada sea válida
                if pos_vacia not in posiciones_validas:
                    print("Posición no válida. Posiciones válidas:", ", ".join(posiciones_validas))
                    continue
                    
                # IMPORTANTE: Crea una nueva instancia completamente limpia del juego
                juego = Comesolo(pos_vacia)
                juego.dibujar_tablero()
                
                # Bucle de juego: continúa hasta que el juego termine
                while not juego.juego_terminado:
                    accion = input("\nPresiona Enter para continuar jugando, '0' para volver al menú: ").strip()
                    if accion == '0':
                        break  # Sale del bucle de juego y vuelve al menú principal
                    else:
                        # Pide al usuario que haga un movimiento
                        try:
                            desde = input("Posición de la ficha a mover (ej: a1, b3) o '0' para menú: ").lower()
                            if desde == '0':
                                break
                                
                            hasta = input("Posición destino (ej: a1, b3): ").lower()
                            
                            # Intenta hacer el movimiento
                            if juego.hacer_movimiento(desde, hasta):
                                # El tablero ya se muestra dentro de hacer_movimiento()
                                pass
                        except Exception as e:
                            print(f"Error: {e}")
                
                # Si el juego terminó (por victoria o sin movimientos), limpia todo
                if juego.juego_terminado:
                    print(f"\n{'='*60}")
                    if juego.ganado:
                        print("¡JUEGO COMPLETADO CON ÉXITO!")
                    else:
                        print("JUEGO TERMINADO - SIN MOVIMIENTOS DISPONIBLES")
                    print("Regresando al menú principal...")
                    print("(Toda la información del juego se ha reiniciado)")
                    print(f"{'='*60}")
                    
                    # Reinicia completamente el juego para empezar un nuevo juego
                    juego = None
                    input("\nPresiona Enter para continuar...")
                
            except Exception as e:
                print(f"Error: {e}")
        
        elif opcion == 2:
            # OPCIÓN 2: Verificar si existe solución
            if juego is None or juego.tablero is None:
                print("Primero inicia un juego con la opción 1.")
            else:
                juego.verificar_solucion_existe()
        
        elif opcion == 3:
            # OPCIÓN 3: Resolver automáticamente
            if juego is None or juego.tablero is None:
                print("Primero inicia un juego con la opción 1.")
            else:
                # Si la resolución automática fue exitosa, el juego termina
                if juego.resolver_automaticamente():
                    print(f"\n{'='*60}")
                    print("¡JUEGO RESUELTO AUTOMÁTICAMENTE!")
                    print("Regresando al menú principal...")
                    print("(Toda la información del juego se ha reiniciado)")
                    print(f"{'='*60}")
                    
                    # Reinicia completamente el juego
                    juego = None
        
        elif opcion == 4:
            # OPCIÓN 4: Mostrar tablero actual
            if juego is None or juego.tablero is None:
                print("Primero inicia un juego con la opción 1.")
            else:
                juego.dibujar_tablero()
        
        elif opcion == 5:
            # OPCIÓN 5: Realizar un movimiento individual
            if juego is None or juego.tablero is None:
                print("Primero inicia un juego con la opción 1.")
            elif juego.juego_terminado:
                print("El juego ya ha terminado. Inicia uno nuevo.")
            else:
                try:
                    # Pide las posiciones de origen y destino
                    desde = input("Posición de la ficha a mover (ej: a1, b3): ").lower()
                    hasta = input("Posición destino (ej: a1, b3): ").lower()
                    
                    # Intenta hacer el movimiento
                    if juego.hacer_movimiento(desde, hasta):
                        # El tablero ya se muestra dentro de hacer_movimiento()
                        pass
                        
                    # Si el juego terminó después del movimiento, limpia todo
                    if juego.juego_terminado:
                        print(f"\n{'='*60}")
                        if juego.ganado:
                            print("¡JUEGO COMPLETADO CON ÉXITO!")
                        else:
                            print("JUEGO TERMINADO - SIN MOVIMIENTOS DISPONIBLES")
                        print("Regresando al menú principal...")
                        print("(Toda la información del juego se ha reiniciado)")
                        print(f"{'='*60}")
                        
                        # Reinicia completamente el juego
                        juego = None
                        input("\nPresiona Enter para continuar...")
                        
                except Exception as e:
                    print(f"Error: {e}")
        
        elif opcion == 6:
            # OPCIÓN 6: Salir del programa
            print("¡Gracias por jugar!")
            break
        
        else:
            print("Opción no válida. Por favor, selecciona una opción del 0 al 6.")

# Punto de entrada del programa
if __name__ == "__main__":
    main()