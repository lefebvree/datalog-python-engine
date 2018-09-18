
from .context import ProgramContext
from .file_parser import FileParser


class Datalog:
    """ Represents a program instance, initialised by a file, the program context is populated from a FileParser

    """
    def __init__(self, file_path=None):
        self._programContext = ProgramContext()

        if file_path is not None:
            file_parser = FileParser(self._programContext)
            file_parser.parse_file(file_path)

            self._programContext.check_program_validity()

        print(self._programContext)

    def solve(self):
        """ For each query() rules found in the program, try to find a list of solution (variables bindings and print it)

        """
        self._programContext.solve_queries()
