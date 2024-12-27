import random

class Process:
    def __init__(self):
        self.process_id = None
        self.port_number = None

    def assign_port_number(self, process_map):
        port = random.randint(1024, 65535)  # Generate a random port number between 1024 and 65535

        # If the generated port is already in process_map, or less than 1024, keep generating
        while port in process_map or port < 1024:
            port = random.randint(1024, 65535)
        
        return port
