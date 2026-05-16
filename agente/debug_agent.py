from environment import Environment
from agent import VacuumAgent

class StaticEnvironment(Environment):
    def __init__(self):
        self.width = 6
        self.height = 6
        self.obstacles = {(2, 1), (3, 3), (4, 4)}
        self.dirt = {(0, 2), (5, 5), (2, 2)}
        self.base = (0, 0)
        
    def is_obstacle(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return (x, y) in self.obstacles
        
env = StaticEnvironment()
agent = VacuumAgent(width=6, height=6, start_x=0, start_y=0, max_battery=25)

paso = 1
running = True
while running and paso < 50:
    percepts = env.get_percepts(agent.x, agent.y)
    agent.perceive(percepts)
    action, args, expl = agent.think_and_act()
    print(f"Step {paso}: Pos={(agent.x, agent.y)} Percepts={percepts} Action={action} Args={args}")
    
    if action == "ASPIRAR":
        env.remove_dirt(agent.x, agent.y)
    elif action == "TERMINAR":
        break
    paso += 1
    
print("Dirt remaining:", env.dirt)
print("Visited cells:", agent.visited)
