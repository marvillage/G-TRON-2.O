import subprocess
import time
import os

# List of (port, script_path) tuples
streamlit_apps = [
    (8501, "esp.py"),
    (8502, "epr.py"),
    (8503, "lifecycle.py"),
    (8504, "classification.py"),
    (8505, "toxmat.py"),
    (8506, "iotsensor.py"),
    (8507, "route.py"),
    (8508, "illegal.py"),
    (8512, "compilance.py"),
    (8513, "wa.py"),
    (8514, "ma.py"),
    (8516, "buyrecycle.py"),
]
background_scripts = [
    "scripts/carbon.py",
    "scripts/live.py"
]
# Optional: kill any process on these ports (Unix-based)
def kill_existing_servers(ports):
    for port in ports:
        subprocess.run(f"lsof -ti:{port} | xargs kill -9", shell=True)

# Kill existing servers on these ports
kill_existing_servers([port for port, _ in streamlit_apps])

# Start each Streamlit app
for port, script in streamlit_apps:
    print(f"Starting {script} on port {port}...")
    subprocess.Popen(
        ["streamlit", "run", script, "--server.port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)  # small delay to avoid overload

for script in background_scripts:
    print(f"⚙️ Running background script: {script}...")
    subprocess.Popen(
        ["python", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

print("\n✅ All apps and scripts launched successfully!\n")
