import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import time
from devices.endDevices import EndDevices
from devices.router import Router
from devices.switch import Switch
from layers.dataLayer import DataLayer
from processing.process import Process

class NetworkLayer:

    def __init__(self, routers):
        self.routers = routers  # List of Router objects
        self.switch1 = Switch()
        self.switch2 = Switch()
        self.end_device = EndDevices()
        self.device_list = []
        self.process_list = []
        self.process_map = {}
        self.mapp = {}
        self.message = ""
        self.ip = ""
        self.scheme = 0
        self.data_layer_obj = DataLayer()
        self.router_obj = Router()

    def create_nid(self):
        return self.router_obj.generate_NID()

    def stop_simulation(self):
        exit(0)

    def start_simulation(self):
        self.run()

    def same_network(self, sender_ip, receiver_ip):
        sender_network = sender_ip.rsplit('.', 1)[0]  # Get the network part
        receiver_network = receiver_ip.rsplit('.', 1)[0]  # Get the network part
        return sender_network == receiver_network  # Check if they are in the same network

    def find_route(self, sender_ip, receiver_ip):
        print(f"Finding route from {sender_ip} to {receiver_ip}...")
        
        # Check each router for the next hop
        for router in self.routers:
            if router.same_NID(sender_ip, receiver_ip):
                print(f"Direct route found via Router {router.get_id()}")
                return [receiver_ip]  # Direct delivery if in the same network
            
            # Check the routing table for the next hop
            next_hop = router.get_next_hop(receiver_ip)
            if next_hop:
                print(f"Route found: Next hop is {next_hop} via Router {router.get_id()}")
                return [next_hop]  # Return the next hop IP address
        
        print("No route found. Using default route.")
        return ["Default_Router_IP"]  # Fallback to a default router IP if no route is found

    def route_packet(self, packet):
        if self.same_network(packet['sender_ip'], packet['receiver_ip']):
            return [packet['receiver_ip']]  # Direct delivery
        else:
            return self.find_route(packet['sender_ip'], packet['receiver_ip'])  # Route through routers

    class Pair:
        def __init__(self, first, second):
            self.first = first
            self.second = second

        def get_first(self):
            return self.first

        def get_second(self):
            return self.second

    def run(self):

        while True:
            print("\nSelect routing scheme : ")
            print("1. Static Routing")
            print("2. Dynamic Routing")
            self.scheme = int(input())

            # Static Routing
            if self.scheme == 1:

                router1 = Router()
                router2 = Router()
                router = Router()

                nid1 = self.create_nid()
                nid2 = self.create_nid()
                nid3 = self.create_nid()
                nid4 = self.create_nid()

                router1.set_address(nid1, nid2, "", self.data_layer_obj.generate_mac_address(), self.data_layer_obj.generate_mac_address(), "")
                router2.set_address(nid3, nid4, "", self.data_layer_obj.generate_mac_address(), self.data_layer_obj.generate_mac_address(), "")

                ipv4 = []
                for i in range(4):
                    if i < 2:
                        self.ip = router.generate_classless_IP(nid1)
                        ipv4.append(self.ip)
                    else:
                        self.ip = router.generate_classless_IP(nid4)
                        ipv4.append(self.ip)

                # End device list in Network 1
                self.device_list.append(EndDevices(1, self.data_layer_obj.generate_mac_address(), ipv4[0]))
                self.device_list.append(EndDevices(2, self.data_layer_obj.generate_mac_address(), ipv4[1]))
                # End device list in Network 2
                self.device_list.append(EndDevices(4, self.data_layer_obj.generate_mac_address(), ipv4[2]))
                self.device_list.append(EndDevices(5, self.data_layer_obj.generate_mac_address(), ipv4[3]))

                router1.connect_switch(self.switch1)
                router2.connect_switch(self.switch2)

                for i in range(4):
                    p = Process()
                    self.process_list.append(p)

                for i in range(4):
                    self.process_map[self.process_list[i].assign_port_number(self.process_map)] = self.process_list[i]

                sender = int(input("Sender (1-4): "))
                receiver = int(input("Receiver (1-4): "))
                if sender == receiver:
                    print("Sender and receiver can't be the same")
                    continue

                app_protocol = int(input("\nChoose a protocol :\n1. HTTP\n2. DNS\n"))

                self.message = input("\nEnter a message: ")

                sender_device = self.device_list[sender - 1]
                receiver_device = self.device_list[receiver - 1]
                sender_device.put_data(self.message)

                source_ip = sender_device.get_ip()
                destination_ip = receiver_device.get_ip()

                random_port = random.randint(0, 3)
                source_port = self.process_list[random_port].assign_port_number(self.process_map)
                destination_port = 80 if app_protocol == 1 else 53

                print(f"Source IP : {source_ip}")
                print(f"Source Port : {source_port}")
                print(f"Destination IP : {destination_ip}")
                print(f"Destination Port : {destination_port}")

                time.sleep(4)

                # Initialize ARP cache
                for i in range(4):
                    device_ip = self.device_list[i].get_ip()
                    device_mac = self.device_list[i].get_mac()
                    self.device_list[i].arp_cache(device_ip, device_mac)

                self.switch1.connected_devices.append(self.device_list[0])
                self.switch1.connected_devices.append(self.device_list[1])
                self.switch2.connected_devices.append(self.device_list[2])
                self.switch2.connected_devices.append(self.device_list[3])
                sender_device.print_arp_cache()

                # Check if sender and receiver are in the same network
                check = router.same_NID(source_ip, destination_ip)
                network = router1.network_no(source_ip)

                if check:
                    # Both sender and receiver are in the same network
                    is_present = sender_device.arp.get(destination_ip)

                    if is_present is None or is_present == "":
                        # Send ARP request
                        print("\nSender sends ARP request")
                        if network == 1:
                            destination_mac = self.switch1.broadcast_arp(destination_ip, router, network)
                            sender_device.arp_cache(destination_ip, destination_mac)

                            print("Updated ARP cache :")
                            sender_device.print_arp_cache()

                            time.sleep(1)

                            print("\nLog of TCP Packets sent from client to server\n")
                            print("Protocol used : Selective Repeat\n")
                            self.end_device.selective_repeat()
                            print()

                            self.switch1.send_message(sender_device, destination_ip)

                            if destination_port == 80:
                                self.end_device.http()
                            else:
                                self.end_device.dns()
                        elif network == 2:
                            destination_mac = self.switch2.broadcast_arp(destination_ip, router, network)
                            sender_device.arp_cache(destination_ip, destination_mac)

                            print("Updated ARP cache :")
                            sender_device.print_arp_cache()

                            time.sleep(1)

                            print("Log of TCP Packets sent from client to server\n")
                            print("Protocol used : Selective Repeat\n")
                            self.end_device.selective_repeat()
                            print()

                            self.switch2.send_message(sender_device, destination_ip)

                            if destination_port == 80:
                                self.end_device.http()
                            else:
                                self.end_device.dns()
                    else:
                        if network == 1:
                            print("\nLog of TCP Packets sent from client to server\n")
                            print("Protocol used : Selective Repeat\n")
                            self.end_device.selective_repeat()
                            print()

                            self.switch1.send_message(sender_device, destination_ip)

                            if destination_port == 80:
                                self.end_device.http()
                            else:
                                self.end_device.dns()
                        elif network == 2:
                            print("\nLog of TCP Packets sent from client to server\n")
                            print("Protocol used : Selective Repeat\n")
                            self.end_device.selective_repeat()
                            print()

                            self.switch2.send_message(sender_device, destination_ip)

                            if destination_port == 80:
                                self.end_device.http()
                            else:
                                self.end_device.dns()

                else:
                    # Sender and receiver are in different networks
                    result = sender_device.arp.get(destination_ip)

                    if result is None or result == "":
                        print("\nSender sends ARP request")
                        if network == 1:
                            destination_mac = self.switch1.broadcast_arp(destination_ip, router1, network)
                            sender_device.arp_cache(router1.IP1, destination_mac)

                            print("Updated ARP cache :")
                            sender_device.print_arp_cache()

                            router1.routing_table(router2, 1)
                            print()
                            router1.print_routing_table(network)

                            router1.arp_cache(router1.IP1, router1.MAC1)
                            router1.arp_cache(router1.IP2, router1.MAC2)
                            router1.arp_cache(router2.IP1, router2.MAC1)
                            print()
                            router1.print_arp_cache(network)

                            router1.routing_decision(destination_ip)

                            router2.routing_table(router1, 2)
                            print()
                            router2.print_routing_table(2)

                            router2.arp_cache(router2.IP1, router2.MAC1)
                            router2.arp_cache(router2.IP2, router2.MAC2)
                            router2.arp_cache(router1.IP2, router1.MAC2)
                            print()
                            router2.print_arp_cache(2)
                            print()

                            print("Router 2 sends ARP request")
                            destination_mac = self.switch2.broadcast_arp(destination_ip, router, 1)
                            sender_device.arp_cache(destination_ip, destination_mac)

                            time.sleep(4)
                            print("Log of TCP Packets sent from client to server\n")
                            print("Protocol used : Selective Repeat\n")
                            self.end_device.selective_repeat()
                            print()

                            self.switch2.send_message(sender_device, destination_ip)

                            if destination_port == 80:
                                self.end_device.http()
                            else:
                                self.end_device.dns()

                        elif network == 2:
                            destination_mac = self.switch2.broadcast_arp(destination_ip, router2, network)
                            sender_device.arp_cache(router2.IP2, destination_mac)

                            print("Updated ARP cache :")
                            sender_device.print_arp_cache()

                            router2.routing_table(router1, 2)
                            print()
                            router2.print_routing_table(network)

                            router2.arp_cache(router2.IP1, router2.MAC1)
                            router2.arp_cache(router2.IP2, router2.MAC2)
                            router2.arp_cache(router1.IP2, router2.MAC2)
                            print()
                            router2.print_arp_cache(network)

                            router2.routing_decision(destination_ip)

                            router1.routing_table(router2, 1)
                            print()
                            router1.print_routing_table(1)

                            print("Log of TCP Packets sent from client to server\n")
                            print("Protocol used : Selective Repeat\n")
                            self.end_device.selective_repeat()
                            print()

                            self.switch2.send_message(sender_device, destination_ip)

                            if destination_port == 80:
                                self.end_device.http()
                            else:
                                self.end_device.dns()

                time.sleep(4)

            # Dynamic Routing
            elif self.scheme == 2:
                print("\nDynamic Routing")
                scheme = int(input("Enter the scheme (2 for RIP): "))

                if scheme == 2:
                    print("\nProtocol Used: RIP (Routing Information Protocol)\n")

                num_vertices = int(input("Enter the number of Routers: "))

                if num_vertices > 15:
                    print("Maximum Hop Count in RIP is 15")
                    print("Enter a valid number")
                    continue

                routers = []
                edges = []
                num_edges = int(input("\nEnter the number of links: "))

                print("\nInput router number as per 0-based indexing")
                for i in range(num_edges):
                    print(f"Edge {i + 1}:")
                    source = int(input("First Router: "))
                    router1 = Router(source)

                    destination = int(input("Second Router: "))
                    router2 = Router(destination)

                    routers.append((router1, router2))

                for router_pair in routers:
                    router1, router2 = router_pair
                    edges.append([router1.get_id(), router2.get_id(), 1])
                    edges.append([router2.get_id(), router1.get_id(), 1])
                    
                router = Router()
                router.initial_routing_table(edges, num_vertices)
                print()

                for source in range(num_vertices):
                    router.rip(edges, num_vertices, source)

            else:
                print("Invalid Choice")
                continue
            break


# if __name__ == "__main__":
#     network_layer_obj = NetworkLayer()
#     network_layer_obj.start_simulation()
