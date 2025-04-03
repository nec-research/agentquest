import io
import os
import sys
import shutil
import tempfile

from typing import List

from ctypes import cdll, CDLL
from ctypes import Structure
from ctypes import POINTER, c_void_p, c_char, c_int, c_char_p, c_bool

from pkg_resources import Requirement, resource_filename

DOWNWARD_PATH = resource_filename(Requirement.parse("fast_downward"), "fast_downward")
DOWNWARD_LIB_PATH = os.path.join(DOWNWARD_PATH, "libdownward.so")

# Function to unload a shared library.
dlclose_func = CDLL(None).dlclose  # This WON'T work on Win
dlclose_func.argtypes = [c_void_p]


class CapturingStdout(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = io.StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


class Operator(Structure):
    """
    An Operator object contains the following fields:

    :param num: Operator ID
    :type num: int
    :param name: Operator name
    :type name: string

    ..warning this class must reflect the C struct in interface.cc.

    """

    _fields_ = [
        ("id", c_int),
        ("_name", c_char * 1024),  # Fixed-length name.
        ("nb_effect_atoms", c_int),
    ]

    def __init__(self, id=-1, name=b"", nb_effect_atoms=0):
        self.id = id
        self.nb_effect_atoms = nb_effect_atoms
        self._name = name

    def __str__(self):
        return "Id {}:\t{}".format(self.id, self.name)

    def __repr__(self):
        return str(self)

    @property
    def name(self):
        return self._name.decode("cp1252")


class Atom(Structure):
    """
    An Atom object contains the following fields:

    :param num: Operator ID
    :type num: int
    :param name: Operator name
    :type name: string

    ..warning this class must reflect the C struct in interface.cc.

    """

    _fields_ = [
        ("_name", c_char * 1024),  # Fixed-length name.
    ]

    def __init__(self):
        self._name = ""

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return str(self)

    @property
    def name(self):
        return self._name.decode("cp1252")


def load_lib():
    """Loads a copy of fast-downward's shared library."""

    # Make a copy of libdownward.so before loading it to avoid concurrency issues.
    tmpdir = tempfile.TemporaryDirectory().name
    os.mkdir(tmpdir)
    # with tempfile.TemporaryDirectory() as tmpdir:
    downward_lib_path = os.path.join(tmpdir, "libdownward.so")
    if not os.path.isfile(DOWNWARD_LIB_PATH):
        raise RuntimeError("Can't find: {}".format(DOWNWARD_LIB_PATH))

    shutil.copyfile(DOWNWARD_LIB_PATH, downward_lib_path)
    downward_lib = cdll.LoadLibrary(downward_lib_path)

    downward_lib.load_sas.argtypes = [c_char_p]
    downward_lib.load_sas.restype = None

    downward_lib.load_sas_replan.argtypes = [c_char_p]
    downward_lib.load_sas_replan.restype = None

    downward_lib.cleanup.argtypes = []
    downward_lib.cleanup.restype = None

    downward_lib.get_applicable_operators_count.argtypes = []
    downward_lib.get_applicable_operators_count.restype = int
    downward_lib.get_applicable_operators.argtypes = [POINTER(Operator)]
    downward_lib.get_applicable_operators.restype = None

    downward_lib.get_state_size.argtypes = []
    downward_lib.get_state_size.restype = int
    downward_lib.get_state.argtypes = [POINTER(Atom)]
    downward_lib.get_state.restype = None

    downward_lib.apply_operator.argtypes = [c_int, POINTER(Atom)]
    downward_lib.apply_operator.restype = int

    downward_lib.check_goal.argtypes = []
    downward_lib.check_goal.restype = bool

    downward_lib.solve.argtypes = [c_bool]
    downward_lib.solve.restype = bool

    downward_lib.solve_sas.argtypes = [c_char_p, c_bool]
    downward_lib.solve_sas.restype = bool

    downward_lib.replan.argtypes = [c_bool]
    downward_lib.replan.restype = bool

    downward_lib.get_last_plan_length.argtypes = []
    downward_lib.get_last_plan_length.restype = int

    downward_lib.get_last_plan.argtypes = [POINTER(Operator)]
    downward_lib.get_last_plan.restype = None

    downward_lib.check_solution.argtypes = [c_int, POINTER(Operator)]
    downward_lib.check_solution.restype = bool
    shutil.rmtree(tmpdir, ignore_errors=True)

    return downward_lib


def compress_plan(lib, plan):
    if lib.check_solution(len(plan), plan):
        return plan

    def _find_shorter_plan(plan):
        for j in range(0, len(plan)):
            for i in range(j + 1, len(plan))[::-1]:
                shorter_plan = plan[:j] + plan[i:]
                shorter_plan = (Operator * len(shorter_plan))(*shorter_plan)
                if lib.check_solution(len(shorter_plan), shorter_plan):
                    return shorter_plan

        return None

    shorter_plan = _find_shorter_plan(plan)
    if shorter_plan:
        return shorter_plan

    # Try recovering from the last operation.
    operators = (Operator * lib.get_applicable_operators_count())()
    lib.get_applicable_operators(operators)

    # print("Operators:\n -> " +"\n -> ".join(_demangle_alfred_name(op.name) for op in operators))

    plan = list(plan)
    for operator in operators:
        new_plan = [operator] + plan
        new_plan = (Operator * len(new_plan))(*new_plan)

        if lib.check_solution(len(new_plan), new_plan):
            return new_plan

        shorter_plan = _find_shorter_plan(new_plan)
        if shorter_plan:
            return shorter_plan

    # assert False
    return None


def names2operators(lib, cmds):
    operators = (Operator * len(cmds))()
    for operator, cmd in zip(operators, cmds):
        operator.id = lib.get_operator_id_from_name(cmd.encode())
        operator._name = cmd.encode()
        assert operator.id > -1

    return operators


def solve_pddl(
    domain: str, problem: str, verbose=False, return_raw_operators=False
) -> List[str]:
    lib = load_lib()
    _, sas = pddl2sas(domain, problem, verbose=verbose, optimize=True)
    if not lib.solve_sas(sas.encode("utf-8"), verbose):
        return None

    operators = (Operator * lib.get_last_plan_length())()
    lib.get_last_plan(operators)

    if return_raw_operators:
        return operators

    operators = [op.name for op in operators]
    return operators


def close_lib(downward_lib):
    downward_lib.cleanup()
    dlclose_func(downward_lib._handle)


def pddl2sas(domain: str, problem: str, verbose: bool = False, optimize=False) -> str:
    """Converts a PDDL domain-problem to fast-downward planning task format (SAS).

    Arguments:
        domain: text content of the PDDL file describing the domain.
        problem: text content of the PDDL file describing the problem.
        verbose: display information about PDDL->SAS conversion.

    Returns:
        planning task described in the SAS format understood by fast-downward.
    """
    # HACK: modify sys.argv according to what module `options` expects.
    import sys

    sys.argv = ["translate.py", "domain", "task"]
    from fast_downward.translate import options
    from fast_downward.translate import normalize
    from fast_downward.translate import translate
    from fast_downward.translate.pddl_parser import lisp_parser, parsing_functions

    if optimize:
        # Optimize translation for faster search.
        options.filter_unimportant_vars = True
        options.filter_unreachable_facts = True
        options.use_partial_encoding = True
        options.skip_variable_reordering = False
        options.add_implied_preconditions = True
        options.invariant_generation_max_candidates = 0
        # options.generate_relaxed_task = True
    else:
        # Do not optimize translation to avoid pruning operators and facts.
        options.filter_unimportant_vars = False
        options.filter_unreachable_facts = False
        options.use_partial_encoding = False
        options.skip_variable_reordering = True
        options.add_implied_preconditions = False
        options.invariant_generation_max_candidates = 0
        # options.generate_relaxed_task = True

    with CapturingStdout() as stdout:
        # Load task.
        domain_pddl = lisp_parser.parse_nested_list(domain.split("\n"))
        problem_pddl = lisp_parser.parse_nested_list(problem.split("\n"))
        task = parsing_functions.parse_task(domain_pddl, problem_pddl)

        normalize.normalize(task)
        sas_task = translate.pddl_to_sas(task)

        # Write SAS file to a string to avoid I/O.
        sas_io = io.StringIO()
        sas_task.output(sas_io)
        sas_io.seek(0)
        sas = sas_io.read()

    if verbose:
        print("\n".join(stdout))

    return task, sas
