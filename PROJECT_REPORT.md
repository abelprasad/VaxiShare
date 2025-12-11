Project Report: SafeVax – Concurrent Vaccine Distribution System
1. Description of the Project
Objective: The primary objective of the SafeVax project is to design and develop a simulation of a distributed healthcare system that manages the concurrent allocation of limited medical resources (vaccines, syringes, and transport trucks) across multiple hospitals.

The system mimics an Operating System kernel managing processes. It treats hospitals as independent "processes" competing for shared system resources. The goal is to ensure data integrity (preventing race conditions during inventory updates) and operational continuity (preventing deadlocks where hospitals hoard resources and none can proceed). The project utilizes multi-threading to simulate real-time concurrent requests and implements a Graphical User Interface (GUI) to visualize the internal decision-making of the OS scheduling algorithms.

2. Significance of the Project
Meaningfulness: In real-world healthcare emergencies, such as the COVID-19 pandemic, the supply chain is often fragmented. Multiple regional hospitals aggressively compete for a finite global stock of vital supplies. If this competition is not managed by a central authority, it leads to two catastrophic failures:

Race Conditions: Inventory databases becoming corrupted when two requests modify stock simultaneously (e.g., "double-booking" vaccines).

Deadlocks: Hospitals holding partial resources (e.g., holding vaccines but waiting for syringes) while others hold the complementary resources, causing the entire distribution network to freeze.

Novelty: While standard OS projects often focus on abstract concepts like CPU scheduling, SafeVax applies these low-level primitives to a high-stakes, domain-specific problem: Healthcare Logistics. By mapping "processes" to "hospitals" and "mutex locks" to "inventory controls," this project demonstrates how Operating System principles are foundational to solving societal challenges in equitable resource delivery.

3. Code Structure
The project is implemented in Python using the threading library for concurrency and tkinter for the GUI. The architecture follows a Client-Server model simulated within a single application.

System Components Diagram
Code snippet

graph TD
    GUI[SafeVaxGUI (Main Thread)] <-->|Queue| OS[ResourceManager (Kernel)]
    OS <-->|Mutex Lock| Database[(Shared Resources)]
    H1[Hospital Thread 1] -->|Request| OS
    H2[Hospital Thread 2] -->|Request| OS
    H3[Hospital Thread 3] -->|Request| OS
Class Descriptions:
ResourceManager (The OS Kernel):

Acting as the central authority, this class manages the global inventory of Vaccines, Syringes, and Trucks.

It maintains the state of the system, tracking Available resources, Allocated resources, and the Max Demand of every hospital.

Key Responsibility: It enforces the Banker’s Algorithm. Every request must pass through request_resources(), which checks if granting the request would lead to an unsafe state.

Hospital (The Process):

Inherits from threading.Thread. Each instance represents an independent hospital running in parallel.

It generates random resource requests (up to a pre-defined maximum need) and submits them to the ResourceManager.

It simulates "work" (treating patients) by sleeping, then releases resources back to the pool.

SafeVaxGUI (The Visualization):

Runs on the main thread. It does not access data directly to avoid freezing.

Instead, it polls a thread-safe gui_queue. Worker threads push updates (logs, status changes, inventory counts) to this queue, which the GUI reads to update the dashboard in real-time.

4. Description of Algorithms
Two primary Operating System algorithms are implemented to solve the concurrency challenges:

A. Mutual Exclusion (Mutex Locks)
To prevent Race Conditions, the ResourceManager uses a threading.Lock object.

Mechanism: Whenever a hospital attempts to read or write to the shared inventory (inside request_resources or release_resources), it must first acquire the lock.

Result: This ensures that even if five hospitals request vaccines at the exact same nanosecond, the system processes them strictly one by one, ensuring the inventory count never becomes corrupted or negative.

B. The Banker’s Algorithm (Deadlock Avoidance)
To prevent Deadlocks, the system employs Dijkstra's Banker's Algorithm.

Mechanism: When a request arrives, the system does not immediately grant it, even if resources are physically available. Instead, it runs a simulation:

Provisional Allocation: It pretends to give the resources to the hospital.

Safety Check (_is_safe_state): It checks if there exists at least one sequence of execution where all hospitals can eventually finish their tasks.

Decision:

