import os, code, pickle, argparse, yaml, uuid
import geopandas as gpd
import pandas as pd
import networkx as nx # type: ignore
from shapely.geometry import LineString, MultiLineString
import fiona


def main(
    folder_path: str,
    input_kml: str,
    crs_code: str,
    id_col: str,
    ):

    # set working dir
    os.chdir(folder_path)


    # 1. Read the sewer file
    pipes = gpd.read_file(input_kml)
    # 2. Project to a CRS in meters
    pipes = pipes.to_crs(crs_code)
    print("Reading Completed")
    # check if unique column exists, if NOT none
    if id_col is not None:
        assert(len(pipes) == len(pipes[id_col].unique()))
    else:
        # generate unique identifier
        pipes['identifier'] = pd.Series([str(uuid.uuid4()) for _ in range(len(pipes))])

    
    # 3. Calculate pipe lengths in meters
    pipes["LengthM"] = pipes.length

    # 4. Create directed graph
    G = nx.DiGraph()

    # Dictionary to assign a unique node ID to each coordinate
    coord_to_node = {}
    next_node_id = 0

    # 5. Loop through each pipe and add it as an edge
    for idx, row in pipes.iterrows():
        #print(idx)
        geom = row.geometry
        # Handle both LineString and MultiLineString
        if isinstance(geom, LineString):
            lines = [geom]
        elif isinstance(geom, MultiLineString):
            lines = list(geom.geoms)
        else:
            continue

        for line in lines:
            coords = list(line.coords)
            # extract last and first coordinates from the line object
            start_coord = coords[0]
            end_coord = coords[-1]

            # check if the start coordinate is part of dictionary
            # hash, links (x, y) coordinate to node number
            if start_coord not in coord_to_node.keys():
                # if its not in dictionary keys, add it to the dictionary
                coord_to_node[start_coord] = next_node_id
                # increment to next number
                next_node_id += 1

            if end_coord not in coord_to_node.keys():
                # if its not in dictionary keys, add it to the dictionary
                coord_to_node[end_coord] = next_node_id
                # increment to next number
                next_node_id += 1    
    
            # once start and end coordinate are part of the dictionary
            # call the dictionary to return node number
            start_node = coord_to_node[start_coord]          
            end_node = coord_to_node[end_coord] 
            # add edge to the directed graph object
            if id_col is not None:
                G.add_edge(
                    start_node,
                    end_node,
                    weight=row["LengthM"], # add weight attribute (length in meters)
                    length=row["LengthM"], # add length attribute (length in meters)
                    identifier=row[id_col],
                    geometry=line
                )
            else:
                G.add_edge(
                    start_node,
                    end_node,
                    weight=row["LengthM"], # add weight attribute (length in meters)
                    length=row["LengthM"], # add length attribute (length in meters)
                    identifier=row['identifier'],
                    geometry=line
                )

    # look at individual edge
    # G.get_edge_data(11530, 11531)

    print("Number of nodes:", G.number_of_nodes())
    print("Number of edges:", G.number_of_edges())
    # save the graph object
    with open('graph.pickle', 'wb') as f:
        pickle.dump(G, f)
    # write gdf to pickle
    pipes.to_pickle('updated_input_graph.kml')


    # heres how to read it back in future code
    '''
    with open('graph.pickle', 'rb') as f:
        loaded_graph = pickle.load(f)
    '''
    '''
    # Define the node for which to find edges
    target_node = 3

    # 2. Get all edges connected to the target node
    # By default, this returns 2-tuples (u, v)
    edges_of_node = G.edges(nbunch=target_node)

    print(f"Edges connected to node {target_node}:")
    # 3. Print the edges
    for edge in edges_of_node:
        print(edge)
    '''


    print('done')
    # exit function
    return


# run from command line
if __name__ == "__main__":

    # use argparse to read config file
    parser = argparse.ArgumentParser(description="generate pickle graph")
    parser.add_argument("config_file", type=str)
    args = parser.parse_args()
    # open config yaml file
    with open(args.config_file, "r") as stream:
        config_data = yaml.safe_load(stream)
    # filter to the commands
    inputs = config_data['Inputs']['create_graph']

    # run main function
    main(
        folder_path = inputs['folder_path'],
        input_kml = inputs['input_kml'],
        crs_code = inputs['crs_code'],
        id_col = inputs['id_col'],
        )
