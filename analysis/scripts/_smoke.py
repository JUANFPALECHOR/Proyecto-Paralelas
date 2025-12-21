from analysis.engine.factory import get_engine
import sys

def main():
    e = get_engine("pandas")
    print("python", sys.version)
    print("engine", type(e).__name__)

if __name__ == "__main__":
    main()
