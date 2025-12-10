import threading
import time
import random
import copy
import queue
import tkinter as tk
from tkinter import ttk, scrolledtext


TOTAL_RESOURCES = {'Vaccines': 60, 'Syringes': 60, 'Trucks': 12}
NUM_HOSPITALS = 5
# Simulation runs until window is closed

# Global Queue for communication between threads and GUI
gui_queue = queue.Queue()


# OS KERNEL

class ResourceManager:
    def __init__(self, total_resources):
        self.lock = threading.Lock()
        self.total = total_resources
        self.available = total_resources.copy()
        self.max_demand = {}
        self.allocated = {}
        self.need = {}
        self.push_update("GLOBAL", self.available)

    # Helper to send data to GUI
    def push_update(self, msg_type, data, hospital_name=None):
        gui_queue.put({"type": msg_type, "data": data, "who": hospital_name})

    def register_hospital(self, name, max_demand):
        with self.lock:
            self.max_demand[name] = max_demand
            self.allocated[name] = {r: 0 for r in self.total}
            self.need[name] = max_demand.copy()
            self.push_update("LOG", f"[SYSTEM] Registered {name}")
            self.push_update("HOSPITAL_INIT", {"max": max_demand, "alloc": self.allocated[name]}, name)

    def request_resources(self, name, request):
        with self.lock:
            # Check Physical Availability
            for r in request:
                if request[r] > self.available[r]:
                    self.push_update("LOG", f"⏳ [WAIT] {name} waiting for physical items.")
                    self.push_update("STATUS", "Waiting for Stock", name)
                    return False

            self._provisional_allocate(name, request)
            
            if self._is_safe_state():
                self.push_update("LOG", f"✅ [GRANTED] {name} request approved. Safe State.")
                self.push_update("GLOBAL", self.available)
                self.push_update("HOSPITAL_UPDATE", self.allocated[name], name)
                return True
            else:
                self._provisional_rollback(name, request)
                self.push_update("LOG", f"🛑 [UNSAFE] {name} DENIED by Banker's Algo.")
                self.push_update("STATUS", "Denied (Unsafe State)", name)
                return False

    def release_resources(self, name, release):
        with self.lock:
            for r in release:
                self.allocated[name][r] -= release[r]
                self.available[r] += release[r]
                self.need[name][r] += release[r]
            self.push_update("LOG", f"♻️  [RELEASE] {name} returned resources.")
            self.push_update("GLOBAL", self.available)
            self.push_update("HOSPITAL_UPDATE", self.allocated[name], name)

    def _provisional_allocate(self, name, request):
        for r in request:
            self.available[r] -= request[r]
            self.allocated[name][r] += request[r]
            self.need[name][r] -= request[r]

    def _provisional_rollback(self, name, request):
        for r in request:
            self.available[r] += request[r]
            self.allocated[name][r] -= request[r]
            self.need[name][r] += request[r]

    def _is_safe_state(self):
        # Banker's Algorithm 
        work = self.available.copy()
        finish = {name: False for name in self.allocated}
        while True:
            found_process = False
            for name in self.allocated:
                if not finish[name]:
                    can_finish = True
                    for r in self.total:
                        if self.need[name][r] > work[r]:
                            can_finish = False
                            break
                    if can_finish:
                        for r in self.total:
                            work[r] += self.allocated[name][r]
                        finish[name] = True
                        found_process = True
            if not found_process:
                break
        return all(finish.values())

# CLIENT
class Hospital(threading.Thread):
    def __init__(self, name, manager):
        super().__init__()
        self.name = name
        self.manager = manager
        self.max_demand = {
            'Vaccines': random.randint(15, 25),
            'Syringes': random.randint(15, 25),
            'Trucks': random.randint(2, 5)
        }
        self.running = True
        self.daemon = True # Ensure thread dies when main window closes

    def run(self):
        self.manager.register_hospital(self.name, self.max_demand)
        while self.running:
            time.sleep(random.uniform(1.0, 3.0))
            
            current_need = self.manager.need[self.name]
            total_need = sum(current_need.values())
            
            if total_need == 0:
                gui_queue.put({"type": "STATUS", "data": "Treating Patients (Busy)", "who": self.name})
                time.sleep(3)
                to_release = self.manager.allocated[self.name].copy()
                self.manager.release_resources(self.name, to_release)
                gui_queue.put({"type": "STATUS", "data": "Idle", "who": self.name})
                continue

            request = {}
            for r in self.max_demand:
                needed = current_need[r]
                request[r] = random.randint(1, needed) if needed > 0 else 0

            gui_queue.put({"type": "STATUS", "data": f"Requesting: V:{request['Vaccines']} S:{request['Syringes']} T:{request['Trucks']}", "who": self.name})
            granted = self.manager.request_resources(self.name, request)
            
            if not granted:
                time.sleep(2) # Wait longer if denied


