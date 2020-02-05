from numpy import take

from Analysis.RW import readAll
import pandas as pd
from pandas import DataFrame as df
from collections import Counter as C
from collections import namedtuple as nt
from os.path import join as join
from os.path import dirname as parent
from os.path import realpath as realPath

from ElementKind_pb2 import ElementKind
from PrettyPrint import pretty, prettyNameSpace
import Analysis.CreatePlots as cp
from TypeChangeAnalysis_pb2 import TypeChangeAnalysis

TypeChange = nt('TypeChange', ['before', 'after'])
Mapping = nt ('Mapping',['nameB4', 'nameAfter', 'before', 'after'])
TypeChangeExample = nt('TypeChangeExample', ['before', 'after', 'mappings'])

projs = readAll("Projects", "Project")
fileDir = parent(parent(parent(realPath('__file__'))))
pathToTypeChanges = join(fileDir, 'TypeChangeMiner/Output/')
latexCommandsInts = C({})
latexCommandsFP = C({})
typeChanges = C({})
visibilityStats, transformationStats, elementKindStats, nameSpaceStats = {}, {}, {}, {}
adaptationComplexity = {}

typeChangeExamples = []


def getMapping(tci):
    mapping = []
    for c in tci.codeMapping:
        if not c.isSame:
            mapping.append(Mapping(nameB4=tci.nameB4, nameAfter=tci.nameAfter, before=c.b4, after= c.after))
    return mapping

def getAdaptationComplexity(tca: TypeChangeAnalysis) -> float:
    c = 0
    tc = 0
    for t in tca.typeChangeInstances:
        tc += len(t.codeMapping)
        c += sum(not c.isSame for c in t.codeMapping)
    return 0.0 if tc == 0 else c / tc


