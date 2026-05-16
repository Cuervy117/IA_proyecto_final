import random

class Environment:
    def __init__(self, width=6, height=6, num_obstacles=8, num_dirt=10):
        self.width = width
        self.height = height
        self.obstacles = set()
        self.dirt = set()
        
        # Base de carga
        self.base = (0, 0)
        
        # Evitar obstáculos en la base y en sus casillas adyacentes inmediatas
        base_y_adyacentes = {self.base, (self.base[0]+1, self.base[1]), (self.base[0]-1, self.base[1]), 
                                   (self.base[0], self.base[1]+1), (self.base[0], self.base[1]-1)}
        
        # Generar obstáculos aleatorios
        while len(self.obstacles) < num_obstacles:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            if (x, y) not in base_y_adyacentes:
                self.obstacles.add((x, y))

        # Función auxiliar para comprobar accesibilidad
        def is_reachable(goal):
            queue = [self.base]
            visited = {self.base}
            while queue:
                cx, cy = queue.pop(0)
                if (cx, cy) == goal:
                    return True
                for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if (nx, ny) not in self.obstacles and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
            return False

        # Generar suciedad aleatoria evitando obstáculos, la base y zonas inalcanzables
        attempts = 0
        while len(self.dirt) < num_dirt and attempts < 1000:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            if (x, y) != self.base and (x, y) not in self.obstacles:
                if is_reachable((x, y)):
                    self.dirt.add((x, y))
            attempts += 1

    def remove_dirt(self, x, y):
        if (x, y) in self.dirt:
            self.dirt.remove((x, y))

    def spawn_dirt(self, num_dirt=5):
        def is_reachable(goal):
            queue = [self.base]
            visited = {self.base}
            while queue:
                cx, cy = queue.pop(0)
                if (cx, cy) == goal:
                    return True
                for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if (nx, ny) not in self.obstacles and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
            return False

        spawned = 0
        attempts = 0
        max_attempts = 100
        while spawned < num_dirt and attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) != self.base and (x, y) not in self.obstacles and (x, y) not in self.dirt:
                if is_reachable((x, y)):
                    self.dirt.add((x, y))
                    spawned += 1
            attempts += 1

    def is_obstacle(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return (x, y) in self.obstacles

    def get_percepts(self, x, y, orientacion):
        is_dirty = (x, y) in self.dirt
        
        fx, fy = x, y
        if orientacion == "N": fy += 1
        elif orientacion == "S": fy -= 1
        elif orientacion == "E": fx += 1
        elif orientacion == "W": fx -= 1
        
        sensor_frente = False
        if fx < 0 or fx >= self.width or fy < 0 or fy >= self.height:
            sensor_frente = True
        elif (fx, fy) in self.obstacles:
            sensor_frente = True
            
        colision = (x, y) in self.obstacles
        return {"Obstaculo_Frente": sensor_frente, "Suciedad": is_dirty, "Colision": colision}

    def print_grid(self, agent_pos):
        print("-" * (self.width * 4 + 1))
        for y in range(self.height - 1, -1, -1):
            row = "|"
            for x in range(self.width):
                cell = " "
                if self.is_obstacle(x, y):
                    cell = "X"
                elif (x, y) == agent_pos:
                    cell = "A"
                elif (x, y) == (0, 0):
                    cell = "B"
                elif (x, y) in self.dirt:
                    cell = "*"
                row += f" {cell} |"
            print(row)
            print("-" * (self.width * 4 + 1))
