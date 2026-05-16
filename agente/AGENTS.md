# Agent: Aspiradora Inteligente FI-UNAM
**Role:** Agente autónomo de limpieza basado en inferencia lógica.
**Objective:** Mapear un entorno de $N \times M$ y succionar todo el polvo minimizando colisiones.
**Logic Model:** Inferencia proposicional mediante comprobación de modelos (Russell & Norvig Cap. 7).

## Skills
- `Maps_grid`: Moverse a coordenadas (x, y) seguras.
- `infer_obstacles`: Procesar percepciones para actualizar la Base de Conocimientos (KB).
- `clean_spot`: Accionar el actuador de succión.

## Constraints
- No salir de los límites de la matriz.
- Priorizar siempre casillas con `p_segura == 1.0`.