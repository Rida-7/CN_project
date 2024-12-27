import tkinter as tk
from tkinter import messagebox
import random
from devices.endDevices import EndDevices
from devices.hub import Hub
from devices.switch import Switch

class NetworkSimulatorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Network Simulator")
        self.geometry("600x600")

        self.data_layer = DataLayer()

        # UI Elements
        self.device_count_label = tk.Label(self, text="Enter number of end devices:")
        self.device_count_label.pack(pady=10)
        self.device_count_entry = tk.Entry(self)
        self.device_count_entry.pack(pady=5)

        self.flow_control_label = tk.Label(self, text="Choose Flow Control Protocol:")
        self.flow_control_label.pack(pady=10)
        self.flow_control_var = tk.IntVar()
        self.flow_control_stop_wait = tk.Radiobutton(self, text="Stop and Wait ARQ", variable=self.flow_control_var, value=1)
        self.flow_control_selective_repeat = tk.Radiobutton(self, text="Selective Repeat", variable=self.flow_control_var, value=2)
        self.flow_control_stop_wait.pack()
        self.flow_control_selective_repeat.pack()

        self.sender_label = tk.Label(self, text="Enter Sender Device ID:")
        self.sender_label.pack(pady=10)
        self.sender_entry = tk.Entry(self)
        self.sender_entry.pack(pady=5)

        self.receiver_label = tk.Label(self, text="Enter Receiver Device ID:")
        self.receiver_label.pack(pady=10)
        self.receiver_entry = tk.Entry(self)
        self.receiver_entry.pack(pady=5)

        self.message_label = tk.Label(self, text="Enter the message:")
        self.message_label.pack(pady=10)
        self.message_entry = tk.Entry(self)
        self.message_entry.pack(pady=5)

        self.send_button = tk.Button(self, text="Send Message", command=self.run_simulation)
        self.send_button.pack(pady=20)

    def run_simulation(self):
        try:
            no_of_device1 = int(self.device_count_entry.get())
            sender = int(self.sender_entry.get())
            receiver = int(self.receiver_entry.get())
            data = self.message_entry.get().strip()

            flow_control = {1: "Stop and Wait ARQ", 2: "Selective Repeat"}
            select = self.flow_control_var.get()

            if no_of_device1 < 2:
                messagebox.showerror("Input Error", "There should be at least two devices.")
                return

            if select not in flow_control:
                messagebox.showerror("Input Error", "Invalid Flow Control Protocol selected.")
                return

            device_list1 = []
            mapp = {}
            switch1 = Switch()
            end_device = EndDevices()

            # Creating devices and configuring switch topology
            for i in range(no_of_device1):
                mac = self.data_layer.generate_mac_address()
                device_list1.append(EndDevices(i + 1, mac, ""))
                switch1.topology(device_list1[i])

            # Checking sender and receiver validity
            if sender == receiver:
                messagebox.showerror("Input Error", "Sender and receiver can't be the same.")
                return

            if sender < 1 or sender > no_of_device1 or receiver < 1 or receiver > no_of_device1:
                messagebox.showerror("Input Error", "Invalid sender or receiver device ID.")
                return

            sender_device = device_list1[sender - 1]
            sender_device.put_data(data)

            # Flow Control Protocol Implementation
            if select == 1:
                sender_device.stop_and_wait()
                switch1.transmission(device_list1, sender, receiver)
            elif select == 2:
                sender_device.selective_repeat()
                switch1.transmission(device_list1, sender, receiver)

            messagebox.showinfo("Simulation Completed", "Message Sent Successfully!")

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers.")

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
        pass  # The run method is removed in this implementation because the logic is now handled by the GUI

def main():
    app = NetworkSimulatorGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
