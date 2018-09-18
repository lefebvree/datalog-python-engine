
import sys

from datalog_engine.datalog import Datalog


def main():
    if len(sys.argv) > 1:
        # If an argument is supplied, try to open the associated file
        file_path = sys.argv[1]
    else:
        # Default file to open
        file_path = "tests/metro.dl"

    datalog_engine = Datalog(file_path)
    # Solve queries found in datalog program
    datalog_engine.solve()


if __name__ == '__main__':
    main()
