class Switch:
    def __init__(self, switch_id=None, message=None):
        self.switch_id = switch_id if switch_id else 0
        self.hub_device_map = {}
        self.mac_table = {}
        self.connected_hubs = []
        self.data = message if message else ""
        self.connected_devices = []

    def get_id(self):
        return self.switch_id

    def topology(self, device):
        self.connected_devices.append(device)

    def print_connection(self, index):
        print(f"Connection successfully established between switch & device with MAC Address: {self.connected_devices[index].get_mac()}")

    def topology_hub(self, hub):
        self.connected_hubs.append(hub)

    def hub_print_connection(self, index):
        if index < len(self.connected_hubs):
            print(f"Connection successfully established between switch & hub with Hub ID: {self.connected_hubs[index].get_id()}")
        else:
            print(f"Invalid index: {index}, no hub at this index.")


    def get_devices(self):
        return self.connected_devices

    def hub_to_device_map(self, hub_id, devices):
        device_ids = [device.get_id() for device in devices]
        self.hub_device_map[hub_id] = device_ids

    def print_hub_to_device_map(self):
        print("Mapping of Hub and End devices, stored in switch")
        for hub_id, device_ids in self.hub_device_map.items():
            print(f"End devices {','.join(map(str, device_ids))} are connected to hub {hub_id + 1}")
        print()

    def find_hub_for_device(self, device_id):
        for hub_id, device_ids in self.hub_device_map.items():
            if device_id in device_ids:
                return hub_id
        return -1

    def update_mac_table(self):
        for device in self.connected_devices:
            self.mac_table[device.get_id()] = device.get_mac()


    def receive_data(self, sender, receiver, message):
        self.data = message
        source_hub = self.find_hub_for_device(sender)
        destination_hub = self.find_hub_for_device(receiver)

        # Debugging information
        print(f"Switch received \"{message}\" from hub {source_hub + 1}")
        print(f"Destination hub: {destination_hub + 1}, Total connected hubs: {len(self.connected_hubs)}")

        # Ensure destination_hub is within bounds
        if destination_hub < len(self.connected_hubs):
            self.connected_hubs[destination_hub].data = message
            print(f"Switch sends {message} to hub {destination_hub + 1}")
        else:
            print(f"Error: Destination hub index {destination_hub} is out of range.")

        return destination_hub


    def transmission(self, devices, sender, receiver):
        print("\nTransmission Status :")
        token = self.connected_devices[sender - 1].token
        data = self.connected_devices[sender - 1].send_data()  # Ensure send_data() exists in device class
        if token:
            print(f"{data} sent successfully from device with MAC {self.mac_table[sender]} to {self.mac_table[receiver]} via switch")


    def send_ack(self, sender):
        ack = self.connected_devices[sender - 1].ack
        if ack:
            print(f"ACK was successfully received by sender with MAC Address {self.mac_table[sender]}")
        else:
            print("ACK not received by sender")

    def receive_ack(self, destination_hub):
        if self.connected_hubs[destination_hub].ack:
            print(f"Hub {destination_hub + 1} sends ACK to switch")

    def send_ack_to_hub(self, source_hub):
        self.connected_hubs[source_hub].ack = True
        print(f"Switch sends ACK to Hub {source_hub + 1}")

    def broadcast_arp(self, destination_ip, router, network):
        print("\nSwitch broadcast ARP request : ")
        print(f"Who is {destination_ip} ?")

        for device in self.connected_devices:
            result = device.arp.get(destination_ip)  # Ensure device.arp exists
            if result:
                print(f"ARP Reply :- Source IP : {device.get_ip()} Source MAC : {device.get_mac()}")
                return device.get_mac()

        # If not found in any device, return router's MAC based on network
        if network == 1:
            print(f"ARP Reply by Default Gateway : Source IP : {router.IP1} Source MAC : {router.MAC1}")
            return router.MAC1
        else:
            print(f"ARP Reply by Default Gateway : Source IP : {router.IP2} Source MAC : {router.MAC2}")
            return router.MAC2

    # def broadcast_arp(self, destination_ip, router, network):
    #     # Look for the device in the connected devices
    #     for device in self.connected_devices:
    #         if device.ip_address == destination_ip:
    #             return device.mac_address
    #     # If device not found, return router's MAC address
    #     return router.MAC1  # You might want to check if the router MAC is returned correctly


    def send_message(self, device, destination_ip):
        print()
        destination_mac = device.arp.get(destination_ip)
        source_mac = device.get_mac()
        print(f"{device.send_data()} sent successfully from device with MAC {source_mac} to {destination_mac}")
