# Look for #IMPLEMENT tags in this file. These tags indicate what has
# to be implemented to complete problem solution.

'''This file will contain different constraint propagators to be used within
   bt_search.

   propagator == a function with the following template
      propagator(csp, newVar=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

      csp is a CSP object---the propagator can use this to get access
      to the variables and constraints of the problem. The assigned variables
      can be accessed via methods, the values assigned can also be accessed.

      newVar (newly instaniated variable) is an optional argument.
      if newVar is not None:
          then newVar is the most
           recently assigned variable of the search.
      else:
          progator is called before any assignments are made
          in which case it must decide what processing to do
           prior to any variables being assigned. SEE BELOW

       The propagator returns True/False and a list of (Variable, Value) pairs.
       Return is False if a deadend has been detected by the propagator.
       in this case bt_search will backtrack
       return is true if we can continue.

      The list of variable values pairs are all of the values
      the propagator pruned (using the variable's prune_value method).
      bt_search NEEDS to know this in order to correctly restore these
      values when it undoes a variable assignment.

      NOTE propagator SHOULD NOT prune a value that has already been
      pruned! Nor should it prune a value twice

      PROPAGATOR called with newVar = None
      PROCESSING REQUIRED:
        for plain backtracking (where we only check fully instantiated
        constraints)
        we do nothing...return true, []

        for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope
        contains only one variable) and we forward_check these constraints.

        for gac we establish initial GAC by initializing the GAC queue
        with all constaints of the csp


      PROPAGATOR called with newVar = a variable V
      PROCESSING REQUIRED:
         for plain backtracking we check all constraints with V (see csp method
         get_cons_with_var) that are fully assigned.

         for forward checking we forward check all constraints with V
         that have one unassigned variable left

         for gac we initialize the GAC queue with all constraints containing V.
   '''


def prop_BT(csp, newVar=None):
    '''Do plain backtracking propagation. That is, do no
    propagation at all. Just check fully instantiated constraints'''

    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []


def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return '''
    constraints = csp.get_all_cons()
    if newVar:
        constraints = csp.get_cons_with_var(newVar)

    # filter out all with > 1 unassigned variables
    constraints = [constraint for constraint in constraints if constraint.get_n_unasgn() == 1]

    pruned_vals = []
    found_deadend = True

    for constraint in constraints:
        variables = constraint.get_scope()
        values = [variable.get_assigned_value() for variable in variables]

        unassigned_variable = constraint.get_unasgn_vars()[0]
        found_deadend = False

        for domain_value in unassigned_variable.cur_domain():
            copied_values = [
                value
                if value is not None else domain_value
                for value in values
            ]

            if not constraint.check(copied_values):
                unassigned_variable.prune_value(domain_value)
                pruned_vals.append((unassigned_variable, domain_value))
            else:
                found_deadend = True

    return found_deadend, pruned_vals


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    constraints = csp.get_all_cons()
    if newVar:
        constraints = csp.get_cons_with_var(newVar)

    pruned_vals = []
    while constraints:
        constraint = constraints.pop(0)

        for variable in constraint.get_scope():
            for domain_value in variable.cur_domain():
                if not constraint.has_support(variable, domain_value):
                    variable.prune_value(domain_value)
                    pruned_vals.append((variable, domain_value))

                    if not variable.cur_domain_size():
                        # Domain wipeout
                        return False, pruned_vals

                    new_constraints = [
                        constr
                        for constr in csp.get_cons_with_var(variable)
                        if constr not in constraints
                    ]
                    constraints.extend(new_constraints)

    # No domain wipeout
    return True, pruned_vals
