import time
from environment import Environment
from agent import VacuumAgent
from visualizer import Visualizer
import pygame

def main():
    print("Iniciando Simulación: Aspiradora Autónoma (Avanzada con PyGame)")
    
    env = Environment(width=8, height=8, num_obstacles=14, num_dirt=15)
    agent = VacuumAgent(width=8, height=8, start_x=0, start_y=0, max_battery=120)
    
    viz = Visualizer(width=8, height=8)
    
    paso = 1
    action_text = "Iniciando..."
    running = True
    resting = False
    rest_counter = 0
    
    while running:
        # Dibujar estado en la ventana
        running, clicks = viz.process_events()
        if not running:
            break
            
        # Procesar interactividad del usuario
        for btn, cx, cy in clicks:
            if btn == 1: # Izquierdo = Suciedad
                if 0 <= cx < env.width and 0 <= cy < env.height and (cx, cy) not in env.obstacles and getattr(env, 'base', (0,0)) != (cx, cy):
                    env.dirt.add((cx, cy))
                    action_text = f"¡INTERVENCIÓN! Usuario ensució ({cx}, {cy})"
                    print(action_text)
            elif btn == 3: # Derecho = Obstáculo
                if 0 <= cx < env.width and 0 <= cy < env.height and getattr(env, 'base', (0,0)) != (cx, cy):
                    if (cx, cy) in env.dirt: env.dirt.remove((cx, cy))
                    env.obstacles.add((cx, cy))
                    action_text = f"¡INTERVENCIÓN! Usuario puso obstáculo en ({cx}, {cy})"
                    print(action_text)
        if resting:
            rest_counter += 1
            action_text = f"REPOSO EN BASE... ({rest_counter}/10)"
            if rest_counter >= 10:
                env.spawn_dirt(5)
                agent.mode = "PATROL"
                agent.patrol_targets = set(agent.visited)
                resting = False
                action_text = "¡NUEVA SUCIEDAD! INICIANDO PATRULLAJE."
                print(f"\n{'='*50}\n{action_text}\n{'='*50}")
            viz.draw(env, agent, paso, action_text)
            pygame.time.wait(166)
            paso += 1
            continue
        viz.draw(env, agent, paso, action_text)
        
        print(f"\n{'='*50}")
        print(f"PASO {paso}")
        print(f"{'='*50}")
        
        env.print_grid((agent.x, agent.y))
        print(f"Posición del agente: ({agent.x}, {agent.y}) Mirando al: {agent.orientacion} | Batería: {agent.battery}/{agent.max_battery} | Modo: {agent.mode}")
        
        percepts = env.get_percepts(agent.x, agent.y, agent.orientacion)
        print(f"Percepciones: {percepts}")
        agent.perceive(percepts)
        
        action, args, expl = agent.think_and_act()
        
        print("\n--- CADENA DE INFERENCIA ---")
        print(expl)
        print("----------------------------\n")
        
        if action == "ASPIRAR":
            action_text = f"ASPIRANDO la casilla ({agent.x}, {agent.y})"
            print(f">>> Acción ejecutada: {action_text}")
            env.remove_dirt(agent.x, agent.y)
        elif action == "MOVER":
            action_text = f"MOVIENDO a {args}"
            print(f">>> Acción ejecutada: {action_text}")
        elif action == "ROTAR_IZQ":
            action_text = "ROTANDO a la IZQUIERDA"
            print(f">>> Acción ejecutada: {action_text}")
        elif action == "ROTAR_DER":
            action_text = "ROTANDO a la DERECHA"
            print(f">>> Acción ejecutada: {action_text}")
        elif action == "ESPERAR":
            action_text = "OBSERVANDO..."
            print(f">>> Acción ejecutada: {action_text}")
        elif action == "CHOQUE":
            action_text = f"¡COLISIÓN! Regresando a {args}"
            print(f">>> Acción ejecutada: {action_text}")
        elif action == "RECARGAR":
            action_text = "RECARGANDO BATERÍA AL 100%"
            print(f">>> Acción ejecutada: {action_text}")
        elif action == "TERMINAR":
            action_text = "Misión actual completada. Esperando..."
            print(">>> Acción ejecutada: TERMINAR.")
            print("El agente ha completado su misión y regresado a la base. Entrando en reposo.")
            resting = True
            rest_counter = 0
            
        paso += 1
        # Reemplazamos time.sleep por pygame.time.wait para no congelar la ventana
        pygame.time.wait(166)

    viz.close()

if __name__ == "__main__":
    main()
