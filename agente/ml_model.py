import os
import pickle
import random
import numpy as np
from sklearn.tree import DecisionTreeClassifier

MODEL_PATH = "decision_tree_model.pkl"

def get_or_train_model():
    """Carga el modelo de ML si existe, o genera datos y lo entrena si no."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
            
    # Generar datos de entrenamiento ficticios basados en reglas ideales
    # Features: [battery_pct (0.0-1.0), dist_to_base (int), exp_done (0/1), pat_done (0/1)]
    # Labels: 0 (EXPLORE), 1 (GO_CHARGE), 2 (PATROL), 3 (GO_FINISH)
    X = []
    y = []
    
    for _ in range(3000):
        bat = random.uniform(0.0, 1.0)
        dist = random.randint(0, 30)
        exp_done = random.choice([0, 1])
        pat_done = random.choice([0, 1])
        
        # La batería cruda la multiplicamos para simular un max_battery típico de 100-120
        bat_raw = bat * 120 
        
        if bat_raw <= dist + 3:  # Margen de seguridad para volver a la base
            label = 1 # GO_CHARGE
        else:
            if exp_done == 0:
                label = 0 # EXPLORE
            elif pat_done == 0:
                label = 2 # PATROL
            else:
                label = 3 # GO_FINISH
                
        X.append([bat, dist, exp_done, pat_done])
        y.append(label)
        
    # Entrenar el Árbol de Decisión
    clf = DecisionTreeClassifier(max_depth=5, random_state=42)
    clf.fit(X, y)
    
    # Guardar el modelo
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
        
    return clf

def predict_mode(model, battery_pct, dist_to_base, exp_done, pat_done):
    """Utiliza el árbol de decisión para predecir el mejor modo del agente."""
    pred = model.predict([[battery_pct, dist_to_base, exp_done, pat_done]])[0]
    modes = {0: "EXPLORE", 1: "GO_CHARGE", 2: "PATROL", 3: "GO_FINISH"}
    return modes[pred]
