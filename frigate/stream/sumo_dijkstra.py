import heapq
import os
import sys
from configuration import SUMO_ROADNET_PATH

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], "tools")
    sys.path.append(tools)
else:
    print("please declare environment variable 'SUMO_HOME'")
import sumolib

def shortest(v, previous, path):
    ''' make shortest path from v.previous'''
    if previous[v]:
        path.append(previous[v])
        shortest(previous[v], previous, path)
    return

def get_outgoing_neighbor_ids(net, node_id):
    outgoing_edges = net.getNode(node_id).getOutgoing()
    return [edge.getToNode().getID() for edge in outgoing_edges]


def are_nodes_connected(net, node_id, nei_node_id):
    outgoing_edges = net.getNode(node_id).getOutgoing()
    connected = False
    for edge in outgoing_edges:
        if edge.getToNode().getID() == nei_node_id:
            connected = True            
            break
    if connected:
        return True
    else:
        return False

def get_outgoing_edge_id(net, node_id, nei_node_id):
    outgoing_edges = net.getNode(node_id).getOutgoing()
    outgoing_edge_id = None
    for edge in outgoing_edges:
        if edge.getToNode().getID() == nei_node_id:
            outgoing_edge_id = edge.getID()
            break
    assert outgoing_edge_id != None
    return outgoing_edge_id


def get_outgoing_edge_weight(net, node_id, nei_node_id):
    outgoing_edge_id = get_outgoing_edge_id(net, node_id, nei_node_id)
    return net.getEdge(outgoing_edge_id).getLength()

# adapted from:
# https://www.bogotobogo.com/python/python_Dijkstras_Shortest_Path_Algorithm.php


def dijkstra(net, source_node_id):

    node_ids = [node.getID() for node in net.getNodes()]
    #print(node_ids)

    distance = dict.fromkeys(node_ids, float("inf"))
    previous = dict.fromkeys(node_ids, None)
    visited = dict.fromkeys(node_ids, False)

    # Set the distance for the start node to zero
    distance[source_node_id] = 0.0

    # Put tuple pair into the priority queue
    unvisited_queue = [(distance[v], v) for v in node_ids]
    heapq.heapify(unvisited_queue)

    while len(unvisited_queue) > 0:
        # Pops a vertex with the smallest distance
        uv = heapq.heappop(unvisited_queue)
        current = uv[1]
        #print(f"current {current}")
        visited[current] = True

        # for next in v.adjacent:
        for nextt in get_outgoing_neighbor_ids(net, current):
            # if visited, skip
            if visited[nextt]:
                continue

            new_dist = distance[current] + \
                get_outgoing_edge_weight(net, current, nextt)

            if new_dist < distance[nextt]:
                distance[nextt] = new_dist
                previous[nextt] = current

        # Rebuild heap
        # 1. Pop every item
        while len(unvisited_queue) > 0:
            heapq.heappop(unvisited_queue)
        # 2. Put all vertices not visited into the queue
        unvisited_queue = [(distance[v], v)
                           for v in node_ids if not visited[v]]
        heapq.heapify(unvisited_queue)


        #print(distance)
        #print(visited)

    return previous  # return the shortest-path tree

def get_single_source_all_dest_paths(net, source_node_id):
    all_sp = {}
    previous = dijkstra(net, source_node_id)
    node_ids = [node.getID() for node in net.getNodes()] 
    for target_id in node_ids:
        path = [target_id]
        shortest(target_id, previous, path) 
        path.reverse()
        assert path[0] == source_node_id and path[-1] == target_id, f"source = {source_node_id} target = {target_id} path = {path}"
        all_sp[target_id] = path
    return all_sp
        

if __name__ == "__main__":

    net = sumolib.net.readNet(SUMO_ROADNET_PATH)
    print(get_single_source_all_dest_paths(net, "n4"))
    print("done.")

