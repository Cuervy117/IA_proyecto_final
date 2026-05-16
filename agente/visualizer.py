import pygame
from logic import Literal

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19) # Obstáculos
GREEN = (34, 139, 34) # Base
BLUE = (0, 0, 255) # Agente
YELLOW = (255, 215, 0) # Suciedad
RED = (255, 0, 0) # Batería baja
DARK_GRAY = (40, 40, 40) # Niebla de guerra

CELL_SIZE = 80
MARGIN = 5
TOP_MARGIN = 40

class Visualizer:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        
        self.grid_width = width * CELL_SIZE + (width + 1) * MARGIN
        self.grid_height = height * CELL_SIZE + (height + 1) * MARGIN
        
        self.screen_width = self.grid_width * 2
        self.screen_height = self.grid_height + 100 + TOP_MARGIN
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Aspiradora Autónoma: Entorno Real vs Visión del Agente")
        self.font = pygame.font.SysFont("Arial", 20)
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)

    def draw(self, env, agent, paso, action_text):
        self.screen.fill(BLACK)
        
        # Títulos
        title1 = self.title_font.render("Entorno Real", True, WHITE)
        title2 = self.title_font.render("Visión del Agente (Niebla)", True, WHITE)
        self.screen.blit(title1, (self.grid_width // 2 - title1.get_width() // 2, 5))
        self.screen.blit(title2, (self.grid_width + self.grid_width // 2 - title2.get_width() // 2, 5))
        
        # Dibujar cuadrículas
        self._draw_grid(env, agent, offset_x=0, offset_y=TOP_MARGIN, is_agent_view=False)
        self._draw_grid(env, agent, offset_x=self.grid_width, offset_y=TOP_MARGIN, is_agent_view=True)
        
        # Separador central
        pygame.draw.line(self.screen, WHITE, (self.grid_width, 0), (self.grid_width, self.screen_height - 100), 2)
        
        # Panel de información inferior
        info_y = self.screen_height - 90
        
        text1 = self.font.render(f"Paso: {paso} | Modo: {agent.mode}", True, WHITE)
        text2 = self.font.render(f"Acción: {action_text}", True, WHITE)
        self.screen.blit(text1, (10, info_y))
        self.screen.blit(text2, (10, info_y + 35))
        
        # Barra de batería
        battery_pct = max(0, min(1.0, agent.battery / agent.max_battery))
        r = min(255, int(255 * 2 * (1 - battery_pct)))
        g = min(255, int(255 * 2 * battery_pct))
        battery_color = (r, g, 0)
        
        bar_width = 150
        bar_height = 25
        bar_x = self.screen_width - bar_width - 15
        bar_y = info_y
        
        bat_label = self.font.render("Batería:", True, WHITE)
        self.screen.blit(bat_label, (bar_x - bat_label.get_width() - 10, bar_y + 2))
        
        fill_width = int(bar_width * battery_pct)
        if fill_width > 0:
            pygame.draw.rect(self.screen, battery_color, (bar_x, bar_y, fill_width, bar_height))
            
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
            
        bat_text = self.font.render(f"{int(battery_pct*100)}%", True, BLACK if 0.3 < battery_pct < 0.7 else WHITE)
        text_rect = bat_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        self.screen.blit(bat_text, text_rect)
        
        pygame.display.flip()

    def _draw_grid(self, env, agent, offset_x, offset_y, is_agent_view):
        for y in range(self.height):
            for x in range(self.width):
                draw_y = self.height - 1 - y 
                rect = pygame.Rect(
                    offset_x + MARGIN + x * (CELL_SIZE + MARGIN),
                    offset_y + MARGIN + draw_y * (CELL_SIZE + MARGIN),
                    CELL_SIZE,
                    CELL_SIZE
                )
                
                color = WHITE
                has_dirt = False
                is_fog = False
                
                if not is_agent_view:
                    if env.is_obstacle(x, y):
                        color = BROWN
                    elif hasattr(env, 'base') and (x, y) == env.base:
                        color = GREEN
                    if (x, y) in env.dirt:
                        has_dirt = True
                else:
                    if (x, y) in agent.visited:
                        color = WHITE
                        if hasattr(env, 'base') and (x, y) == env.base:
                            color = GREEN
                            
                        in_targets = hasattr(agent, 'patrol_targets') and (x, y) in agent.patrol_targets
                        in_route = hasattr(agent, 'patrol_route') and (x, y) in agent.patrol_route
                        if in_targets or in_route:
                            color = (70, 90, 110) # Azul-grisáceo para distinguirla de la niebla normal
                            is_fog = True
                    else:
                        obs_sym = Literal(f"O_{x}_{y}").to_sympy()
                        
                        if obs_sym in agent.kb.clauses:
                            color = BROWN
                        else:
                            # Si no la ha visitado y no es un obstáculo confirmado, es NIEBLA total.
                            # Incluso si el agente sabe lógicamente que es segura para pisar, 
                            # no la ha "revisado", así que no sabemos si hay basura.
                            color = DARK_GRAY
                            is_fog = True
                            
                    # La suciedad (L_x_y en negativo es sucio según el agente)
                    dirty_sym = Literal(f"L_{x}_{y}").negate().to_sympy()
                    if dirty_sym in agent.kb.clauses:
                        has_dirt = True
                        
                pygame.draw.rect(self.screen, color, rect)
                
                if has_dirt and not is_fog:
                    pygame.draw.circle(self.screen, YELLOW, rect.center, CELL_SIZE // 4)
                
                # Agente
                if (x, y) == (agent.x, agent.y):
                    agent_color = BLUE if agent.battery > 5 else RED
                    pygame.draw.circle(self.screen, agent_color, rect.center, CELL_SIZE // 2 - 10)
                    
                    center_x, center_y = rect.center
                    radius = CELL_SIZE // 2 - 10
                    if getattr(agent, 'orientacion', 'N') == "N":
                        end_pos = (center_x, center_y - radius)
                    elif agent.orientacion == "S":
                        end_pos = (center_x, center_y + radius)
                    elif agent.orientacion == "E":
                        end_pos = (center_x + radius, center_y)
                    else:
                        end_pos = (center_x - radius, center_y)
                        
                    pygame.draw.line(self.screen, BLACK, rect.center, end_pos, 4)

    def process_events(self):
        """Retorna (running, clicks_list) donde clicks_list es una lista de tuplas (button, x, y)"""
        clicks = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, clicks
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if MARGIN <= mx <= self.grid_width - MARGIN and TOP_MARGIN <= my <= self.grid_height + TOP_MARGIN:
                    grid_x = (mx - MARGIN) // (CELL_SIZE + MARGIN)
                    draw_y = (my - TOP_MARGIN - MARGIN) // (CELL_SIZE + MARGIN)
                    grid_y = self.height - 1 - draw_y
                    clicks.append((event.button, grid_x, grid_y))
        return True, clicks

    def close(self):
        pygame.quit()
