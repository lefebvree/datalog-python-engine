
class Argument:
    def __init__(self):
        pass


class Constant(Argument):
    """ Argument immutable

    """
    def __init__(self, value):
        Argument.__init__(self)
        self.value = value

    def __str__(self):
        return 'c:' + self.value

    @staticmethod
    def is_constant():
        return True


class Variable(Argument):
    """ Argument initially starting with a $ sign, a name is associated to each variable

    """
    def __init__(self, name):
        Argument.__init__(self)
        self.name = name

    def __str__(self):
        return '$:' + self.name

    @staticmethod
    def is_constant():
        return False


class Clause:
    """ List of arguments defined by a name

    """
    def __init__(self, name, parameters):
        self.name = name

        self.parameters = parameters


class Fact(Clause):
    """ EDB statement only including constant arguments

    """
    def __init__(self, name, constants):
        Clause.__init__(self, name, constants)

    def __str__(self):
        string = self.name + " ("
        for idx, argument in enumerate(self.parameters):
            if idx != 0:
                string += ", "
            string += str(argument)
        string += ")"

        return string


class Predicate(Clause):
    """ IDB statement only including variable arguments

    """
    def __init__(self, name, parameters):
        Clause.__init__(self, name, parameters)

    def __str__(self):
        string = self.name + " ("
        for idx, argument in enumerate(self.parameters):
            if idx != 0:
                string += ", "
            string += str(argument)
        string += ")"

        return string


class Rule:
    """ MAPPING statement including a clause as its head and a list of clause as its body

    """
    def __init__(self, head, body):
        self.head = head
        self.body = body

    def __str__(self):
        string = ""
        for idx_clause, clause in enumerate(self.body):
            if idx_clause != 0:
                string += ", "
            string += clause.name + " ("
            for idx, argument in enumerate(clause.parameters):
                if idx != 0:
                    string += ", "
                string += str(argument)
            string += ")"

        string += " -> " + self.head.name + " ("
        for idx, argument in enumerate(self.head.parameters):
            if idx != 0:
                string += ", "
            string += str(argument)
        string += ")"

        return string