# THE GUI

class SafeVaxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SafeVax: OS Concurrency & Deadlock Simulation")
        self.root.geometry("900x700")
        
        # Styles 
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Danger.TLabel", foreground="red", font=("Helvetica", 10, "bold"))

        #  Top Section: Global Resources
        res_frame = ttk.LabelFrame(root, text="Global Central Warehouse (OS Resources)", padding=10)
        res_frame.pack(fill="x", padx=10, pady=5)
        
        self.res_labels = {}
        for i, res in enumerate(TOTAL_RESOURCES):
            ttk.Label(res_frame, text=f"{res}:", style="Header.TLabel").grid(row=0, column=i*2, sticky="e", padx=5)
            lbl = ttk.Label(res_frame, text=str(TOTAL_RESOURCES[res]), font=("Courier", 14, "bold"), foreground="blue")
            lbl.grid(row=0, column=i*2+1, sticky="w", padx=10)
            self.res_labels[res] = lbl

        # Middle Section: Hospital Grid 
        grid_frame = ttk.LabelFrame(root, text="Hospital Processes Status", padding=10)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Headers
        headers = ["Hospital Name", "Max Need (V/S/T)", "Currently Holding (V/S/T)", "Current Status"]
        for col, text in enumerate(headers):
            ttk.Label(grid_frame, text=text, style="Header.TLabel").grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        self.hospital_rows = {}
        self.grid_frame = grid_frame

        # Bottom Section: Logs 
        log_frame = ttk.LabelFrame(root, text="OS Kernel System Logs", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, state='disabled', font=("Courier", 9))
        self.log_area.pack(fill="both", expand=True)


        self.root.after(100, self.process_queue)

    def add_hospital_row(self, name, row_idx):
        widgets = {}
        widgets['name'] = ttk.Label(self.grid_frame, text=name)
        widgets['name'].grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        
        widgets['max'] = ttk.Label(self.grid_frame, text="...")
        widgets['max'].grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        
        widgets['alloc'] = ttk.Label(self.grid_frame, text="0 / 0 / 0")
        widgets['alloc'].grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        
        widgets['status'] = ttk.Label(self.grid_frame, text="Starting...", width=35)
        widgets['status'].grid(row=row_idx, column=3, padx=5, pady=2, sticky="w")
        
        self.hospital_rows[name] = widgets

    def fmt_dict(self, d):
        return f"{d['Vaccines']} / {d['Syringes']} / {d['Trucks']}"

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END) # Auto-scroll
        self.log_area.config(state='disabled')

    # Processing messages from threads
    def process_queue(self):
        try:
            while True:
                msg = gui_queue.get_nowait()
                m_type = msg['type']
                data = msg['data']
                who = msg['who']

                if m_type == "GLOBAL":
                    for res in data:
                        self.res_labels[res].config(text=str(data[res]))
                
                elif m_type == "HOSPITAL_INIT":
                    self.hospital_rows[who]['max'].config(text=self.fmt_dict(data['max']))
                    self.hospital_rows[who]['alloc'].config(text=self.fmt_dict(data['alloc']))
                    
                elif m_type == "HOSPITAL_UPDATE":
                    self.hospital_rows[who]['alloc'].config(text=self.fmt_dict(data))

                elif m_type == "STATUS":
                    label = self.hospital_rows[who]['status']
                    label.config(text=data)
                    if "Denied" in data:
                         label.config(foreground="red")
                    elif "Treating" in data:
                         label.config(foreground="green")
                    else:
                         label.config(foreground="black")

                elif m_type == "LOG":
                    self.log(data)
                    
        except queue.Empty:
            pass
        finally:
            # Schedule next check in 100ms
            self.root.after(100, self.process_queue)

# MAIN LAUNCHER

if __name__ == "__main__":
    # 1. Setup GUI Root
    root = tk.Tk()
    gui = SafeVaxGUI(root)
    
    # 2. Setup Simulation Objects
    manager = ResourceManager(TOTAL_RESOURCES)
    hospitals = []

    # 3. Initialize Hospital Rows in GUI ahead of time
    for i in range(NUM_HOSPITALS):
        h_name = f"Hospital-{i+1}"
        gui.add_hospital_row(h_name, i+1)
        h = Hospital(h_name, manager)
        hospitals.append(h)

    # 4. Start Simulation Threads
    for h in hospitals:
        h.start()

    # 5. Start GUI Main Loop (Blocking)
    root.mainloop()
    
    # When GUI closes, threads will die because they are daemons.
    print("Simulation terminated.")