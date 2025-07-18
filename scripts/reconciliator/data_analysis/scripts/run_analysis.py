
from .check_settings import checkSettings
from .run_all import main as run_all

def main():
    if checkSettings():
        run_all()

if __name__ == "__main__":
    main()