# Nova Defender - RECURSIVIDAD (Python + Pygame y HTML)

Juego de aviones para el proyecto de Analisis de Algoritmos. La ruta del autopiloto (tecla **T**) se calcula con **recursividad**.
La carpeta trae **dos versiones** del juego:

| Version | Como ejecutarla |
|---|---|
| **Pygame** (`main.py`) | `pip install -r requirements.txt` y luego `python main.py` (VS Code) |
| **Web** (`index.html`) | Abrir `index.html` con doble clic en el navegador (Chrome/Edge). Tambien se publica en GitHub Pages con `.github/workflows/pages.yml` |

## Reglas (requisitos del informe)
- **3 vidas**; **3 niveles** (1 basico: enemigos a velocidad media, 2 intermedio: enemigos rapidos, 3 dificil: rapidos + meteoritos).
- La nave y los enemigos disparan; **jefe final** al terminar cada nivel.
- Controles: flechas/WASD o mouse, ESPACIO o clic (disparar), ESC pausa, **T** autopiloto, **F** tiempo por fotograma (en Pygame).

## Donde esta la recursividad
- **Ruta del autopiloto (las dos versiones):** `buscar()` en `main.py` / `rSearch()` en `index.html` prueba izquierda-centro-derecha y se llama a si misma (poda + tope de nodos). No guarda tablas.
- **Solo en la version web:** formaciones de enemigos, disparo fractal del jefe y explosion en cadena tambien son recursivas.
- El resto del juego (movimiento, colisiones) es programacion normal.

Diferencia entre versiones: en Pygame el menu elige el nivel inicial; en la web el menu elige un modo (basico/intermedio/dificil) que ajusta la dureza y se juegan los 3 niveles en orden.

## Analisis empirico
`python benchmark_recursividad.py` mide la recursion (3^n llamadas) y genera `resultados_recursividad.csv`.
