'''
baseline random simulation for sensor placement optimization
--
idea:
    randomly select N sensor locations from all junctions, many times
    evaluate each random solution by total pipe length covered
    keep the best solution found across all iterations
--
inputs
- pickled networkx graph object (edges have 'identifier' and 'length' attributes)
- pickled coverage dictionary {junction ID: [list of reachable pipe IDs]}
- N: number of sensors to deploy
- num_iterations: number of random samples to try
outputs
- best_solution: list of junction IDs selected
- best_objective: total length of covered pipes (meters)
'''


# import required packages
import os, code, yaml, argparse
import pickle
import random
import networkx as nx


def build_pipe_length_lookup(G, id_attribute, length_attribute):
    """
    build a dictionary mapping pipe identifier to its length from the graph edges.

    Parameters
    ----------
    G : networkx.DiGraph
        the graph object with edge attributes.
    id_attribute : str
        edge attribute name for the pipe identifier.
    length_attribute : str
        edge attribute name for the pipe length.

    Returns
    -------
    dict
        {pipe_identifier: pipe_length_in_meters}
    """
    pipe_length_lookup = {}
    for u, v, data in G.edges(data=True):
        pipe_id = data.get(id_attribute)
        pipe_length = data.get(length_attribute)
        if pipe_id is not None and pipe_length is not None:
            pipe_length_lookup[pipe_id] = pipe_length
    return pipe_length_lookup


def evaluate_solution(junction_selection, coverage_dict, pipe_length_lookup):
    """
    evaluate a sensor placement solution by computing total covered pipe length.

    Parameters
    ----------
    junction_selection : list
        list of selected junction IDs for sensor placement.
    coverage_dict : dict
        {junction ID: [list of reachable pipe IDs]}.
    pipe_length_lookup : dict
        {pipe_identifier: pipe_length_in_meters}.

    Returns
    -------
    float
        total length of all unique covered pipes (meters).
    set
        set of all covered pipe IDs.
    """
    # initialize set of covered pipes
    # use of set avoids double counting
    all_covered_pipes = set()

    # loop over selected junctions
    for junction in junction_selection:
        # get list of covered pipes for this junction
        covered_pipes = coverage_dict.get(junction, [])
        if covered_pipes is not None:
            # update set (avoids double counting)
            all_covered_pipes.update(covered_pipes)

    # calculate total covered distance
    total_distance_covered = sum(
        pipe_length_lookup.get(pipe_id, 0) for pipe_id in all_covered_pipes
    )

    return total_distance_covered, all_covered_pipes


# main function here
def main(
        folder_path,
        graph_pickle,
        coverage_pickle,
        id_attribute,
        length_attribute,
        N,
        num_iterations,
        random_seed,
    ):

    # set folder
    os.chdir(folder_path)

    'step 1 - read graph from pickle path'
    with open(graph_pickle, 'rb') as f:
        G = pickle.load(f)

    'step 2 - read coverage dictionary from pickle path'
    with open(coverage_pickle, 'rb') as f:
        coverage_dict = pickle.load(f)

    'step 3 - build pipe length lookup from graph edges'
    pipe_length_lookup = build_pipe_length_lookup(G, id_attribute, length_attribute)

    'step 4 - get all junctions from graph'
    all_junctions = list(G.nodes())
    num_junctions = len(all_junctions)
    num_pipes = G.number_of_edges()

    # compute total pipe length in the network
    total_network_length = sum(pipe_length_lookup.values())

    print(f"number of junctions: {num_junctions}")
    print(f"number of pipes: {num_pipes}")
    print(f"total network pipe length: {total_network_length:.2f} meters")
    print(f"number of sensors to place (N): {N}")
    print(f"number of random iterations: {num_iterations}")
    print()

    # validate N
    assert N <= num_junctions, \
        f"N ({N}) cannot exceed the number of junctions ({num_junctions})"

    'step 5 - random simulation'
    # set random seed for reproducibility
    if random_seed is not None:
        random.seed(random_seed)

    best_solution = None
    best_objective = 0

    for i in range(num_iterations):
        # randomly sample N locations from all junctions
        junction_selection = random.sample(all_junctions, N)

        # evaluate this random solution
        total_distance_covered, all_covered_pipes = evaluate_solution(
            junction_selection, coverage_dict, pipe_length_lookup
        )

        # check if best solution and best objective needs updating
        if total_distance_covered > best_objective:
            # update if better solution found
            best_solution = junction_selection
            best_objective = total_distance_covered
            best_covered_pipes = all_covered_pipes
            print(f"iteration {i}: new best objective = {best_objective:.2f} meters")

    'step 6 - print results'
    print()
    print("=" * 60)
    print("RANDOM SIMULATION RESULTS")
    print("=" * 60)
    print(f"best objective (total covered pipe length): {best_objective:.2f} meters")
    print(f"number of unique pipes covered: {len(best_covered_pipes)}")
    print(f"coverage: {best_objective / total_network_length * 100:.2f}% of total network length")
    print(f"best solution (junction IDs): saved to output pickle")
    print("=" * 60)

    'step 7 - save results'
    results = {
        'best_solution': best_solution,
        'best_objective': best_objective,
        'best_covered_pipes': best_covered_pipes,
        'N': N,
        'num_iterations': num_iterations,
        'num_junctions': num_junctions,
        'total_network_length': total_network_length,
    }
    with open('random_simulation_output.pickle', 'wb') as f:
        pickle.dump(results, f)

    print("results saved to random_simulation_output.pickle")

    code.interact(local=dict(globals(), **locals()))

    # exit function
    return


# command line run
if __name__ == "__main__":

    # use argparse to read config file
    parser = argparse.ArgumentParser(description="random simulation baseline for sensor placement")
    parser.add_argument("config_file", type=str)
    args = parser.parse_args()
    # open config yaml file
    with open(args.config_file, "r") as stream:
        config_data = yaml.safe_load(stream)
    # filter to the commands
    inputs = config_data['Inputs']['random_simulation']

    # run main function
    main(
        folder_path = inputs['folder_path'],
        graph_pickle = inputs['graph_pickle'],
        coverage_pickle = inputs['coverage_pickle'],
        id_attribute = inputs['id_attribute'],
        length_attribute = inputs['length_attribute'],
        N = inputs['N'],
        num_iterations = inputs['num_iterations'],
        random_seed = inputs.get('random_seed', None),
        )
