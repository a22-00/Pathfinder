import subprocess
import sys

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")

# Install remaining packages
packages = [
    "anthropic==0.7.4",
    "pytrends==4.9.2", 
    "pandas==2.0.3"
]

print("Installing remaining packages...")
for package in packages:
    install_package(package)

print("Done!") 