If the future state is SAFE, the allocation is finalized.

If the future state is UNSAFE (potential deadlock), the allocation is rolled back, and the hospital is denied and told to wait.

5. Verification of Algorithms
We can verify the Banker's Algorithm with the following "toy example" trace derived from the system logic:

Initial State:

Available: [Vaccines: 10]

Hospital A Needs: 8 (Has 2) -> Needs 6 more.

Hospital B Needs: 4 (Has 0) -> Needs 4 more.

Scenario 1: Unsafe Request

Hospital A requests 2 vaccines.

Simulation: If we give 2 to A, Available becomes 8.

A needs 4 more. (8 available > 4 needed). A can finish.

B needs 4 more. (8 available > 4 needed). B can finish.

Result: SAFE. Request Granted.

Scenario 2: Unsafe Request (The "Greedy" Block)

New State: Available: 4. A needs 4. B needs 4.

Hospital B requests 2 vaccines.

Simulation: If we give 2 to B, Available becomes 2.

A needs 4. (We have 2). A cannot finish.

B has 2, needs 2 more. (We have 2). B might finish, but if A requests first, we are stuck.

Strict Safety Check: If the system cannot guarantee a sequence where everyone finishes, it declares the state UNSAFE.

Result: UNSAFE. Request Denied. Hospital B must wait, preserving the 4 vaccines for Hospital A to finish first, return its resources, and then B can proceed.

6. Functionalities
The SafeVax system includes the following key functionalities:

Real-Time Dashboard: A visual grid showing the status of 5 concurrent hospitals, including their specific resource holdings and current actions (Waiting, Requesting, Treating).

Live Resource Tracking: A global counter displaying the "Warehouse" inventory of Vaccines, Syringes, and Trucks, updating dynamically as threads claim and release items.

Deadlock Avoidance Logging: A scrolling log window that explicitly reports when the Banker's Algorithm intervenes. Messages like 🛑 [UNSAFE] ... DENIED highlight the algorithm protecting the system.

Starvation Simulation: Hospitals automatically retry requests after a denial, simulating the "wait and backoff" strategy used in network protocols.

Thread-Safe Communication: Utilization of a queue.Queue to bridge the gap between background simulation threads and the main GUI thread without freezing the interface.

7. Execution Results and Analysis
Upon executing the simulation, the effectiveness of the algorithms is immediately visible through the GUI logs.

Main Results:

Successful Concurrency: All 5 hospital threads operate simultaneously without crashing the application. The total resources never drift from their initial constants (60 Vaccines, 60 Syringes, 12 Trucks), proving the Mutex locks successfully prevented race conditions.

Deadlock Prevention: The system frequently enters states where physical resources are available (e.g., 2 Trucks left), but a request is denied.

Observation: The log prints 🛑 [UNSAFE] Hospital-3 DENIED.

Analysis: This confirms that Hospital-3's request, while physically possible, would have depleted the buffer needed for a higher-demand hospital to complete its work. By denying this, the system forced a safe ordering.

Throughput: Despite the delays introduced by the safety checks (Banker's Algorithm), all hospitals eventually cycle through Treating Patients and ♻️ [RELEASE]. This demonstrates that the system is liveness-preserving—it delays tasks to prevent crashes but ensures everyone eventually completes their job.

8. Conclusions
Summary of Findings: The project successfully demonstrates that Operating System primitives are essential for robust application design. By treating healthcare logistics as a resource allocation problem, we proved that the Banker's Algorithm effectively eliminates deadlocks in a supply chain, ensuring that critical resources are never hoarded inefficiently.

Issues & Limitations:

Starvation: While deadlocks are prevented, the current implementation does not strictly prevent "starvation" (where a small hospital waits indefinitely if larger hospitals constantly consume resources). A future improvement would be implementing a "Fairness" or "Aging" algorithm.

Simulation Constraints: The "work" is simulated by time.sleep(). In a real deployment, this would be replaced by database transactions.

Application of Course Learning: This project served as a practical capstone for the OS course, allowing for the direct application of:

Concurrency: Managing multi-threaded access to shared memory.

Synchronization: Using Mutexes to protect critical sections.

Process Management: Understanding process states (Blocked, Running, Ready) through the lens of hospital workflows.
