import os

# Test path to actions logic
def _path_to_actions(curr_x, curr_y, curr_dir, path_coords, look_only_at_end=False):
    actions = []
    dirs = ["N", "E", "S", "W"]
    
    for i, (nx, ny) in enumerate(path_coords):
        if nx == curr_x and ny == curr_y + 1: target_dir = "N"
        elif nx == curr_x and ny == curr_y - 1: target_dir = "S"
        elif nx == curr_x + 1 and ny == curr_y: target_dir = "E"
        elif nx == curr_x - 1 and ny == curr_y: target_dir = "W"
        else: continue # should not happen in BFS
        
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

print(_path_to_actions(0, 0, "N", [(0, 1), (1, 1)], True)) # Expect [MOVER (0,1), ROTAR_DER]
print(_path_to_actions(0, 0, "N", [(1, 0)], True)) # Expect [ROTAR_DER]
print(_path_to_actions(0, 0, "N", [(0, 1)], False)) # Expect [MOVER (0,1)]
