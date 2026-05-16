from environment import Environment
from agent import VacuumAgent
import sys

# Test headless execution for 200 steps
env = Environment(width=6, height=6, num_obstacles=8, num_dirt=10)
agent = VacuumAgent(width=6, height=6, start_x=0, start_y=0, max_battery=40)

paso = 1
resting = False
rest_counter = 0

for _ in range(250):
    if resting:
        rest_counter += 1
        if rest_counter >= 10:
            env.spawn_dirt(5)
            agent.mode = "PATROL"
            agent.patrol_targets = set(agent.visited)
            resting = False
            print(f"PASO {paso}: NUEVA SUCIEDAD DETECTADA. PATRULLAJE INICIADO.")
        paso += 1
        continue
        
    percepts = env.get_percepts(agent.x, agent.y, agent.orientacion)
    agent.perceive(percepts)
    
    action, args, expl = agent.think_and_act()
    if action == "ESPERAR":
        print(f"PASO {paso}: {action} | pos=({agent.x},{agent.y}) mode={agent.mode} path={agent.path} visited_len={len(agent.visited)} target_path={agent._bfs_path((agent.x, agent.y), agent.base)}")
    
    if action == "ASPIRAR":
        env.remove_dirt(agent.x, agent.y)
    elif action == "TERMINAR":
        print(f"PASO {paso}: TERMINAR -> Entrando en reposo.")
        resting = True
        rest_counter = 0
    elif action == "CHOQUE":
        print(f"PASO {paso}: CHOQUE at {args}")
        
    paso += 1

print(f"Simulación terminada tras {paso-1} pasos. Dirt remaining: {len(env.dirt)}")
print(f"Agent mode: {agent.mode}, Battery: {agent.battery}/{agent.max_battery}")
