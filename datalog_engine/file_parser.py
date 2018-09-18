
import re

from .clause import *


class FileParser:

    # Regular expressions for every recognised Datalog statement

    REGEX_CLAUSE = re.compile('^([a-z]+)\(([$a-zA-Z0-9][a-zA-Z0-9]*(?:,[$a-zA-Z0-9][a-zA-Z0-9]*)*)\)$')

    REGEX_EDB = re.compile('^([a-z]+)\(([a-zA-Z0-9]+(?:,[a-zA-Z0-9]+)*)\)\.$')
    REGEX_IDB = re.compile('^([a-z]+)\(([$a-zA-Z0-9][a-zA-Z0-9]*(?:,[$a-zA-Z0-9][a-zA-Z0-9]*)*)\)\.$')
    REGEX_MAPPING = re.compile('^((?:[a-z][a-zA-Z]*\((?:[$a-zA-Z0-9][a-zA-Z0-9]*,?)+\),?)+)->([a-z][a-zA-Z0-9]*\((?:[$a-zA-Z0-9][a-zA-Z0-9]*,?)+\))\.$')

    def __init__(self, context):
        """ Open and read file to populate a context with facts, rules and queries

        :param context: ProgramContext
        """
        self._program_context = context

    def parse_file(self, file_path):
        """ Read a dl file and populate a program context

        :param file_path: string of file path
        """
        with open(file_path) as file:
            for line in file:
                self.parse_line(line)

    def parse_line(self, line):
        """ Try to compute a string to a dl predicate

        :param line: string, line with a valid dl syntax or ignored
        :return: boolean indicating if line could be computed
        """
        line = line.replace(" ", "")

        # FACT : link(Charpennes, PartDieu).
        fact = self.REGEX_EDB.match(line)
        if fact:
            self._program_context.add_fact(self.get_fact_from_regex_match(fact))
            return True

        # IDB : link($X, $Y)
        predicate = self.REGEX_IDB.match(line)
        if predicate:
            self._program_context.add_predicate(self.get_predicate_from_regex_match(predicate))
            return True

        # RULE : link($X, Charpennes), link($Y, $Z) -> link($X, $Z)
        rule = self.REGEX_MAPPING.match(line)
        if rule:
            self._program_context.add_rule(self.get_rule_from_regex_match(rule))
            return True

        return False

    @staticmethod
    def get_parameter_from_string(string):
        """ Check if a parameter is a variable or a constant and construct associated object

        :param string: value of a constant or variable name preceded by '$'
        """
        if string[0] == '$':
            return Variable(string[1:])
        else:
            return Constant(string)

    @staticmethod
    def get_clause_from_regex_match(match):
        """ Construct a Clause object from a regex match

        :param match: re match object
        """
        name = match.group(1)
        parameters_str = match.group(2).split(',')
        parameters = list(map(lambda x: FileParser.get_parameter_from_string(x), parameters_str))

        return Clause(name, parameters)

    @staticmethod
    def get_fact_from_regex_match(match):
        """ Construct a Fact object from a regex match

        :param match: re match object
        """
        name = match.group(1)
        parameters_str = match.group(2).split(',')
        parameters = list(map(lambda x: Constant(x), parameters_str))

        return Fact(name, parameters)

    @staticmethod
    def get_predicate_from_regex_match(match):
        """ Construct a Predicate object from a regex match

        :param match: re match object
        """
        name = match.group(1)
        parameters_str = match.group(2).split(',')
        parameters = list(map(lambda x: Variable(x[1:]), parameters_str))

        return Predicate(name, parameters)

    @staticmethod
    def get_rule_from_regex_match(match):
        """ Construct a Rule object from a regex match

        :param match: re match object
        """
        head_rgx = FileParser.REGEX_CLAUSE.match(match.group(2))
        head = FileParser.get_clause_from_regex_match(head_rgx)

        body_str = match.group(1).split('),')
        body = []
        for idx, body_clause in enumerate(body_str):
            if idx < len(body_str) - 1:
                body_clause += ')'
            body_clause_rgx = FileParser.REGEX_CLAUSE.match(body_clause)
            body.append(FileParser.get_clause_from_regex_match(body_clause_rgx))

        return Rule(head, body)
