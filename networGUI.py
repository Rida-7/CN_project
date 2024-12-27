import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
from devices.hub import Hub
from devices.router import Router
from devices.endDevices import EndDevices
from devices.switch import Switch
from layers.dataLayer import DataLayer
from layers.physicalLayer import PhysicalLayer
from layers.networkLayer import NetworkLayer

class NetworkSimulatorGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Network Simulator")
        self.geometry("1200x900")

        self.device_locations = []
        self.message_history = {}
        self.physical_layer = PhysicalLayer()
        self.data_layer = DataLayer()
        # self.network_layer = NetworkLayer()

        # Use grid layout for overall window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=250)  # control panel
        self.grid_columnconfigure(1, weight=1)  # output and topology area

        self.control_panel = tk.Frame(self, bg="lightgray")
        self.control_panel.grid(row=0, column=0, sticky="nswe")

        # Main Device Panel
        self.add_main_device_panel = tk.LabelFrame(self.control_panel, text="Main Device Panel")
        self.add_main_device_panel.grid(padx=10, pady=10, sticky="ew")

        self.main_device_type_var = tk.StringVar()
        self.main_device_type_combo = tk.OptionMenu(self.add_main_device_panel, self.main_device_type_var, "Hub", "Switch", "Router")
        self.no_of_main_devices_field = tk.Entry(self.add_main_device_panel, width=5)

        self.add_main_device_button = tk.Button(self.add_main_device_panel, text="Add Main Device", command=self.add_main_device)
        tk.Label(self.add_main_device_panel, text="Main Device Type:").grid(row=0, column=0)
        self.main_device_type_combo.grid(row=0, column=1)
        tk.Label(self.add_main_device_panel, text="Number of Main Devices:").grid(row=1, column=0)
        self.no_of_main_devices_field.grid(row=1, column=1)
        self.add_main_device_button.grid(row=2, columnspan=2)

        # End Device Panel
        self.add_end_devices_panel = tk.LabelFrame(self.control_panel, text="Add End Devices")
        self.add_end_devices_panel.grid(padx=10, pady=10, sticky="ew")

        self.no_of_end_devices_field = tk.Entry(self.add_end_devices_panel, width=5)
        self.add_end_devices_button = tk.Button(self.add_end_devices_panel, text="Add End Devices", command=self.add_end_devices)

        tk.Label(self.add_end_devices_panel, text="Number of End Devices:").grid(row=0, column=0)
        self.no_of_end_devices_field.grid(row=0, column=1)
        self.add_end_devices_button.grid(row=1, columnspan=2)

        # Message Panel
        self.message_panel = tk.LabelFrame(self.control_panel, text="Message Panel")
        self.message_panel.grid(padx=10, pady=10, sticky="ew")

        self.sender_field = tk.Entry(self.message_panel)
        self.receiver_field = tk.Entry(self.message_panel)
        self.message_field = tk.Entry(self.message_panel)

        self.send_message_button = tk.Button(self.message_panel, text="Send Message", command=self.send_message)

        tk.Label(self.message_panel, text="Sender ID:").grid(row=0, column=0)
        self.sender_field.grid(row=0, column=1)
        tk.Label(self.message_panel, text="Receiver ID:").grid(row=1, column=0)
        self.receiver_field.grid(row=1, column =1)
        tk.Label(self.message_panel, text="Message:").grid(row=2, column=0)
        self.message_field.grid(row=2, column=1)
        self.send_message_button.grid(row=3, columnspan=2)

        # Remove Topology Button
        self.remove_topology_button = tk.Button(self.control_panel, text="Remove Topology", command=self.remove_topology)
        self.remove_topology_button.grid(padx=10, pady=10, sticky="ew")

        # Output Area
        self.output_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=20)
        self.output_area.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        # Topology Panel
        self.topology_panel = TopologyPanel(self)
        self.topology_panel.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        self.devices = []
        self.device_map = {}
        self.hubs = {}
        self.switches = {}
        self.routers = {}
        

    def add_main_device(self):
        device_type = self.main_device_type_var.get()
        num_devices = int(self.no_of_main_devices_field.get())

        if not device_type or num_devices <= 0:
            self.output_area.insert(tk.END, "Invalid input.\n")
            return

        for i in range(num_devices):
            id = len(self.device_locations) + 1
            point = (len(self.device_locations) * 50 + 20, 50)
            self.device_locations.append(point)

            if device_type == "Hub":
                hub = Hub(id)
                self.hubs[id] = hub
                self.topology_panel.add_device(point, f"Hub {id}", "red", "H")
            elif device_type == "Switch":
                switch_device = Switch(id)
                self.switches[id] = switch_device
                self.topology_panel.add_device(point, f"Switch {id}", "green", "S")
            elif device_type == "Router":
                router = Router(id)
                self.routers[id] = router
                self.topology_panel.add_device(point, f"Router {id}", "blue", "R")

        self.output_area.insert(tk.END, f"Added {num_devices} {device_type}(s)\n")

        # Use grid instead of pack for add_end_devices_panel
        self.add_end_devices_panel.grid(padx=10, pady=10, sticky="ew")


    def add_end_devices(self):
        num_end_devices = int(self.no_of_end_devices_field.get())

        if num_end_devices <= 0:
            self.output_area.insert(tk.END, "Invalid input.\n")
            return

        for i in range(num_end_devices):
            id = len(self.devices) + 1
            end_device = EndDevices(id, self.generate_mac_address(), f"IP{id}")
            self.devices.append(end_device)
            self.device_map[id] = end_device

            point = (len(self.device_locations) * 50 + 20, 100 if len(self.device_locations) % 2 == 0 else 150)
            self.device_locations.append(point)
            self.topology_panel.add_device(point, f"End {id}", "orange", "E")

            for hub in self.hubs.values():
                hub.topology(end_device)
                self.topology_panel.add_link(point, self.device_locations[hub.hub_id - 1])

            for switch_device in self.switches.values():
                switch_device.topology(end_device)
                self.topology_panel.add_link(point, self.device_locations[switch_device.switch_id - 1])

            for router in self.routers.values():
                router.topology(end_device)
                self.topology_panel.add_link(point, self.device_locations[router.id - 1])

        self.output_area.insert(tk.END, f"Added {num_end_devices} End Device(s)\n")

    def remove_topology(self):
        self.devices.clear()
        self.device_map.clear()
        self.hubs.clear()
        self.switches.clear()
        self.routers.clear()
        self.device_locations.clear()
        self.topology_panel.clear_devices()
        self.output_area.insert(tk.END, "Topology removed.\n")

    def send_message(self):
        sender = int(self.sender_field.get())
        receiver = int(self.receiver_field.get())
        message = self.message_field.get()

        if not message:
            self.output_area.insert(tk.END, "Message cannot be empty.\n")
            return

        if sender in self.device_map and receiver in self.device_map:
            sender_device = self.device_map[sender]
            receiver_device = self.device_map[receiver]

            if self.hubs:
                hub = next(iter(self.hubs.values()))
                hub.broadcast(self.devices, sender)
                hub.transmission(sender, receiver)
                sender_device.send_ack(receiver)
                hub.broadcast_ack(sender, receiver, True)

            self.output_area.insert(tk.END, f"Message from {sender} to {receiver}: {message}\n")
            self.message_history[sender] = message
        else:
            self.output_area.insert(tk.END, "Invalid Sender or Receiver ID\n")

    def generate_mac_address(self):
        return ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])

