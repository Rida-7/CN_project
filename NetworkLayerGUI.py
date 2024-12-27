import tkinter as tk
from tkinter import messagebox
from threading import Thread
from layers.networkLayer import NetworkLayer

class NetworkSimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Simulation")
        self.network_layer = NetworkLayer([])  # Pass routers if needed

        # Sender and Receiver Selection
        tk.Label(root, text="Sender (1-4):").grid(row=0, column=0, padx=5, pady=5)
        self.sender_entry = tk.Entry(root)
        self.sender_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Receiver (1-4):").grid(row=1, column=0, padx=5, pady=5)
        self.receiver_entry = tk.Entry(root)
        self.receiver_entry.grid(row=1, column=1, padx=5, pady=5)

        # Message Input
        tk.Label(root, text="Message:").grid(row=2, column=0, padx=5, pady=5)
        self.message_entry = tk.Entry(root)
        self.message_entry.grid(row=2, column=1, padx=5, pady=5)

        # Routing Scheme Selection
        tk.Label(root, text="Routing Scheme:").grid(row=3, column=0, padx=5, pady=5)
        self.scheme_var = tk.IntVar()
        tk.Radiobutton(root, text="Static Routing", variable=self.scheme_var, value=1).grid(row=3, column=1, padx=5, pady=5, sticky="w")
        tk.Radiobutton(root, text="Dynamic Routing", variable=self.scheme_var, value=2).grid(row=3, column=2, padx=5, pady=5, sticky="w")

        # Start Simulation Button
        self.start_button = tk.Button(root, text="Start Simulation", command=self.start_simulation)
        self.start_button.grid(row=4, column=1, pady=10)

        # Output Log
        tk.Label(root, text="Simulation Log:").grid(row=5, column=0, columnspan=3, padx=5, pady=5)
        self.log_text = tk.Text(root, height=15, width=50)
        self.log_text.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def start_simulation(self):
        sender = self.sender_entry.get()
        receiver = self.receiver_entry.get()
        message = self.message_entry.get()
        scheme = self.scheme_var.get()

        if not sender or not receiver or not message or not scheme:
            messagebox.showerror("Input Error", "Please fill all fields!")
            return

        try:
            sender = int(sender)
            receiver = int(receiver)

            if sender == receiver:
                messagebox.showerror("Input Error", "Sender and Receiver can't be the same!")
                return

            # Run simulation in a separate thread
            Thread(target=self.simulate_network, args=(sender, receiver, message, scheme)).start()

        except ValueError:
            messagebox.showerror("Input Error", "Sender and Receiver must be integers!")

    def simulate_network(self, sender, receiver, message, scheme):
        self.log(f"Starting simulation: Sender={sender}, Receiver={receiver}, Scheme={scheme}")
        self.network_layer.message = message
        self.network_layer.scheme = scheme

        # Call the `NetworkLayer` logic
        self.network_layer.run()

        self.log("Simulation finished.")


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkSimulationApp(root)
    root.mainloop()
