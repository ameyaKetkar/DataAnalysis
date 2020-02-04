from Analysis.RW import readAll
import pandas as pd
from pandas import DataFrame as df
from collections import Counter as C


def labelRefactoring(ref: str) -> str:
    if "Type" in ref:
        return "Change Type"
    if "Extract" in ref:
        if "class" not in ref and "Class" not in ref and "Interface" not in ref:
            return "Extract"
    if "Inline" in ref:
        return "Others"
    if "Move" in ref:
        if "class" not in ref and "Class" not in ref and "Interface" not in ref:
            return "Move"
    if "Rename" in ref:
        if "class" not in ref and "Class" not in ref and "Interface" not in ref:
            return "Rename"
    return "Others"


def genLatexNewCommandLong(commandName: str, value: int) -> str:
    return "\\newcommand{" + commandName + "}{" + f'{value:,}' + "}"

def isDependencyUpdate(c):
    return len(c.dependencyUpdate.added) > 0 or len(c.dependencyUpdate.removed) > 0 or len(c.dependencyUpdate.update) > 0


projs = readAll("Projects", "Project")

refactorings = []
latexCommandsInts = C({})
latexCommandsFPs = C({})
for p in projs:
    latexCommandsInts += C({'corpusSize': 1})
    commits = readAll("commits_" + p.name, "Commit")
    latexCommandsInts += C({'noOfCommitsAnalyzed': len(commits)})
    for c in commits:
        if isDependencyUpdate(c):
            latexCommandsInts += C({'commitsWithDependencyUpd': 1})
        if len(c.refactorings) > 0:
            latexCommandsInts += C({'commitsWithRefactoring': 1})
            if c.isTypeChangeReported:
                latexCommandsInts += C({'commitsWithCTT': 1})
                if isDependencyUpdate(c):
                    latexCommandsInts += C({'commitsWithCTTAndDependencyUpd': 1})
            refs = list(map(lambda r: (labelRefactoring(r.name), r.name, r.occurences), c.refactorings))
            refactorings.extend(refs)
            if any(r[0] == "Rename" for r in refs):
                latexCommandsInts += C({'commitsWithRename': 1})
            if any(r[0] == "Extract" for r in refs):
                latexCommandsInts += C({'commitsWithExtract': 1})
            if any(r[0] == "Move" for r in refs):
                latexCommandsInts += C({'commitsWithMove': 1})
            latexCommandsInts += C({'NoOfRefactoringsMined': len(c.refactorings)})

refactoringDf = pd.DataFrame(refactorings, columns=['Kind', 'Refactoring', 'Occurences'])

refByType = refactoringDf.groupby("Refactoring")["Occurences"].sum()

refByKind = refactoringDf.groupby('Kind')['Occurences'].sum()

latexCommandsInts += C({'noOfOtherRef': refByKind["Others"]})
latexCommandsInts += C({'noOfExtracts': refByKind["Extract"]})
latexCommandsInts += C({'noOfRenames': refByKind["Rename"]})
latexCommandsInts += C({'noOfMoves': refByKind["Move"]})
latexCommandsInts += C({'noOfCTT': refByKind["Change Type"]})

latexCommandsInts += C({'noOfCTTParam': refByType["Change Parameter Type"]})
latexCommandsInts += C({'noOfCTTRet': refByType["Change Return Type"]})
latexCommandsInts += C({'noOfCTTField': refByType["Change Attribute Type"]})
latexCommandsInts += C({'noOfCTTVar': refByType["Change Variable Type"]})

latexCommandsInts += C({'noOfRenameMethod': refByType["Rename Method"]})
latexCommandsInts += C({'noOfRenameParam': refByType["Rename Parameter"]})
latexCommandsInts += C({'noOfRenameField': refByType["Rename Attribute"]})
latexCommandsInts += C({'noOfRenameVar': refByType["Rename Variable"]})
latexCommandsInts += C({'noOfExtractVar': refByType["Extract Variable"]})
latexCommandsInts += C({'noOfExtractMethod': refByType["Extract Method"]})

latexCommandsFPs += C({'CTTvsRename': latexCommandsInts['noOfCTT'] / latexCommandsInts['noOfRenames']})
latexCommandsFPs += C({'CTTvsMove': latexCommandsInts['noOfCTT'] / latexCommandsInts['noOfMoves']})
latexCommandsFPs += C({'CTTvsExtract': latexCommandsInts['noOfCTT'] / latexCommandsInts['noOfExtracts']})

latexCommandDFInt = pd.DataFrame.from_dict(dict(latexCommandsInts), orient='index', columns=['Value'])
latexCommandDFFP = pd.DataFrame.from_dict(dict(latexCommandsFPs), orient='index', columns=['Value'])

print(latexCommandDFInt)
print(latexCommandDFFP)

