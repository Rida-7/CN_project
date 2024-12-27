class Hub:
    def __init__(self, hub_id=0):
        self.hub_id = hub_id
        self.connected_devices = []
        self.ack = False
        self.data = None

    def get_id(self):
        return self.hub_id

    def get_devices(self):
        return self.connected_devices

    def topology(self, device):
        self.connected_devices.append(device)

    def connection(self, i):
        for device in self.connected_devices:
            print(f"Connection Established between hub {i} and End device with ID {device.get_id()}")

    def print_connection(self, i):
        print(f"Connection successfully created between hub and device {self.connected_devices[i].get_id()}")

    def broadcast(self, devices, sender):
        sender_device = devices[sender - 1]
        data = sender_device.send_data()
        print(f"Data being sent by device {sender}: {data}")  # Debug print to check data
        print(f"\nMessage \"{data}\" is being broadcasted from the Hub")

        for device in self.connected_devices:
            device.put_data(data)



    def transmission(self, sender, receiver):
        print("\nTransmission status :")

        for device in self.connected_devices:
            message = device.send_data()
            current_device = device.get_id()
            if current_device != sender:
                if current_device != receiver:
                    # discarded by all the devices other than receiver
                    print(f"\"{message}\" was received by device {current_device} but it was discarded")
                else:
                    # accepted by receiver
                    print(f"Device {current_device} received message '{message}' successfully")

    def broadcast_ack(self, sender, receiver, ack):
        print("Hub Broadcasts ACK\n")

        if ack:
            for device in self.connected_devices:
                current_device = device.get_id()
                if current_device != receiver:
                    if current_device != sender:
                        # discarded by all the devices other than sender
                        print(f"ACK was received by device {current_device} but it was discarded")
                    else:
                        # accepted by sender
                        print(f"ACK was received by device {current_device} and it was accepted")
