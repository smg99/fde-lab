import subprocess
import sys

def main():
    """Entry point for `make demo`."""
    print("Starting FDE Lab demo...")
    try:
        # We delegate to the typer CLI app
        subprocess.run([sys.executable, "-m", "fde_lab.cli.main", "demo"], check=True)
    except KeyboardInterrupt:
        print("\nExiting.")
    except subprocess.CalledProcessError as e:
        print(f"Error running demo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
