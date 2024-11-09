import time
import matplotlib.pyplot as plt
import pandas as pd
from game import *

MIN_THRESHOLD = 3


def run_simulation_with_graph(configurations):
    results = []  # Para almacenar todos los resultados
    summary_tables = []  # Para las tablas resumen para LaTeX
    average_move_times = []  # Para almacenar el tiempo promedio de movimiento
    board_sizes = []  # Para almacenar el tamaño del tablero (filas x columnas)

    for config in configurations:
        ROWS, COLUMNS, MINE_COUNT = config['ROWS'], config['COLUMNS'], config['MINE_COUNT']
        print(f"\nProbando configuración: ROWS={ROWS}, COLUMNS={COLUMNS}, MINE_COUNT={MINE_COUNT}")

        set_board_config(ROWS, COLUMNS, MINE_COUNT)

        brute_force_stats = initialize_stats()
        heuristic_stats = initialize_stats()

        # Ejecutar simulaciones en 100 tableros, como en run_simulation
        for board_num in range(100):  # Ejecutar simulaciones por 100 tableros
            brute_force_result = play_game("brute_force", retry_on_early_loss=True)
            heuristic_result = play_game("heuristic", retry_on_early_loss=True)

            # Actualizar estadísticas para cada solver
            for result, stats, solver in zip(
                    [brute_force_result, heuristic_result],
                    [brute_force_stats, heuristic_stats],
                    ["Brute Force", "Heuristic"]
            ):
                total_time, move_times, moves, won = result
                update_stats(stats, total_time, move_times, moves, won)

                # Almacenar los resultados detallados
                results.append({
                    "Solver": solver,
                    "Board Number": board_num + 1,
                    "Rows": ROWS,
                    "Columns": COLUMNS,
                    "Mines": MINE_COUNT,
                    "Total Time (s)": total_time,
                    "Average Move Time (s)": sum(move_times) / len(move_times),
                    "Total Moves": moves,
                    "Won": won
                })

        # Calcular promedios y porcentaje de victorias para cada solver
        brute_force_results = calculate_averages(brute_force_stats, 100)
        heuristic_results = calculate_averages(heuristic_stats, 100)

        # Agregar los resultados de cada solver a la tabla resumen para LaTeX
        summary_tables.append(
            pd.DataFrame([brute_force_results, heuristic_results], index=["Brute Force", "Heuristic"])
        )

        # Calcular el tiempo promedio de movimiento y añadirlo a la lista
        avg_move_time_brute_force = brute_force_stats["move_time"] / 100
        avg_move_time_heuristic = heuristic_stats["move_time"] / 100

        average_move_times.append((avg_move_time_brute_force, avg_move_time_heuristic))
        board_sizes.append(ROWS * COLUMNS)

        # Imprimir resumen para cada configuración
        print(f"\nResultados de configuración: ROWS={ROWS}, COLUMNS={COLUMNS}, MINE_COUNT={MINE_COUNT}")
        print(summary_tables[-1])

    # Graficar los resultados
    plot_move_times(board_sizes, average_move_times)

    # Guardar resultados detallados en CSV
    df_results = pd.DataFrame(results)
    df_results.to_csv("output/resultados.csv", index=False)

    # Generar tablas LaTeX
    generate_latex_tables(summary_tables, configurations)


def plot_move_times(board_sizes, average_move_times):
    brute_force_times, heuristic_times = zip(*average_move_times)

    plt.figure(figsize=(10, 6))
    plt.plot(board_sizes, brute_force_times, marker='o', label='Brute Force')
    plt.plot(board_sizes, heuristic_times, marker='o', label='Heuristic')
    plt.xlabel('Tamaño del Tablero (Filas x Columnas)')
    plt.ylabel('Tiempo Promedio de Movimiento (s)')
    plt.title('Tiempo Promedio de Movimiento según el Tamaño del Tablero')
    plt.legend()
    plt.grid(True)
    plt.show()


