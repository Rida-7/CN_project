import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
from devices.hub import Hub
from devices.endDevices import EndDevices

class PhysicalLayer:
    @staticmethod
    def generate_mac_address():
        # Generate a random MAC address
        return ":".join(f"{random.randint(0, 255):02X}" for _ in range(6))
    
    @staticmethod
    def send_packet(route):
        # Simulate sending the packet over the network
        print(f"Sending packet to {route[-1]}...")

    @staticmethod
    def run():
        while True:
            try:
                no_of_device = int(input("\nEnter the number of end devices: "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if no_of_device < 2:
                print("\nThere should be at least two devices. Enter a valid number")
                continue

            device_list = []
            device_map = {}
            hub = Hub()

            # Creating end devices and connecting them to the hub
            for i in range(no_of_device):
                device = EndDevices(i + 1, "", "")
                device_list.append(device)
                device_map[device.device_id] = True
                hub.topology(device)  # Connecting device to hub
                if i == 0:
                    print("\nConnection status:\n")
                hub.print_connection(i)  # Print connected devices with hub

            # Create an instance of EndDevices to use prompt
            end_device_instance = EndDevices()

            # Selecting sender
            end_device_instance.prompt("sender", no_of_device, device_map)
            try:
                sender = int(input())
            except ValueError:
                print("Invalid input. Please enter a valid device ID.")
                continue

            if not device_map.get(sender, False):
                print("Invalid Entry")
                continue

            # Selecting receiver
            end_device_instance.prompt("receiver", no_of_device, device_map)
            try:
                receiver = int(input())
            except ValueError:
                print("Invalid input. Please enter a valid device ID.")
                continue

            if not device_map.get(receiver, False):
                print("Invalid Entry")
                continue

            # If sender and receiver are the same
            if sender == receiver:
                print("Sender and receiver can't be the same")
                continue

            # Input the message
            print("\nInput the message:")
            data = input().strip()

            sender_device = device_list[sender - 1]
            sender_device.put_data(data)

            hub.broadcast(device_list, sender)  # Broadcast the message
            hub.transmission(sender, receiver)  # Transmit to the receiver

            sender_device.send_ack(receiver)  # Send acknowledgment
            hub.broadcast_ack(sender, receiver, True)  # Broadcast acknowledgment
            break


# if __name__ == "__main__":
#     PhysicalLayer.run()