class TopologyPanel(tk.Canvas):
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.devices = []
        self.device_labels = []
        self.device_colors = []
        self.device_shapes = []
        self.links = []

        self.bind("<Button-1>", self.on_click)

    def add_device(self, point, label, color, shape):
        self.devices.append(point)
        self.device_labels.append(label)
        self.device_colors.append(color)
        self.device_shapes.append(shape)
        self.draw()

    def clear_devices(self):
        self.devices.clear()
        self.device_labels.clear()
        self.device_colors.clear()
        self.device_shapes.clear()
        self.links.clear()
        self.delete("all")

    def add_link(self, from_point, to_point):
        self.links.append((from_point, to_point))
        self.draw()

    def draw(self):
        self.delete("all")
        for link in self.links:
            self.create_line(link[0][0] + 15, link[0][1] + 15, link[1][0] +  15, link[1][1] + 15, fill="black")

        for i, point in enumerate(self.devices):
            color = self.device_colors[i]
            shape = self.device_shapes[i]
            label = self.device_labels[i]

            if shape == "H":
                self.create_rectangle(point[0], point[1], point[0] + 30, point[1] + 30, fill=color)
            elif shape == "S":
                self.create_oval(point[0], point[1], point[0] + 30, point[1] + 30, fill=color)
            elif shape == "R":
                self.create_oval(point[0], point[1], point[0] + 30, point[1] + 30, fill=color)
            elif shape == "E":
                self.create_oval(point[0], point[1], point[0] + 20, point[1] + 20, fill=color)

            self.create_text(point[0] + 15, point[1] - 5, text=label)

    def on_click(self, event):
        click_point = (event.x, event.y)
        for i, device_point in enumerate(self.devices):
            if (device_point[0] <= click_point[0] <= device_point[0] + 30 and
                device_point[1] <= click_point[1] <= device_point[1] + 30):
                self.show_device_details(i + 1)

    def show_device_details(self, device_id):
        device = self.master.device_map.get(device_id)
        if device:
            messagebox.showinfo("Device Details", f"Device ID: {device_id}\nMAC Address: {device.get_mac()}\nIP Address: {device.get_ip()}")
        elif device_id in self.master.hubs:
            messagebox.showinfo("Device Details", f"Hub ID: {device_id}")
        elif device_id in self.master.switches:
            messagebox.showinfo("Device Details", f"Switch ID: {device_id}")
        elif device_id in self.master.routers:
            messagebox.showinfo("Device Details", f"Router ID: {device_id}")
        else:
            messagebox.showerror("Error", "Device not found.")

if __name__ == "__main__":
    app = NetworkSimulatorGUI()
    app.mainloop()