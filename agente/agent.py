from logic import KnowledgeBase, Literal
import random
from ml_model import get_or_train_model, predict_mode
class VacuumAgent:
    def __init__(self, width, height, start_x, start_y, max_battery=25):
        self.width = width
        self.height = height
        self.x = start_x
        self.y = start_y
        self.prev_x = start_x
        self.prev_y = start_y
        self.orientacion = "N"
        self.base = (start_x, start_y)
        
        self.visited = set()
        self.visited.add((start_x, start_y))
        
        self.kb = KnowledgeBase()
        
        self.max_battery = max_battery
        self.battery = max_battery
        self.mode = "EXPLORE" # Modos: EXPLORE, GO_CHARGE, GO_FINISH, PATROL
        self.path = []
        self.patrol_targets = set()
        self.known_dirt = set()
        self.ml_model = get_or_train_model()
        
        self._init_rules()

    def _init_rules(self):
        # Base is safe
        self.kb.add_fact(Literal(f"O_{self.x}_{self.y}").negate())

    def _get_valid_adjacents(self, x, y):
        adj = []
        if x > 0: adj.append((x-1, y))
        if x < self.width - 1: adj.append((x+1, y))
        if y > 0: adj.append((x, y-1))
        if y < self.height - 1: adj.append((x, y+1))
        return adj

    def perceive(self, percepts):
        sensor_frente = percepts.get("Obstaculo_Frente", False)
        sucio = percepts.get("Suciedad", False)
        
        fx, fy = self.x, self.y
        if self.orientacion == "N": fy += 1
        elif self.orientacion == "S": fy -= 1
        elif self.orientacion == "E": fx += 1
        elif self.orientacion == "W": fx -= 1
        
        o_lit = Literal(f"O_{fx}_{fy}")
        if sensor_frente:
            self.kb.update_fact(o_lit)
        else:
            if 0 <= fx < self.width and 0 <= fy < self.height:
                self.kb.update_fact(o_lit.negate())

        l_lit = Literal(f"L_{self.x}_{self.y}")
        if sucio:
            self.kb.update_fact(l_lit.negate())
            self.known_dirt.add((self.x, self.y))
        else:
            self.kb.update_fact(l_lit)
            if hasattr(self, 'known_dirt') and (self.x, self.y) in self.known_dirt:
                self.known_dirt.remove((self.x, self.y))

    def _bfs_path(self, start, goal):
        queue = [[start]]
        visited = set()
        visited.add(start)
        
        while queue:
            path = queue.pop(0)
            node = path[-1]
            
            if node == goal:
                return path[1:] # Exclude start node
                
            for nxt in self._get_valid_adjacents(*node):
                if nxt not in visited and (nxt in self.visited or nxt == goal):
                    visited.add(nxt)
                    new_path = list(path)
                    new_path.append(nxt)
                    queue.append(new_path)
        return []

    def _path_to_actions(self, path_coords, look_only_at_end=False):
        actions = []
        curr_x, curr_y = self.x, self.y
        curr_dir = self.orientacion
        dirs = ["N", "E", "S", "W"]
        
        for i, (nx, ny) in enumerate(path_coords):
            if nx == curr_x and ny == curr_y + 1: target_dir = "N"
            elif nx == curr_x and ny == curr_y - 1: target_dir = "S"
            elif nx == curr_x + 1 and ny == curr_y: target_dir = "E"
            elif nx == curr_x - 1 and ny == curr_y: target_dir = "W"
            else: continue
            
            while curr_dir != target_dir:
                idx = dirs.index(curr_dir)
                t_idx = dirs.index(target_dir)
                if (idx + 1) % 4 == t_idx:
                    actions.append("ROTAR_DER")
                    curr_dir = dirs[(idx + 1) % 4]
                elif (idx - 1) % 4 == t_idx:
                    actions.append("ROTAR_IZQ")
                    curr_dir = dirs[(idx - 1) % 4]
                elif (idx + 2) % 4 == t_idx:
                    actions.append("ROTAR_DER")
                    curr_dir = dirs[(idx + 1) % 4]
                    
            is_last = (i == len(path_coords) - 1)
            if not (is_last and look_only_at_end):
                actions.append(("MOVER", (nx, ny)))
                curr_x, curr_y = nx, ny
                
        return actions

    def _genetic_algorithm_tsp(self, start, targets):
        if not targets: return []
        if len(targets) == 1: return targets
        
        nodes = [start] + targets
        dist_cache = {}
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                d = len(self._bfs_path(nodes[i], nodes[j]))
                dist_cache[(nodes[i], nodes[j])] = d
                dist_cache[(nodes[j], nodes[i])] = d
                
        def route_distance(route):
            d = dist_cache.get((start, route[0]), 0)
            for i in range(len(route)-1):
                d += dist_cache.get((route[i], route[i+1]), 0)
            return d
            
        pop_size = max(10, min(50, len(targets) * 2))
        generations = 40
        
        # Seed 1: Ruta Voraz (Vecino más cercano) para un comportamiento más "barrido"
        nn_route = []
        unvisited = set(targets)
        curr = start
        while unvisited:
            closest = min(unvisited, key=lambda x: dist_cache.get((curr, x), float('inf')))
            nn_route.append(closest)
            unvisited.remove(closest)
            curr = closest
            
        population = [nn_route]
        for _ in range(pop_size - 1):
            ind = list(targets)
            random.shuffle(ind)
            population.append(ind)
            
        for gen in range(generations):
            population.sort(key=route_distance)
            next_pop = population[:pop_size//2]
            
            while len(next_pop) < pop_size:
                p1, p2 = random.sample(population[:pop_size//2], 2)
                start_cx = random.randint(0, len(targets)-2)
                end_cx = random.randint(start_cx+1, len(targets)-1)
                
                child = [None]*len(targets)
                child[start_cx:end_cx] = p1[start_cx:end_cx]
                
                p2_idx = 0
                for i in range(len(targets)):
                    if child[i] is None:
                        while p2[p2_idx] in child:
                            p2_idx += 1
                        child[i] = p2[p2_idx]
                        
                if random.random() < 0.2:
                    m1, m2 = random.sample(range(len(targets)), 2)
                    child[m1], child[m2] = child[m2], child[m1]
                    
                next_pop.append(child)
            population = next_pop
            
        population.sort(key=route_distance)
        return population[0]

    def think_and_act(self):
        explicacion_total = ""
        
        if self.x == self.base[0] and self.y == self.base[1] and self.mode == "GO_FINISH":
            return "TERMINAR", None, "He llegado a la base tras finalizar la tarea."
            
        # 1. Recargar si llegó a la base con batería baja
        if self.x == self.base[0] and self.y == self.base[1] and self.mode == "GO_CHARGE":
            self.battery = self.max_battery
            self.mode = getattr(self, 'prev_mode', 'EXPLORE')
            return "RECARGAR", None, "Batería recargada al 100%. Vuelvo a mi tarea anterior."

        # 2. Control por ML (Árbol de Decisión)
        path_coords = self._bfs_path((self.x, self.y), self.base)
        actions_to_base = self._path_to_actions(path_coords)
        cost_to_base = len(actions_to_base)
        
        battery_pct = self.battery / self.max_battery
        exp_done = 1 if self.mode == "GO_FINISH" or self.mode == "PATROL" else 0
        pat_done = 1 if not getattr(self, 'patrol_targets', set()) and not getattr(self, 'patrol_route', []) else 0
        
        predicted_mode = predict_mode(self.ml_model, battery_pct, cost_to_base, exp_done, pat_done)
        
        if predicted_mode == "GO_CHARGE" and self.mode in ["EXPLORE", "PATROL"] and (self.x, self.y) != self.base:
            self.prev_mode = self.mode
            self.mode = "GO_CHARGE"
            self.path = actions_to_base
            explicacion_total += f"[ÁRBOL DE DECISIÓN] Batería crítica detectada (Predicción ML). Aborto misión para ir a recargar.\n"

        # 3. Aspirar si está sucio
        if self.mode in ["EXPLORE", "PATROL"]:
            query_sucio = Literal(f"L_{self.x}_{self.y}").negate()
            is_dirty, expl = self.kb.entails(query_sucio)
            if is_dirty:
                self.kb.update_fact(Literal(f"L_{self.x}_{self.y}"))
                if hasattr(self, 'known_dirt') and (self.x, self.y) in self.known_dirt:
                    self.known_dirt.remove((self.x, self.y))
                self.battery -= 1
                explicacion_total += expl + f"\n[RAZONAMIENTO] Casilla ({self.x}, {self.y}) sucia. Decido ASPIRAR.\n"
                return "ASPIRAR", None, explicacion_total

        # 4. Seguir la ruta activa
        if self.path:
            action = self.path.pop(0)
            if action == "ROTAR_IZQ":
                dirs = ["N", "E", "S", "W"]
                self.orientacion = dirs[(dirs.index(self.orientacion) - 1) % 4]
                self.battery -= 1
                return "ROTAR_IZQ", None, explicacion_total + f"[RUTA] Rotando a la izquierda. Mirando a {self.orientacion}"
            elif action == "ROTAR_DER":
                dirs = ["N", "E", "S", "W"]
                self.orientacion = dirs[(dirs.index(self.orientacion) + 1) % 4]
                self.battery -= 1
                return "ROTAR_DER", None, explicacion_total + f"[RUTA] Rotando a la derecha. Mirando a {self.orientacion}"
            elif isinstance(action, tuple) and action[0] == "MOVER":
                next_pos = action[1]
                self.prev_x, self.prev_y = self.x, self.y
                self.x, self.y = next_pos
                self.visited.add((next_pos[0], next_pos[1]))
                if (self.x, self.y) in self.patrol_targets:
                    self.patrol_targets.remove((self.x, self.y))
                if hasattr(self, 'patrol_route') and (self.x, self.y) in self.patrol_route:
                    self.patrol_route.remove((self.x, self.y))
                self.battery -= 1
                explicacion_total += f"[RUTA] Avanzando a {next_pos}. Batería restante: {self.battery}."
                return "MOVER", next_pos, explicacion_total

        # 4.5. Buscar nuevo objetivo de patrulla
        if self.mode == "PATROL":
            if self.patrol_targets:
                explicacion_total += "[ALGORITMO GENÉTICO] Optimizando ruta de patrullaje (TSP)...\n"
                self.patrol_route = self._genetic_algorithm_tsp((self.x, self.y), list(self.patrol_targets))
                self.patrol_targets = set()
                
            if hasattr(self, 'patrol_route') and self.patrol_route:
                target = self.patrol_route.pop(0)
                path_coords = self._bfs_path((self.x, self.y), target)
                self.path = self._path_to_actions(path_coords)
                return self.think_and_act()
            else:
                self.mode = "GO_FINISH"
                path_coords = self._bfs_path((self.x, self.y), self.base)
                self.path = self._path_to_actions(path_coords)
                explicacion_total += "[PATRULLA FINALIZADA] Todas las casillas seguras patrulladas. Regresando a base.\n"
                
                if not self.path:
                    if (self.x, self.y) == self.base:
                        return "TERMINAR", None, explicacion_total + " Ya estoy en la base."
                else:
                    return self.think_and_act()

        # 4.8. Ir a suciedad conocida antes de explorar nuevas fronteras
        if self.mode == "EXPLORE" and getattr(self, 'known_dirt', set()):
            dirt_targets = []
            for d in self.known_dirt:
                path_coords = self._bfs_path((self.x, self.y), d)
                if path_coords:
                    dirt_targets.append((d, len(path_coords), path_coords))
            
            if dirt_targets:
                dirt_targets.sort(key=lambda x: x[1])
                target, dist, path_coords = dirt_targets[0]
                self.path = self._path_to_actions(path_coords)
                explicacion_total += f"\n[RECORDATORIO] Tengo suciedad pendiente en {target}. Voy a limpiarla antes de seguir explorando.\n"
                return self.think_and_act()

        # 5. Buscar nueva frontera segura si terminamos la tarea anterior
        if self.mode == "EXPLORE":
            frontier = set()
            for vx, vy in self.visited:
                for nx, ny in self._get_valid_adjacents(vx, vy):
                    if (nx, ny) not in self.visited:
                        frontier.add((nx, ny))
            
            safe_frontiers = []
            unknown_frontiers = []
            
            for fx, fy in frontier:
                query_safe = Literal(f"O_{fx}_{fy}").negate()
                is_safe, expl = self.kb.entails(query_safe)
                
                query_obstacle = Literal(f"O_{fx}_{fy}")
                is_obs, _ = self.kb.entails(query_obstacle)
                
                if is_safe:
                    dist = len(self._bfs_path((self.x, self.y), (fx, fy)))
                    safe_frontiers.append(((fx, fy), dist, expl))
                elif not is_obs:
                    dist = len(self._bfs_path((self.x, self.y), (fx, fy)))
                    unknown_frontiers.append(((fx, fy), dist))

            if safe_frontiers:
                safe_frontiers.sort(key=lambda x: x[1])
                target, dist, expl = safe_frontiers[0]
                
                path_coords = self._bfs_path((self.x, self.y), target)
                self.path = self._path_to_actions(path_coords)
                explicacion_total += f"\n[EXPLORACIÓN SEGURA] Frontera más cercana en {target}. Generando ruta.\n{expl}"
                return self.think_and_act()
            elif unknown_frontiers:
                unknown_frontiers.sort(key=lambda x: x[1])
                target, dist = unknown_frontiers[0]
                
                path_coords = self._bfs_path((self.x, self.y), target)
                self.path = self._path_to_actions(path_coords, look_only_at_end=True)
                explicacion_total += f"\n[INCERTIDUMBRE] Frontera dudosa en {target}. Iré a mirarla.\n"
                
                if not self.path:
                    return "ESPERAR", None, "Mirando a la frontera..."
                return self.think_and_act()
            else:
                self.mode = "GO_FINISH"
                path_coords = self._bfs_path((self.x, self.y), self.base)
                self.path = self._path_to_actions(path_coords)
                explicacion_total += "[EXPLORACIÓN FINALIZADA] No hay más casillas alcanzables. Regresando a base.\n"
                
                if not self.path:
                    if (self.x, self.y) == self.base:
                        return "TERMINAR", None, explicacion_total + " Ya estoy en la base."
                else:
                    return self.think_and_act()
                    
        return "ESPERAR", None, "Esperando instrucciones."
