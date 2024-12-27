import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
from devices.endDevices import EndDevices
from devices.hub import Hub
from devices.switch import Switch

class DataLayer:

    def generate_mac_address(self):
        """Generate a random MAC address."""
        return ':'.join(['{:02X}'.format(random.randint(0, 255)) for _ in range(6)])
    
    def create_packet(self, sender_ip, receiver_ip, message):
        return {
            'sender_ip': sender_ip,
            'receiver_ip': receiver_ip,
            'message': message
        }

    def run(self, choice, hub_size):
        while True:
            no_of_device1, sender, receiver = 0, 0, 0
            data = ""
            device_list1 = []
            mapp = {}
            hub = Hub()
            end_device = EndDevices()
            switch1 = Switch()
            select = 0

            if choice == 1:
                no_of_device1 = int(input("\nEnter the number of end devices: "))

                if no_of_device1 < 2:
                    print("There should be at least two devices. Enter a valid number.")
                    continue

                # Flow Control Protocol Implementation
                flow_control = {1: "Stop and Wait ARQ", 2: "Selective Repeat"}
                print("\nChoose a Flow Control Protocol:")
                for key, value in flow_control.items():
                    print(f"{key} : {value}")

                select = int(input())
                if select not in flow_control:
                    print("Invalid Entry")
                    continue

                for i in range(no_of_device1):
                    mac = self.generate_mac_address()
                    device_list1.append(EndDevices(i + 1, mac, ""))
                    switch1.topology(device_list1[i])

                    if i == 0:
                        print("\nConnection status : ")
                    switch1.print_connection(i)

                # Select sender and receiver devices
                end_device.prompt("sender", no_of_device1, mapp)
                sender = int(input())
                if not mapp.get(sender, False):
                    print("Invalid Entry")
                    continue

                end_device.prompt("receiver", no_of_device1, mapp)
                receiver = int(input())
                if not mapp.get(receiver, False):
                    print("Invalid Entry")
                    continue

                if sender == receiver:
                    print("Sender and receiver can't be the same")
                    continue

                print("\nInput the message that you would like to send: ")
                data = input()

                sender_device = device_list1[sender - 1]
                sender_device.put_data(data)

                # Token Passing - Access Control Protocol
                sender_device.token_check(device_list1, sender, no_of_device1)
                switch1.update_mac_table()
                print()

                # Flow Control Protocols
                if select == 1:
                    sender_device.stop_and_wait()
                    switch1.transmission(device_list1, sender, receiver)
                    break
                elif select == 2:
                    sender_device.selective_repeat()
                    switch1.transmission(device_list1, sender, receiver)
                    break

            elif choice == 2:
                device_list2 = []
                main_switch = Switch()
                hub_list = []

                for i in range(hub_size):
                    hub = Hub(i + 1)  # Create a new hub with a unique identifier
                    hub_list.append(hub)  # Append it to the hub_list
                    print(f"Hub {i + 1} added to the list.")  # Debugging line

                    main_switch.topology_hub(hub)  # Add the hub to the main switch's topology

                    if i == 0:
                        print("Connection status:\n")
                    main_switch.hub_print_connection(i)  # Print connection status for debugging

                device_num = int(input("\nEnter the number of end devices to be connected with each hub: "))
                if device_num < 2:
                    print("There should be at least two devices. Enter a valid number.")
                    continue

                id = 1
                k = 0
                for hub2 in hub_list:
                    for j in range(device_num):
                        device_list2.append(EndDevices(id, "", ""))
                        hub2.topology(device_list2[k])
                        id += 1
                        k += 1

                # Print connection for each hub
                for i in range(len(hub_list)):
                    print()
                    hub_list[i].connection(i + 1)

                print()

                # Mapping of hubs and devices in Switch
                for i in range(len(hub_list)):
                    connected_devices = hub_list[i].get_devices()
                    main_switch.hub_to_device_map(i, connected_devices)

                main_switch.print_hub_to_device_map()

                total_devices = device_num * hub_size
                end_device.prompt("sender", total_devices, mapp)
                sender = int(input())
                if not mapp.get(sender, False):
                    print("Invalid Entry")
                    continue

                end_device.prompt("receiver", total_devices, mapp)
                receiver = int(input())
                if not mapp.get(receiver, False):
                    print("Invalid Entry")
                    continue

                if sender == receiver:
                    print("Sender and receiver can't be the same")
                    continue

                print("\nInput the message that you would like to send: ")
                data = input()

                source_hub = main_switch.find_hub_for_device(sender)
                sender_device2 = device_list2[sender - 1]
                sender_device2.put_data(data)

                hub_list[source_hub].data = data
                hub_list[source_hub].broadcast(device_list2, sender)
                print()
                hub_list[source_hub].transmission(sender, receiver)

                # Source hub sends data to switch
                destination_hub = main_switch.receive_data(sender, receiver, data)
                receiver_hub = hub_list[destination_hub]

                receiver_hub.broadcast(device_list2, sender)
                print()
                receiver_hub.transmission(sender, receiver)
                print()

                sender_device2.send_ack(receiver)
                receiver_hub.broadcast_ack(sender, receiver, True)
                main_switch.receive_ack(destination_hub)
                main_switch.send_ack_to_hub(source_hub)
                hub_list[source_hub].broadcast_ack(sender, receiver, True)

                break
def main():
    data_layer = DataLayer()
    
    print("Choose an option:")
    print("1: Setup with one switch")
    print("2: Setup with multiple hubs")
    choice = int(input())

    if choice == 1:
        hub_size = 0  # Not required for this choice
    elif choice == 2:
        hub_size = int(input("Enter the number of hubs: "))
    else:
        print("Invalid choice. Exiting...")
        return

    data_layer.run(choice, hub_size)

# if __name__ == "__main__":
#     main()