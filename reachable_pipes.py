'''
the objective of this script is to read in the pickle file of a directed networkx graph
the script will loop over every junction in the graph
and seach for all reachable nodes within a threshold distance provided by the user
from the reachable nodes, we need to convert this into all reachable PIPES
the analysis will return a dictionary with all results
--
inputs
- pickled networkx object, with the edges weighted using pipe length
- user defined threshold distance
outputs
- dictionary with format {node ID: [list of OTHER reachable pipe IDs]}

- the entire pipe has to be within the reachable distance for a junction be included
'''


# import required packages
import os, code, yaml, argparse
import pickle 
import networkx as nx


# reachable nodes
def reachable_node_list(
    graph, 
    source, 
    max_distance, 
    weight):
    # call function
    lengths = nx.single_source_dijkstra_path_length(
        graph,
        source=source,
        cutoff=max_distance,
        weight=weight
    )
    return list(lengths.keys())



def pipes_in_induced_subgraph(
    graph, 
    nodes, 
    edge_id_attr=None):
    """
    Given a list of nodes, return all edges (pipes) in the induced subgraph.

    Parameters
    ----------
    G : networkx.Graph or DiGraph
        Input graph.
    nodes : iterable
        List or set of nodes defining the subgraph.
    edge_id_attr : str, optional
        If provided, return this edge attribute (e.g., pipe ID) instead of node pairs.

    Returns
    -------
    list
        List of edges (u, v) or list of edge attribute values if edge_id_attr is provided.
    """
    # Create induced subgraph
    subG = graph.subgraph(nodes)
    
    if edge_id_attr:
        # Return specific edge attribute (e.g., pipe IDs)
        return [
            data.get(edge_id_attr)
            for _, _, data in subG.edges(data=True)
            if edge_id_attr in data
        ]
    else:
        # Return edge tuples
        return list(subG.edges())


# main function here
def main(
        folder_path,
        graph_pickle,
        id_attribute,
        length_attribute,
        search_limit,
    ):
    #code.interact(local = dict(globals(), **locals()))

    # set folder
    os.chdir(folder_path)

    'step 1 - read graph from pickle path'
    # this is a directed graph
    with open(graph_pickle, 'rb') as f:
        G = pickle.load(f)

    'step 2 - initialize output dictionary'
    # key is the junction ID
    # values is the list of reachable pipe IDs, from the junction source
    output = {n: None for n in G.nodes}

    'step 2b - loop over all nodes in the graph, and perform a distance search'
    for n in G.nodes:
        # use distance search function from networkx
        # expect reachable nodes with format [n1, n2, etc.]

        reachable_nodes = reachable_node_list(
            graph = G, 
            source = n, 
            max_distance = search_limit, 
            weight = length_attribute
            )

        # from reachables nodes, induce reachable pipes
        # excpect reachable pipes with format [pipe_id, pipe_id] or [(n1, n2), (n2, n3)]
        reachable_pipes = pipes_in_induced_subgraph(
            graph = G, 
            nodes = reachable_nodes, 
            edge_id_attr = id_attribute
            )
        '''
        pipes_in_induced_subgraph(
            graph = G, 
            nodes = reachable_nodes, 
            edge_id_attr = None
            )
        '''
        # attach solution to dictionary
        output[n] = reachable_pipes
        # print outputs
        print('source node: ', n)
        print('reachable links: ', reachable_pipes)


    'step 3 - write output'
    # using pickling again
    with open('reachable_pipes_output.pickle', 'wb') as file:
        pickle.dump(output, file)

    code.interact(local = dict(globals(), **locals()))

    # exit function
    return


# command line run
if __name__ == "__main__":

    # use argparse to read config file
    parser = argparse.ArgumentParser(description="generate reachable pipes")
    parser.add_argument("config_file", type=str)
    args = parser.parse_args()
    # open config yaml file
    with open(args.config_file, "r") as stream:
        config_data = yaml.safe_load(stream)
    # filter to the commands
    inputs = config_data['Inputs']['reachable_pipes']

    # run main function
    main(
        folder_path = inputs['folder_path'],
        graph_pickle = inputs['graph_pickle'],
        id_attribute = inputs['id_attribute'],
        length_attribute = inputs['length_attribute'],
        search_limit = inputs['search_limit']
        )

