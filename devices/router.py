import random
from devices.endDevices import EndDevices
from devices.switch import Switch

class Router(EndDevices):
    INF = 99999

    def __init__(self, id=None):
        self.id = id
        self.IP1 = None
        self.IP2 = None
        self.IP3 = None
        self.MAC1 = None
        self.MAC2 = None
        self.MAC3 = None
        self.connectedDevices = []
        self.routingTable = {}
        self.routerEndDeviceList = []
        self.arp = {}  # Adding ARP cache to Router class

    def get_id(self):
        return self.id  # Return the router's unique ID

    def set_address(self, IP1, IP2, IP3, MAC1, MAC2, MAC3):
        self.IP1 = IP1
        self.IP2 = IP2
        self.IP3 = IP3
        self.MAC1 = MAC1
        self.MAC2 = MAC2
        self.MAC3 = MAC3

    def topology(self, endD):
        self.routerEndDeviceList.append(endD)

    def connect_switch(self, switch):
        self.connectedDevices.append(switch)

    def random(self, min, max):
        return random.randint(min, max)

    def generate_NID(self):
        NID = ""
        for i in range(4):
            octet = self.random(0, 255)
            if i < 2:
                NID += str(octet) + "."
            else:
                NID += "0."
        return NID[:-1]  # Remove the last dot

    def generate_classless_IP(self, NID):
        NID = NID[:-1]  # Remove last character
        for i in range(4):
            octet = self.random(0, 255)
            if i == 3:
                NID += str(octet) + "/24"
            else:
                NID += str(octet) + "."
        return NID

    def same_NID(self, sourceIp, destinationIp):
        return sourceIp[:6] == destinationIp[:6]

    def network_no(self, sourceIp):
        return 1 if self.IP1[:6] == sourceIp[:6] else 2

    def routing_table(self, r, source):
        self.routingTable[self.IP1] = ("1", "0")
        self.routingTable[self.IP2] = ("2", "0")
        if source == 1:
            self.routingTable[r.IP2] = ("2", r.IP1)
        else:
            self.routingTable[r.IP1] = ("2", r.IP2)

    def get_next_hop(self, destination_ip):
        for network in self.routingTable:
            if destination_ip.startswith(network):
                return self.routingTable[network][1]  # Return the next hop IP
        return None  # No route found

    def print_routing_table(self, source):
        print(f"\nRouting Table of Router {source}")
        print(f"{'NID':<15} {'Interface':<12} {'Next Hop':<10}")
        print("-" * 39)
        for key, value in self.routingTable.items():
            print(f"{key:<15} {value[0]:<12} {value[1]:<10}")

    def routing_decision(self, destinationIp):
        for key, value in self.routingTable.items():
            if self.same_NID(key, destinationIp):
                print(f"Sending packet to Network {key} on interface {value[0]}")
                break

    def print_arp_cache(self, source):
        print(f"\nARP Cache of Router {source} is as :\n")
        print("IP\t\tMAC\n")
        for key, value in self.arp.items():
            print(f"{key}\t{value}\n")

    def rip(self, edges, numVertices, source):
        # Initialize distance and nextHop arrays
        distance = [self.INF] * numVertices
        distance[source] = 0
        nextHop = [-1] * numVertices

        # Validate edges
        print(f"Validating edges...")
        for edge in edges:
            u, v, weight = edge
            if u < 0 or u >= numVertices or v < 0 or v >= numVertices:
                raise ValueError(f"Invalid edge: ({u}, {v}). Vertex index out of bounds.")

        print(f"Edges: {edges}")
        print(f"Number of vertices: {numVertices}")
        print(f"Source router: {source}")

        # Bellman-Ford algorithm
        for _ in range(1, numVertices):
            for edge in edges:
                u, v, weight = edge
                if distance[u] != self.INF and distance[u] + weight < distance[v]:
                    distance[v] = distance[u] + weight
                    nextHop[v] = u

        # Print final routing table
        print("\nFinal Routing Table:")
        print(f"Routing Table for Router {source}:")
        print("Destination\tNext Hop\tCost")
        for i in range(numVertices):
            print(f"R{i}\t\t", end="")
            if distance[i] == self.INF:
                print("-\t\t", end="")
            else:
                if i == source:
                    print(f"-\t\t{distance[i]}")
                else:
                    if nextHop[i] != -1 and source != nextHop[i]:
                        print(f"R{nextHop[i]}\t\t", end="")
                    else:
                        print("-\t\t", end="")
                    print(distance[i])


    def initial_routing_table(self, edges, numVertices):
        print("Initial Routing Tables:")
        for source in range(numVertices):
            print(f"Routing table for Router {source}:")
            print("Destination\tNext Hop\tCost")
            for i in range(numVertices):
                print(f"R{i}\t\t", end="")
                if i == source:
                    print("-\t\t0")
                else:
                    directlyConnected = False
                    for edge in edges:
                        if edge[0] == source and edge[1] == i:
                            print(f"-\t\t{edge[2]}")
                            directlyConnected = True
                            break
                    if not directlyConnected:
                        print("-\t\t-")
            print()

class Pair:
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def get_first(self):
        return self.first

    def get_second(self):
        return self.second
