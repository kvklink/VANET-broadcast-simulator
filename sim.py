import multiprocessing as mp

from tqdm import tqdm
from main import *


def run(_args: (int, int)) -> [int]:
    amount, thread_index = _args
    result = []
    for count in tqdm(range(amount), position=thread_index):
        simulation_seed = "%.30f" % time()

        simulation = PG2DSimulation(simulation_seed, SOURCE_POS, SOURCE_TARGETS, HEAT_MAPS)
        simulation.simulate()
        rounds = len(simulation.num_of_broadcasters) - 1
        result.append(rounds)
    return result


if __name__ == '__main__':
    # Simulation settings
    # MAKE SURE VARIABLES IN HELP.PY ARE ALSO CORRECT
    # EXCEED_MOVES must be set to True
    SOURCE_POS = (25, 25)
    SOURCE_TARGETS = diamond()
    TOTAL_SIMULATION_COUNT = 10000
    # Only required for PGMM simulations
    HEAT_MAPS = ["./heatmaps/4-circles/left-top.jpg",
                 "./heatmaps/4-circles/left-bottom.jpg",
                 "./heatmaps/4-circles/right-top.jpg",
                 "./heatmaps/4-circles/right-bottom.jpg"]

    cpus = mp.cpu_count()
    print(f'Amount of cores available: {cpus}')
    L = list(range(cpus))
    chunk_size = TOTAL_SIMULATION_COUNT // cpus
    chunks = [chunk_size for _ in range(cpus)]
    for i in range(TOTAL_SIMULATION_COUNT % cpus):
        chunks[i] += 1

    p = mp.Pool(cpus, initargs=(mp.RLock(),))
    results = p.map(run, [*zip(chunks, range(cpus))])
    p.close()
    p.join()

    # Flatten all result arrays into one
    results = [item for sublist in results for item in sublist]
    # Remove entries where the max amount of moves was exceeded
    results = list(filter(lambda x: x != NUM_OF_MOVES, results))

    print(f'min: {min(results)}, max: {max(results)}')
    print(f'Amount of timed out simulations: {TOTAL_SIMULATION_COUNT - len(results)}, {len(results)} remain')
    print(f'Average number of rounds: {sum(results) / len(results)}')
    print("\a")  # Ring the terminal bell to indicate we're done
