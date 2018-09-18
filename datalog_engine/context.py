
class ProgramContext:
    """ Store the rules, facts and IDBs information for a program instance and tries to solve the query() rules

    """
    def __init__(self):
        self._predicates = {}
        self._facts = {}
        self._rules = {}

        self.queries = set()

    def solve_queries(self):
        """ For each query in program context, try to solve it and print results

        """
        print("---------------------------------------------")
        print(" Solving Queries :")
        print("---------------------------------------------\n")
        for query in self.queries:
            binds = self.get_variables_binds(query, recursion_level=10)
            print("QUERY : " + str(query))
            for bind in binds:
                print("Answers :", bind)
            print()

    def check_program_validity(self):
        """ Run through every fact and rule to check their validity

        :return: Raise Exception on any invalid Clause
        """
        for fact in self._facts:
            if fact not in self._predicates:
                raise Exception("Invalid fact, no IDB defined: " + fact)
            for clause in self._facts[fact]:
                self.check_clause_validity(clause)

        for rule in self._rules:
            if rule not in self._predicates:
                raise Exception("Invalid rule, no IDB defined: " + rule)
            for clause in self._rules[rule]:
                self.check_clause_validity(clause.head)
                for body_clause in clause.body:
                    self.check_clause_validity(body_clause)

    def check_clause_validity(self, clause):
        """ Check arity of a clause against the context IDB definition

        :param clause: Clause to check
        :return: Raise Exception on invalid arity
        """
        expected_arity = len(self._predicates[clause.name][0].parameters)
        if len(clause.parameters) != expected_arity:
            raise Exception("Wrong clause arity, expected " + str(expected_arity) + " parameters got " + str(len(clause.parameters)) + " for " + clause.name)

    @staticmethod
    def substitute_variable_names(variables_binds, from_clause, to_clause):
        """ Compute new variables binds from a clause to a identical clause with possible different variables names

        :param variables_binds: Variables binds from old clause
        :param from_clause: Clause to convert binds for
        :param to_clause: Old clause
        :return: variables binds adapted to new clause
        """
        new_binds = []
        substitute = {}
        for index, param in enumerate(from_clause.parameters):
            if not param.is_constant() and not to_clause.parameters[index].is_constant():
                from_var_name = param.name
                to_var_name = to_clause.parameters[index].name
                substitute[from_var_name] = to_var_name

        for b in variables_binds:
            new_bind = {}
            for name, value in b.items():
                if name in substitute:
                    new_bind[substitute[name]] = value
            if len(new_bind):
                new_binds.append(new_bind)

        return new_binds

    def get_variables_binds(self, predicate, bound_variables=None, variables_binds=None, recursion_level=1):
        """ Find possible binds for predicate

        :param predicate: Predicate object
        :param bound_variables: Set of variables bounds (argument information)
        :param variables_binds: List of dictionaries defining variables binds
        :param recursion_level: Current level of recursion defining how far we can explore the sub-rules
        :return: Yield possible binds objects
        """

        # print("EXPLORING", recursion_level, predicate, variables_binds)

        # Set of bound variables in predicate body
        if bound_variables is None:
            bound_variables = set()

        # Possible binds
        if variables_binds is None:
            variables_binds = [{}]

        recursion_level -= 1

        new_possible_binds = []

        for body_clause in predicate.body:
            adornments = self.compute_adornments(body_clause.parameters, bound_variables)

            # For each fact search if we can match every bound variable and assign free ones
            if body_clause.name in self._facts:
                for fact in self._facts[body_clause.name]:
                    possible_binds = self.check_fact_with_adornment(fact, body_clause, adornments, variables_binds)
                    if len(possible_binds):
                        # A fact matched, we add variables binds to sup
                        new_possible_binds.extend(possible_binds)

            # if len(new_possible_binds):
            #     variables_binds = new_possible_binds

            if recursion_level > 0:
                # For each rule
                if body_clause.name in self._rules:
                    for applicable_rule in self._rules[body_clause.name]:

                        n_bound_variables = set()
                        n_variables_binds = [{}]

                        for index, argument in enumerate(body_clause.parameters):
                            rule_corresponding_parameter = applicable_rule.head.parameters[index]

                            if rule_corresponding_parameter.is_constant():
                                if argument.is_constant():
                                    if rule_corresponding_parameter.value != argument.value:
                                        break
                            else:
                                if adornments[index]:
                                    if argument.is_constant():
                                        n_bound_variables.add(rule_corresponding_parameter.name)
                                        n_variables_binds[0][rule_corresponding_parameter.name] = argument.value
                                    elif argument.name in bound_variables and argument.name in variables_binds[0]:
                                        n_bound_variables.add(rule_corresponding_parameter.name)
                                        n_variables_binds[0][rule_corresponding_parameter.name] = variables_binds[0][argument.name]

                        applicable_predicate_binds = self.get_variables_binds(applicable_rule, n_bound_variables, n_variables_binds, recursion_level)
                        for n_bind in applicable_predicate_binds:
                            adapted_bind = self.substitute_variable_names(n_bind, applicable_rule.head, body_clause)
                            new_possible_binds.extend(adapted_bind)

            if len(new_possible_binds):
                variables_binds = new_possible_binds.copy()
                new_possible_binds.clear()
            else:
                variables_binds = [{}]

        new_possible_binds_no_duplicates = self.remove_duplicate_binds(variables_binds)

        if len(new_possible_binds_no_duplicates):
            yield new_possible_binds_no_duplicates

    @staticmethod
    def compute_adornments(parameters, bound_variables):
        """ For all parameters, compute their adornments according to bound variables

        :param parameters: Predicate parameters
        :param bound_variables: set of bound variables
        :return: Array of adornments with constant value if constant or boolean indicating variable bind status
        """
        adornments = [None] * len(parameters)

        for index, argument in enumerate(parameters):
            if argument.is_constant() or argument.name in bound_variables:
                adornments[index] = True
            else:
                adornments[index] = False
                bound_variables.add(argument.name)

        return adornments

    def check_fact_with_adornment(self, fact, body_clause, adornments, possible_binds):
        """ Check if a fact is applicable for a predicate by checking possibles binds with adornments

        :param fact: Fact object from the same rule as clause
        :param body_clause: parameters of clause
        :param adornments: adornments array from compute_adornments
        :param possible_binds: binds previously founds
        :return: Array of binds applicable with fact
        """
        new_possible_binds = []
        for bind in possible_binds:
            new_bind = self.check_fact_with_binding(fact, body_clause, adornments, bind)
            if new_bind:
                new_possible_binds.append(new_bind)
        return new_possible_binds

    @staticmethod
    def check_fact_with_binding(fact, body_clause, adornments, bind):
        """ Check if fact is applicable with specific variables binds

        :param fact: Fact to check
        :param body_clause: parameters from clause
        :param adornments: adornments computed for clause
        :param bind: object of variables and their bindings
        :return: object of variables and their bindings
        """

        possible_bind = bind.copy()

        for index, argument in enumerate(body_clause.parameters):
            if adornments[index]:
                # Bind previously affected value match
                if argument.is_constant():
                    if argument.value != fact.parameters[index].value:
                        return False
                elif argument.name not in possible_bind or possible_bind[argument.name] != fact.parameters[index].value:
                    return False
            else:
                # No bound we assign fact value
                possible_bind[argument.name] = fact.parameters[index].value

        return possible_bind

    @staticmethod
    def remove_duplicate_binds(variable_binds):
        """ Run through each binds and remove possible duplicates

        :param variable_binds: List of binds dictionaries
        :return: List of binds dictionary purged from the duplicate instances
        """
        no_duplicates = []
        seen = set()
        for bind in variable_binds:
            t = tuple(bind.items())
            if t not in seen:
                seen.add(t)
                no_duplicates.append(bind)

        return no_duplicates

    """
    GETTERS AND SETTERS FOR CONTEXT ATTRIBUTES
    Initialise empty list, sets and dictionary on first clause access
    """

    def get_predicate_by_name(self, name):
        if name not in self._predicates:
            self._predicates[name] = []
        return self._predicates[name]

    def get_fact_by_name(self, name):
        if name not in self._facts:
            self._facts[name] = set()
        return self._facts[name]

    def get_rule_by_name(self, name):
        if name not in self._rules:
            self._rules[name] = set()
        return self._rules[name]

    def add_predicate(self, predicate):
        self.get_predicate_by_name(predicate.name).append(predicate)

    def add_fact(self, fact):
        self.get_fact_by_name(fact.name).add(fact)

    def add_rule(self, rule):
        name = rule.head.name
        if name == "query":
            self.queries.add(rule)
        else:
            self.get_rule_by_name(name).add(rule)

    def __str__(self):
        """ Print a nice version of the current context

        """
        context_print = "EDB :\n"
        for fact_name, facts in self._facts.items():
            for f in facts:
                context_print += "  " + str(f) + ".\n"

        context_print += "\nIDB :\n"
        for predicates in self._predicates.values():
            for predicate in predicates:
                context_print += "  " + str(predicate) + ".\n"

        context_print += "\nMAPPING :\n"
        for rule_name, rules in self._rules.items():
            for r in rules:
                context_print += "  " + str(r) + ".\n"

        context_print += "\nQUERY :\n"
        for q in self.queries:
            context_print += "  " + str(q) + ".\n"

        return context_print
