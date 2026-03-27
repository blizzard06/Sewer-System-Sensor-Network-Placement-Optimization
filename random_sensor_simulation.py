"""
Random Sensor Placement Simulation (Baseline)

Randomly selects N sensor locations from the sewer network junctions
many times and evaluates each solution by the total length of covered pipes.
Serves as a baseline to compare against optimization methods.

Inputs:
    - graph: NetworkX DiGraph with edges containing 'pipe_id' and 'length' attributes
    - coverage_dict: {junction_id: [list of reachable pipe_ids]}

Output:
    - Best random solution (junction selection) and its objective value
"""

import random
import networkx as nx


def calculate_objective(junction_selection, coverage_dict, pipe_lengths):
    """Calculate total length of covered pipes for a given sensor placement.

    Args:
        junction_selection: Iterable of junction IDs where sensors are placed.
        coverage_dict: {junction_id: [list of reachable pipe_ids]}.
        pipe_lengths: {pipe_id: length in meters}.

    Returns:
        Tuple of (total_distance_covered, all_covered_pipes set).
    """
    all_covered_pipes = set()
    for junction in junction_selection:
        covered_pipes = coverage_dict.get(junction, [])
        all_covered_pipes.update(covered_pipes)

    total_distance_covered = sum(pipe_lengths[pipe] for pipe in all_covered_pipes)
    return total_distance_covered, all_covered_pipes


def get_pipe_lengths(graph):
    """Extract pipe lengths from graph edges.

    Args:
        graph: NetworkX DiGraph where each edge has 'pipe_id' and 'length' attributes.

    Returns:
        Dictionary mapping pipe_id to length.
    """
    pipe_lengths = {}
    for u, v, data in graph.edges(data=True):
        pipe_id = data["pipe_id"]
        length = data["length"]
        pipe_lengths[pipe_id] = length
    return pipe_lengths


def random_sensor_simulation(graph, coverage_dict, N, num_iterations=1000, seed=None):
    """Run random sensor placement simulation.

    Args:
        graph: NetworkX DiGraph with edge attributes 'pipe_id' and 'length'.
        coverage_dict: {junction_id: [list of reachable pipe_ids]}.
        N: Number of sensors to deploy.
        num_iterations: Number of random samples to try (default 1000).
        seed: Random seed for reproducibility (default None).

    Returns:
        Dictionary with keys:
            - best_solution: list of junction IDs for best sensor placement
            - best_objective: total pipe length covered by best solution
            - best_covered_pipes: set of pipe IDs covered by best solution
            - all_objectives: list of objective values from all iterations
            - total_pipe_length: total length of all pipes in the network
            - coverage_percentage: percentage of total pipe length covered
    """
    if seed is not None:
        random.seed(seed)

    all_junctions = list(graph.nodes())
    num_junctions = len(all_junctions)

    if N > num_junctions:
        raise ValueError(
            f"N ({N}) cannot exceed the number of junctions ({num_junctions})"
        )

    pipe_lengths = get_pipe_lengths(graph)
    total_pipe_length = sum(pipe_lengths.values())

    best_solution = None
    best_objective = 0
    best_covered_pipes = set()
    all_objectives = []

    for i in range(num_iterations):
        junction_selection = random.sample(all_junctions, N)

        total_distance_covered, covered_pipes = calculate_objective(
            junction_selection, coverage_dict, pipe_lengths
        )

        all_objectives.append(total_distance_covered)

        if total_distance_covered > best_objective:
            best_solution = junction_selection
            best_objective = total_distance_covered
            best_covered_pipes = covered_pipes

        if (i + 1) % 100 == 0:
            print(
                f"Iteration {i + 1}/{num_iterations} | "
                f"Current best: {best_objective:.2f}m | "
                f"Coverage: {best_objective / total_pipe_length * 100:.2f}%"
            )

    coverage_percentage = (best_objective / total_pipe_length * 100) if total_pipe_length > 0 else 0

    print("\n--- Random Simulation Results ---")
    print(f"Number of sensors (N): {N}")
    print(f"Number of iterations: {num_iterations}")
    print(f"Total pipe length in network: {total_pipe_length:.2f}m")
    print(f"Best objective (covered length): {best_objective:.2f}m")
    print(f"Coverage: {coverage_percentage:.2f}%")
    print(f"Number of pipes covered: {len(best_covered_pipes)}/{len(pipe_lengths)}")
    print(f"Average objective across iterations: {sum(all_objectives) / len(all_objectives):.2f}m")
    print(f"Worst objective: {min(all_objectives):.2f}m")

    return {
        "best_solution": best_solution,
        "best_objective": best_objective,
        "best_covered_pipes": best_covered_pipes,
        "all_objectives": all_objectives,
        "total_pipe_length": total_pipe_length,
        "coverage_percentage": coverage_percentage,
    }


if __name__ == "__main__":
    # ---- Example usage ----
    # Replace this section with your actual graph and coverage_dict loading code.

    # Build a small example graph
    G = nx.DiGraph()
    G.add_edge(1, 2, pipe_id="P1", length=100.0)
    G.add_edge(2, 3, pipe_id="P2", length=150.0)
    G.add_edge(3, 4, pipe_id="P3", length=200.0)
    G.add_edge(4, 5, pipe_id="P4", length=120.0)
    G.add_edge(2, 5, pipe_id="P5", length=180.0)

    # Example coverage dictionary
    coverage_dict = {
        1: ["P1"],
        2: ["P1", "P2", "P5"],
        3: ["P2", "P3"],
        4: ["P3", "P4"],
        5: ["P4", "P5"],
    }

    N = 2
    results = random_sensor_simulation(G, coverage_dict, N, num_iterations=100, seed=42)

    print(f"\nBest sensor locations: {results['best_solution']}")
