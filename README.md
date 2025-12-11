# SafeVax - Concurrent Vaccine Distribution System

A GUI-based simulation demonstrating Operating System concepts through vaccine resource allocation across multiple hospitals using Banker's Algorithm for deadlock avoidance.

## Quick Start

### Prerequisites
- Python 3.7 or higher
- Tkinter (usually included with Python)

### Running the Simulation
```bash
python "Vaccine distribution simulation.py"
```

## Features

- **Banker's Algorithm**: Deadlock avoidance through safe state checking
- **Concurrent Hospital Threads**: Multiple processes competing for resources
- **Real-time GUI**: Live visualization of resource allocation
- **Thread-safe Operations**: Mutex locks preventing race conditions

## Project Components

- `Vaccine distribution simulation.py` - Main application with SafeVax implementation
- `PROJECT_REPORT.md` - Complete project report with algorithm descriptions and analysis
- `LICENSE` - MIT License

## OS Concepts Demonstrated

1. **Deadlock Avoidance** - Banker's Algorithm implementation
2. **Concurrency** - Multi-threaded hospital processes
3. **Synchronization** - Mutex locks for thread safety
4. **Resource Management** - Dynamic allocation of vaccines, syringes, and trucks

## System Parameters

Configure in the Python file:
- `TOTAL_RESOURCES`: Available vaccines, syringes, and trucks
- `NUM_HOSPITALS`: Number of concurrent hospital processes (default: 5)

## Documentation

For detailed algorithm descriptions, verification examples, and execution analysis, see [PROJECT_REPORT.md](PROJECT_REPORT.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