for p in projs:
    typeChangeCommits = readAll("TypeChangeCommit_" + p.name, "TypeChangeCommit", protos=pathToTypeChanges)
    if len(typeChangeCommits) > 0:
        print(p.name + "   " + str(len(typeChangeCommits)))
        for t in typeChangeCommits:
            for tca in t.typeChanges:
                noOfTypeChangeInstances = len(tca.typeChangeInstances)
                # RQ1
                latexCommandsInts += C({'noOfTypeChanges': 1})
                typeChanges += C({TypeChange(before=pretty(tca.b4), after=pretty(tca.aftr)): 1})
                for tci in tca.typeChangeInstances:
                    # RQ1
                    latexCommandsInts += C({'noOfTCIs': 1})
                    # RQ3
                    latexCommandsInts += C({'noOf' + tci.visibility + 'TCI': 1})

                    if tci.nameB4 != tci.nameAfter:
                        latexCommandsInts += C({'noOfRenmeAndTCI': 1})

                    # RQ3
                    latexCommandsInts += C({'noOf' + tci.syntacticUpdate.transformation.replace(' ', ''): 1})

                    # RQ3 (Binary and Source Incompatibility)
                    if tci.visibility == 'public':
                        if tca.primitiveInfo.widening:
                            latexCommandsInts += C({'noOfPublicWideningTCI': 1})
                        if tci.elementKindAffected == ElementKind.Return and tca.hierarchyRelation == 'T_SUPER_R':
                            latexCommandsInts += C({'noOfPublicRetTypeToSubTypeTCI': 1})
                        if tci.elementKindAffected == ElementKind.Parameter and tca.hierarchyRelation == 'R_SUPER_T':
                            latexCommandsInts += C({'noOfPublicRetTypeToSubTypeTCI': 1})
                        if tci.elementKindAffected == ElementKind.Return and tca.primitiveInfo.narrowing:
                            latexCommandsInts += C({'noOfPublicRetTypeNarrowTCI': 1})
                        if tca.primitiveInfo.narrowing:
                            latexCommandsInts += C({'noOfPublicNarrowTCI': 1})
                        if tca.primitiveInfo.boxing or tca.primitiveInfo.unboxing:
                            latexCommandsInts += C({'noOfPublicPrimitiveWrapUnwrapTCI': 1})
                        if tca.primitiveInfo.widening and tci.elementKindAffected == ElementKind.Parameter:
                            latexCommandsInts += C({'noOfPublicParamPrimitiveWideningTCI': 1})
                        # RQ4 Namespace analysis
                        latexCommandsInts += C({"noOf" + prettyNameSpace(tca.nameSpacesB4) + "To" + prettyNameSpace(
                            tca.nameSpaceAfter): 1})

                # RQ4
                if tca.hierarchyRelation != '':
                    latexCommandsInts += C({'noOf' + tca.hierarchyRelation + 'TC': 1})
                    # RQ5
                    if tca.hierarchyRelation == "T_SUPER_R" or tca.hierarchyRelation == "R_SUPER_T":
                        adaptationComplexity.setdefault("Parent Child", []).append(getAdaptationComplexity(tca))
                    if tca.hierarchyRelation == "SIBLING":
                        adaptationComplexity.setdefault("Sibling", []).append(getAdaptationComplexity(tca))

                if tca.b4ComposesAfter:
                    latexCommandsInts += C({'noOfCompositionTC': 1})
                    adaptationComplexity.setdefault("Composition", []).append(getAdaptationComplexity(tca))
                    mapping = []
                    for tci in tca.typeChangeInstances:
                            m = getMapping(tci)
                            if len(m) > 0:
                                mapping.append(m)
                    if len(mapping) > 0:
                        typeChangeExamples.append(TypeChangeExample(before=pretty(tca.b4), after=pretty(tca.aftr), mappings= mapping))

                if tca.primitiveInfo.widening:
                    latexCommandsInts += C({'noOfWideningTCI': len(tca.typeChangeInstances)})
                if tca.primitiveInfo.narrowing:
                    latexCommandsInts += C({'noOfNarrowingfTCI': len(tca.typeChangeInstances)})
                if tca.primitiveInfo.boxing:
                    latexCommandsInts += C({'noOfBoxingTCI': len(tca.typeChangeInstances)})
                if tca.primitiveInfo.unboxing:
                    latexCommandsInts += C({'noOfUnBoxingTCI': len(tca.typeChangeInstances)})

                stats = tca.typeChangeStats

                # RQ3 (Visibility ratios)
                for k, v in stats.visibilityStats.items():
                    if v > 1.0:
                        v = 1.0
                    visibilityStats.setdefault(k, []).append(v)
                # RQ3 (Syntactic update ratios)
                for k, v in stats.transformationStats.items():
                    if v > 1.0:
                        v = 1.0
                    transformationStats.setdefault(k, []).append(v)
                # RQ1 (Element kind ratios)
                for k, v in stats.elementKindStats.items():
                    if v > 1.0:
                        v = 1.0
                    elementKindStats.setdefault(k, []).append(v)
                # RQ4 (Namespace ratios)
                for k, v in stats.nameSpaceStats.items():
                    if v > 1.0:
                        v = 1.0
                    nameSpaceStats.setdefault(k, []).append(v)

            # RQ5
            for migration in t.migrationAnalysis:
                latexCommandsInts += C({'noOf' + migration.typeMigrationLevel + ' Migrations': 1})

# RQ4 (Hierarchy Analysis)
latexCommandsInts += C({"noOfHierarchyTC": latexCommandsInts['noOfT_SUPER_RTC ']
                                           + latexCommandsInts['noOfR_SUPER_TTC']
                                           + latexCommandsInts['noOfSIBLINGTC']})
latexCommandsFP += C(
    {'PercentHierarchyTC': latexCommandsInts['noOfHierarchyTC'] / latexCommandsInts['noOfTypeChanges']})
latexCommandsFP += C(
    {'PercentCompositionTC': latexCommandsInts['noOfCompositionTC'] / latexCommandsInts['noOfTypeChanges']})

tcs = sorted(typeChanges.items(), reverse=True, key=lambda x: x[1])


cp.violin(adaptationComplexity)

cp.violin(elementKindStats)

cp.violin(visibilityStats)

cp.violin(dict(filter(lambda x: 'DontKnow' not in x[0] and 'TypeVariable' not in x[0]
                      , sorted(nameSpaceStats.items(), key=lambda item: len(item[1]), reverse=True))))
cp.violin(transformationStats)

latexCommandDFInt = pd.DataFrame.from_dict(dict(latexCommandsInts), orient='index', columns=['Value'])
latexCommandDFFP = pd.DataFrame.from_dict(dict(latexCommandsFP), orient='index', columns=['Value'])
print(latexCommandDFInt.to_string())
print(latexCommandDFFP.to_string())
