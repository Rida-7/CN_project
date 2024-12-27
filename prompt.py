from layers.physicalLayer import physical_layer
from layers.dataLayer import DataLayer
from layers.networkLayer import NetworkLayer

class Prompt:
    def run(self):
        while True:
            hubs = 0
            all_devices = {0: "Hub", 1: "Switch", 2: "Router"}
            print("\n\nChoose a device ")

            for key, value in all_devices.items():
                print(f"{key + 1}: {value}")

            choice = int(input("\nYour choice: "))

            if choice == 1:
                hubs = int(input("\nEnter the number of hubs required: "))

                if hubs == 1:
                    p = physical_layer()
                    p.run()
                else:
                    d = DataLayer()
                    d.run(2, hubs)
            elif choice == 2:
                d = DataLayer()
                d.run(1, hubs)
            elif choice == 3:
                n = NetworkLayer()
                n.run()
            else:
                print("Invalid Entry")

if __name__ == "__main__":
    p = Prompt()
    p.run()
