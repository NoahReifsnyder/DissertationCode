import importlib
from Problems.SND.MWO_SND import *
def run(s_p):
    domain, domain_type = s_p.split("_")
    problem_file = "Problems." + domain_type + "."+domain+"P_"+domain_type
    operator_file = "Problems." + domain_type + "."+domain+"O_"+domain_type
    problem_file = importlib.import_module(problem_file)
    operator_file = importlib.import_module(operator_file)
    problem_file.run()