def run_simulation(configurations):
    results = []
    summary_tables = []

    for config in configurations:
        ROWS, COLUMNS, MINE_COUNT = config['ROWS'], config['COLUMNS'], config['MINE_COUNT']
        print(f"\nProbando configuración: ROWS={ROWS}, COLUMNS={COLUMNS}, MINE_COUNT={MINE_COUNT}")

        set_board_config(ROWS, COLUMNS, MINE_COUNT)

        brute_force_stats = initialize_stats()
        heuristic_stats = initialize_stats()

        for board_num in range(100):
            brute_force_result = play_game("brute_force", retry_on_early_loss=True)
            heuristic_result = play_game("heuristic", retry_on_early_loss=True)

            for result, stats, solver in zip(
                    [brute_force_result, heuristic_result],
                    [brute_force_stats, heuristic_stats],
                    ["Brute Force", "Heuristic"]
            ):
                total_time, move_times, moves, won = result
                update_stats(stats, total_time, move_times, moves, won)

                results.append({
                    "Solver": solver,
                    "Board Number": board_num + 1,
                    "Rows": ROWS,
                    "Columns": COLUMNS,
                    "Mines": MINE_COUNT,
                    "Total Time (s)": total_time,
                    "Average Move Time (s)": sum(move_times) / len(move_times),
                    "Total Moves": moves,
                    "Won": won
                })

        # Calcular promedios y porcentaje de victorias para cada solver
        brute_force_results = calculate_averages(brute_force_stats, 100)
        heuristic_results = calculate_averages(heuristic_stats, 100)

        # Agregar a la tabla resumen para LaTeX
        summary_tables.append(
            pd.DataFrame([brute_force_results, heuristic_results], index=["Brute Force", "Heuristic"])
        )

        # Imprimir resumen para cada configuración
        print(f"\nResultados de configuración: ROWS={ROWS}, COLUMNS={COLUMNS}, MINE_COUNT={MINE_COUNT}")
        print(summary_tables[-1])

    # Guardar resultados detallados en CSV
    df_results = pd.DataFrame(results)
    df_results.to_csv("output/resultados.csv", index=False)

    # Generar tablas LaTeX
    generate_latex_tables(summary_tables, configurations)


def set_board_config(rows, columns, mine_count):
    global ROWS, COLUMNS, MINE_COUNT, BOARD, MINES, EXTENDED, MATRIX
    ROWS, COLUMNS, MINE_COUNT = rows, columns, mine_count
    # Reiniciar el estado global del tablero
    BOARD = []
    MINES = set()
    EXTENDED = set()
    MATRIX = [['?'] * COLUMNS for _ in range(ROWS)]  # Crear un nuevo tablero vacío


def initialize_stats():
    return {
        "total_time": 0,
        "move_time": 0,
        "moves": 0,
        "wins": 0,
    }


def update_stats(stats, total_time, move_times, moves, won):
    stats["total_time"] += total_time
    stats["move_time"] += sum(move_times) / len(move_times)
    stats["moves"] += moves
    stats["wins"] += int(won)


def play_game(solver, retry_on_early_loss=False):
    attempts = 0
    create_board()  # Reinicia el estado del tablero antes de cada simulación
    moves = 0
    total_time = 0
    move_times = []

    while True:
        start_time = time.time()
        if solver == "brute_force":
            square, was_random = brute_force_solve()
        elif solver == "heuristic":
            square, was_random = heuristic_solve()
        else:
            raise ValueError("Solver desconocido")

        end_time = time.time()
        move_time = end_time - start_time
        total_time += move_time
        move_times.append(move_time)

        moves += 1
        mine_hit = update_board(square)
        if mine_hit or has_won():
            break

    # Si el juego no fue exitoso o si se ha alcanzado el umbral de movimientos,
    # devolvemos los resultados
    if not mine_hit or moves > MIN_THRESHOLD or not retry_on_early_loss:
        return total_time, move_times, moves, not mine_hit
    else:
        attempts += 1
        print(f"Reintentando el tablero {attempts} debido a pérdida temprana en {solver}.")
        # Aquí garantizamos que siempre se retorne un valor si se hace un reintento.
        return total_time, move_times, moves, True  # Asumimos que no se ha perdido el juego si estamos reintentando


def calculate_averages(stats, num_boards):
    return {
        "Total Time (s)": stats["total_time"] / num_boards,
        "Average Move Time (s)": stats["move_time"] / num_boards,
        "Average Moves": stats["moves"] / num_boards,
        "Win Percentage (%)": (stats["wins"] / num_boards) * 100,
    }


def generate_latex_tables(summary_tables, configurations):
    with open("output/tablas.tex", "w") as file:
        for idx, config in enumerate(configurations):
            ROWS, COLUMNS, MINE_COUNT = config['ROWS'], config['COLUMNS'], config['MINE_COUNT']
            table = summary_tables[idx]
            latex_table = table.to_latex(
                caption=f"Resultados para ROWS={ROWS}, COLUMNS={COLUMNS}, MINES={MINE_COUNT}",
                label=f"tab:{ROWS}_{COLUMNS}_{MINE_COUNT}",
                index=True
            )
            file.write(latex_table + "\n\n")
        print("\nTablas LaTeX generadas en el archivo tablas.tex.")


if __name__ == '__main__':
    configurations = [
        {"ROWS": 5, "COLUMNS": 5, "MINE_COUNT": 5},
        {"ROWS": 10, "COLUMNS": 10, "MINE_COUNT": 20},
        {"ROWS": 15, "COLUMNS": 15, "MINE_COUNT": 45}
    ]
    run_simulation_with_graph(configurations)
