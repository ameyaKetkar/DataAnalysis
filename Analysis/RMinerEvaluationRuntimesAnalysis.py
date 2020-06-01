import statistics
from collections import Counter as C
from collections import namedtuple as nt
from os.path import dirname as parent
from os.path import join as join
from os.path import realpath as realpath
import Analysis.CreatePlots as cp
import git
import time
import pandas as pd
import scipy.stats as stats
import scikit_posthocs as posthocs
import PrettyPrint as Pretty
from Analysis.AnalysisFns import tca_tci_analysis, theWorldContains, mergeDict, mergeDictSet
from Analysis.RW import readAll
import re

tools = {
    "RefactoringMiner 2.0": "/Users/ameya/Research/RMinerEvaluationTools/Runtimes/RMiner2_analyzed.txt"
    , "RefactoringMiner 1.0": "/Users/ameya/Research/RMinerEvaluationTools/Runtimes/RMiner1_analyzed.txt"
    , "RefDiff 2.0": "/Users/ameya/Research/RMinerEvaluationTools/Runtimes/Runtime2x_analyzed.txt"
    , "RefDiff 0.1.1": "/Users/ameya/Research/RMinerEvaluationTools/Runtimes/Runtime011_analyzed.txt"
    , "RefDiff 1.0": "/Users/ameya/Research/RMinerEvaluationTools/Runtimes/Runtime1x_analyzed.txt"
}

d = {}
for tool in tools:
    data = pd.read_csv(tools[tool])
    print(tool)
    # if tool == "RefactoringMiner 2.0":
    d[tool] = data[" Runtime"].tolist()
    print(data.sort_values(" Runtime"))

cp.violin(d, "Tool", "Runtime",  isVertical=True, isLog=True, height=5, width= 14, legendDontOVerlap= True)
