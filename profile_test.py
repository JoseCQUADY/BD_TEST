import os
import psutil
from main import run_automation

def monitor_peak_memory():
    process = psutil.Process(os.getpid())
    print("Executing performance analysis on network ETL pipeline...")
    
    run_automation()
    
    peak_bytes = process.memory_info().peak_wset if os.name == 'nt' else process.memory_info().rss
    peak_mb = peak_bytes / (1024 * 1024)
    
    print("\n" + "="*50)
    print(f"AUDIT REPORT: AUDITORÍA DE INFRAESTRUCTURA")
    print(f"Maximum Peak Memory Registered: {peak_mb:.2f} MB")
    print("="*50)
    
    if peak_mb <= 4.0:
        print("STATUS: SUCCESS - Script operates safely below the 4MB threshold.")
    else:
        print("STATUS: FAILURE - Memory allocation exceeds production limits.")

if __name__ == "__main__":
    monitor_peak_memory()