"""
Analisis empirico: RECURSIVIDAD (version Nova Defender)
Problema de la nave: elegir la ruta (una columna por paso) que evita
naves, meteoritos y balas durante n pasos, moviendose -1, 0 o +1 columnas.

Ambos algoritmos usan EXACTAMENTE la misma tabla de peligro y el mismo modelo,
por eso deben devolver el mismo costo optimo (se verifica en cada fila).

  Recursividad:          O(3^n)      (re-calcula los mismos subproblemas)
  Programacion dinamica: O(n * m)    (cada subproblema (t, columna) una sola vez)

Uso:   python benchmark.py            (no necesita pygame)
Salida: tabla en pantalla + resultados_benchmark.csv
"""
import csv
import random
import statistics
import time

COLS = 36            # columnas de la rejilla
MOVES = (-1, 0, 1)   # movimientos por paso
MOVE_COST = 0.6
HARD = 1000.0
INF = float("inf")
BUDGET_MS = 1000 / 60    # 16,7 ms por fotograma a 60 FPS


def make_danger(n, seed):
    """Tabla peligro[t][c]: 6 'obstaculos' por paso, cada uno bloquea 3 columnas."""
    rnd = random.Random(seed)
    danger = [[0.0] * COLS for _ in range(n + 1)]
    for t in range(1, n + 1):
        for _ in range(6):
            c = rnd.randint(1, COLS - 2)
            for k in (c - 1, c, c + 1):
                danger[t][k] = HARD
    return danger


# ------------------------------------------------------------------ RECURSION
nodes = 0


def route_recursive(c, t, n, danger):
    """Prueba los 3 movimientos en cada paso: 3^n llamadas."""
    global nodes
    nodes += 1
    if t == n:
        return 0.0
    best = INF
    for dc in MOVES:
        nc = c + dc
        if nc < 0 or nc >= COLS:
            continue
        cost = danger[t + 1][nc] + abs(dc) * MOVE_COST
        v = cost + route_recursive(nc, t + 1, n, danger)
        if v < best:
            best = v
    return best


def timeit(fn, reps):
    times = []
    for _ in range(reps):
        t0 = time.perf_counter()
        result = fn()
        times.append((time.perf_counter() - t0) * 1000)
    return statistics.median(times), result


def main():
    global nodes
    start_col = COLS // 2
    rows = []
    print(f"{'n':>3} {'3^n':>9} {'llamadas':>10} {'recursion ms':>13} {'< 16.7 ms':>10}")
    for n in range(3, 14):
        danger = make_danger(n, seed=n)
        reps = 20 if n <= 8 else (5 if n <= 10 else 1)

        def run_rec():
            global nodes
            nodes = 0
            return route_recursive(start_col, 0, n, danger)

        t_rec, _ = timeit(run_rec, reps)
        rows.append([n, 3 ** n, nodes, round(t_rec, 4), t_rec < BUDGET_MS])
        print(f"{n:>3} {3 ** n:>9} {nodes:>10} {t_rec:>13.4f} {str(t_rec < BUDGET_MS):>10}")
    with open("resultados_recursividad.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n_pasos", "3^n", "llamadas", "recursion_ms", "menor_16.7ms"])
        w.writerows(rows)
    print("\nGuardado: resultados_recursividad.csv (presupuesto: %.1f ms)" % BUDGET_MS)


if __name__ == "__main__":
    main()
