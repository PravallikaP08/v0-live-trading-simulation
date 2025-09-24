import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    # Essential packages first
    essential_packages = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "sqlalchemy==2.0.23",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "python-multipart==0.0.6",
        "websockets==12.0"
    ]
    
    # Data packages (might need compilation)
    data_packages = [
        "numpy==1.24.3",
        "pandas==2.1.4", 
        "yfinance==0.2.28"
    ]
    
    print("Installing essential packages...")
    for package in essential_packages:
        install_package(package)
    
    print("\nInstalling data packages...")
    for package in data_packages:
        if not install_package(package):
            print(f"Trying alternative installation for {package.split('==')[0]}...")
            # Try without version constraint
            package_name = package.split('==')[0]
            install_package(package_name)

if __name__ == "__main__":
    main()
