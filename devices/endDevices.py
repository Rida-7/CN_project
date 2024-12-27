import random
import subprocess
import time
from processing.process import Process

class EndDevices:
    def __init__(self, device_id=0, mac_address="", ip_address=""):
        self.device_id = device_id
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.message = ""
        self.arp = {}
        self.selective_window = {}
        self.sender_buffer = 0
        self.receiver_buffer = 0
        self.ack = False
        self.token = False

    def get_id(self):
        return self.device_id

    def get_mac(self):
        return self.mac_address

    def get_ip(self):
        return self.ip_address

    def put_data(self, data):
        self.message = data

    def send_data(self):
        return self.message

    # Application layer protocol (Callback function to write received data into a string)
    @staticmethod
    def write_callback(contents, size, nmemb, output):
        total_size = size * nmemb
        output.append(contents[:total_size])
        return total_size

    def http(self):
        domain = input("Enter domain name: ")
        command = f"curl -s https://{domain}"

        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            response, _ = process.communicate()
            print(f"Response:\n{response.decode()}")
            return 0
        except Exception as e:
            print("Error executing command.")
            return 1

    def dns(self):
        domain = input("DNS \nEnter domain name: ")
        command = f"nslookup {domain}"

        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = process.communicate()
            print(output.decode())
        except Exception as e:
            print("Failed to execute the command.")

    def send_ack(self, receiver):
        print(f"\nAcknowledgement Status: \nDevice {receiver} sends back ACK to Hub\n")

    # Access Control Protocol
    def token_check(self, devices, sender, size):
        rand = random.Random()
        print("\nToken status:")
        i = rand.randint(0, size - 1)
        
        # Until sender doesn't have access to token
        while not devices[sender - 1].token:
            current_device = i % size
            devices[current_device].token = True
            if current_device != (sender - 1):
                print(f"Currently sender doesn't have access to channel. Token is at device {current_device + 1}. Waiting to get access.")
            i += 1
            time.sleep(1)
        
        print("Sender has access to channel now.")

    def sender(self, window):
        rand = random.Random()
        print()
        i = 0
        while i < len(window):
            self.ack = False
            timeout_duration = 4
            sending_time = rand.randint(0, 5)
            receiving_time = rand.randint(0, 5)
            self.sender_buffer = window[i]

            # Sending packet to receiver
            try:
                time.sleep(sending_time)
            except InterruptedError:
                pass

            # Packet got lost, then resend it
            if sending_time > timeout_duration:
                print(f"Sender sends packet with sequence number {window[i]} but it got lost")
                continue
            # Packet didn't get lost
            else:
                print(f"Sender sends packet with sequence number {self.sender_buffer}")
                ack_no = self.receiver(window, i)
                # Receiver reaches at the end of window
                if ack_no == -1:
                    print("Done")
                    break
                if receiving_time > timeout_duration:
                    print(f"ACK {ack_no} got lost")
                    continue  # Resend packet
                else:
                    if self.ack:
                        print(f"Sender receives ACK {ack_no}")  # ACK received
                        i += 1

    def receiver(self, window, i):
        j = 0
        if self.sender_buffer == window[j] and i == j and j < len(window):
            self.receiver_buffer = self.sender_buffer
            self.ack = True
            j += 1
            if j == len(window):
                return -1
            return window[j]
        else:
            print(f"Packet {window[i]} was discarded as it is a duplicate")
            self.ack = True
            return window[j]

    def stop_and_wait(self):
        window_size = 7
        window = [i % 2 for i in range(window_size)]
        print("\nTransmission Status:")
        self.sender(window)

    def selective_receiver(self, packet):
        self.selective_window[packet] = True
        ack_no = packet

        count = 0
        for j in range(len(self.selective_window)):
            if not self.selective_window.get(j, False):
                break
            count += 1
        rn = count
        self.ack = True
        return ack_no

    def selective_sender(self):
        rand = random.Random()
        sn = 0
        sf = 1
        s_z = len(self.selective_window)
        i = 0

        while i < s_z:
            self.ack = False
            timeout_duration = 4
            sending_time = rand.randint(0, 5)
            receiving_time = rand.randint(0, 5)

            try:
                time.sleep(sending_time)
            except InterruptedError:
                pass

            if sending_time > timeout_duration:
                print(f"Sender sends packet with sequence number {i} but it got lost")
                i += 1
                continue
            else:
                packet = i
                print(f"Sender sends packet with sequence number {packet}")
                ack_no = self.selective_receiver(packet)

                if receiving_time > timeout_duration:
                    print(f"ACK {ack_no} got lost")
                    i += 1
                else:
                    if self.ack:
                        print(f"ACK {ack_no} received")
                        count = 0
                        for j in range(ack_no + 1):
                            if not self.selective_window.get(j, False):
                                break
                            count += 1
                        sf = count

                        i += 1
                        sn = i

        if i == s_z:
            print("\nTime out occurred")
            for j in range(len(self.selective_window)):
                if not self.selective_window.get(j, False):
                    print(f"Resending Packet {j} as it wasn't received")
                    ack_no = self.selective_receiver(j)
                    print(f"ACK {ack_no} received")

    def selective_repeat(self):
        print()
        size = 8
        for i in range(size):
            self.selective_window[i] = False
        self.selective_sender()

    # For selecting Sender and Receiver device
    def prompt(self, device_type, d, mp):
        for i in range(1, d + 1):
            mp[i] = True
        print(f"\nChoose the {device_type} device - ")
        for i in range(len(mp)):
            print(f"{i + 1} : device {i + 1}")

    def arp_cache(self, ip, mac):
        self.arp[ip] = mac

    def print_arp_cache(self):
        print("\nARP Cache of sender is as :\n")
        print("IP\t\t\tMAC\n")
        for ip, mac in self.arp.items():
            print(f"{ip}\t\t{mac}\n")
