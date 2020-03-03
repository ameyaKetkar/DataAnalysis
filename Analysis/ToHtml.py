import shutil
import html
# import OldModels.OldRW as OldRW
from jinja2 import Environment, FileSystemLoader
import os
from collections import Counter as C
from Analysis.RW import readAll
from collections import namedtuple as nt
from PrettyPrint import pretty, prettyNameSpace1

TypeChange = nt('TypeChange', ['before', 'after'])

pathToPages = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath('__file__'))), "docs/Pages")
pathToProjectsHtml = os.path.join(pathToPages, "projects.html")
pathToIndexFile = os.path.join(os.path.dirname(pathToPages), "index.html")

env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.dirname(os.path.realpath('__file__')))))
projectTemplate = env.get_template("HTMLTemplate/ProjectTemplate.html")
commitTemplate = env.get_template("HTMLTemplate/CommitSummaryTemplate.html")
detailedCommitTemplate = env.get_template("HTMLTemplate/DetailCommitTemplate.html")
indexTemplate = env.get_template("HTMLTemplate/IndexTemplate.html")

TypeChangeSummarytemplate = env.get_template("HTMLTemplate/TypeChangeSummaryTemplate.html")
templateTCI = env.get_template("HTMLTemplate/TypeChangeInstances.html")

projects = readAll('Projects', 'Project')
items = []

if os.path.isdir(pathToPages):
    shutil.rmtree(pathToPages)
try:
    os.mkdir(pathToPages)
except OSError:
    print("Could not make directory")

noOfProjects, noOfCommits, noOfRefactorings, noOfTypeChanges, noOfCommitsException = 0, 0, 0, 0, 0

for p in projects:
    noOfProjects += 1
    commits = readAll('commits_' + p.name, 'Commit')
    l = str(len(commits))
    d = dict(name=p.name, Url=p.url, totalCommits=p.totalCommits, CommitsAnalyzed=l,
             LinkToCommits=p.name + ".html")
    items.append(d)
    commitSummary = []
    for cmt in commits:
        noOfCommits += 1
        r = sum(list(map(lambda r: r.occurences, cmt.refactorings)))
        refactorings = []
        dependencies = []
        added = []
        removed = []
        updated = []

        for dep in cmt.dependencies:
            dependencies.append(dict(name=dep.artifactID + ":" + dep.groupID + ":" + dep.version))

        for dep in cmt.dependencyUpdate.added:
            added.append(dict(name=dep.artifactID + ":" + dep.groupID + ":" + dep.version))

        for dep in cmt.dependencyUpdate.removed:
            removed.append(dict(name=dep.artifactID + ":" + dep.groupID + ":" + dep.version))

        for dep in cmt.dependencyUpdate.update:
            updated.append(dict(
                name="From " + dep.before.artifactID + ":" + dep.before.groupID + "   " + dep.before.version + " To " + dep.after.version))

        depChanged = len(added) + len(removed) + len(updated) > 0

        commitSummary.append(dict(sha=cmt.sha, noOfJars=str(len(cmt.dependencies)),
                                  refactoringsLink=p.name + "/" + cmt.sha + ".html" if r > 0 or depChanged else None,
                                  noOfRefactoring=str(r),
                                  typeChangeFound='Yes' if cmt.isTypeChangeReported else 'No',
                                  dependenciesChanged='Yes' if depChanged else 'No',
                                  isException='Yes' if (cmt.exception != '') else 'No',
                                  exception=cmt.exception if cmt.exception != '' else '-'))

        if cmt.exception != '':
            noOfCommitsException += 1

        for ref in cmt.refactorings:
            noOfRefactorings += ref.occurences
            if ref.name.startswith('Change Parameter Type') or ref.name.startswith(
                    'Change Variable Type') or ref.name.startswith('Change Return Type') or ref.name.startswith('Change Attribute Type'):
                noOfTypeChanges += ref.occurences
            descrptions = []
            # print(type(ref.descriptionAndurl))
            for k, v in ref.descriptionAndurl.items():
                descrptions.append(dict(description=html.escape(k), frm=v.lhs, to=v.rhs))

            if descrptions is []:
                refactorings.append(dict(name=ref.name, occurence=ref.occurences, num=0))
            else:
                refactorings.append(
                    dict(name=ref.name, occurence=ref.occurences, descriptions=descrptions,
                         num=len(descrptions)))

        if len(refactorings) > 0 or depChanged:
            pathToCommitsInProject = os.path.join(pathToPages, p.name)
            pathToDetailedCommits = os.path.join(pathToCommitsInProject, cmt.sha + ".html")
            os.makedirs(os.path.dirname(pathToDetailedCommits), exist_ok=True)
            with open(pathToDetailedCommits, 'w+') as fh:
                fh.write(
                    detailedCommitTemplate.render(sha=cmt.sha, filesAdded=cmt.fileDiff.filesAdded,
                                                  filesRemoved=cmt.fileDiff.filesRemoved,
                                                  filesRenamed=cmt.fileDiff.filesRenamed,
                                                  filesModified=cmt.fileDiff.filesModified,
                                                  refactorings=refactorings,
                                                  dependencies=dependencies, projectName=p.name,
                                                  Added=added if added is not [] else None,
                                                  AddedNum=len(added),
                                                  Removed=removed if removed is not [] else None,
                                                  RemovedNum=len(removed),
                                                  Updated=updated if updated is not [] else None,
                                                  UpdatedNum=len(updated)))
                fh.write('\n')
                fh.close()

    pathToProjectCommits = os.path.join(pathToPages, p.name + ".html")
    with open(pathToProjectCommits, 'a') as fh:
        fh.write(commitTemplate.render(projectName=p.name, commits=commitSummary))
        fh.write('\n')
        fh.close()

with open(pathToProjectsHtml, 'a') as fh:
    fh.write(projectTemplate.render(projects=items))
    fh.write('\n')
    fh.close()

with open(pathToIndexFile, 'w+') as f:
    f.write(indexTemplate.render(NumberOfProjects=noOfProjects, NumberOfCommits=noOfCommits,
                                 NoOfRefactoring=noOfRefactorings, NumberOfTypeChanges=noOfTypeChanges,
                                 NumberOfExceptionCommits=noOfCommitsException))
    f.write('\n')
    f.close()

pathToPages = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath('__file__'))), "docs/Pages/AllTCA/")
os.mkdir(pathToPages)

typeChanges = {}
typeChanges_commit = {}
typeChange_project = {}
typeChange_hierarchy = {}
typeChange_nameSpace = {}
typeChange_primitiveInfo = {}
pop_typeChange_nameSpace = C({})

processedCodeMapping = readAll("ProcessedCodeMapping", "ProcessedCodeMapping",
                               protos="/Users/ameya/Research/TypeChangeStudy/TypeChangeMiner/Output/CodeMapping/")

x = set()
for pc in processedCodeMapping:
    if len(pc.relevantStmts) > 0:
        for rs in pc.relevantStmts:
            if len(rs.mapping) > 0:
                for em in rs.mapping:
                    x.add(em.replacement)

print(x)


def getStatementMapping(typechange):
    for p in processedCodeMapping:
        if pretty(p.b4) == typechange.before and pretty(p.aftr) == typechange.after:
            return p.relevantStmts

    return []


for p in projects:
    typeChangeCommits = readAll("TypeChangeCommit_" + p.name, "TypeChangeCommit",
                                protos="/Users/ameya/Research/TypeChangeStudy/TypeChangeMiner/Output/")

    commitSummary = []
    for cmt in typeChangeCommits:
        for tca in cmt.typeChanges:
            if not tca.b4.root.isTypeVariable and not tca.aftr.root.isTypeVariable:
                zzz = TypeChange(before=pretty(tca.b4), after=pretty(tca.aftr))
                if zzz.before == "":
                    print()
                typeChanges.setdefault(zzz, []).extend(tca.typeChangeInstances)
                typeChanges_commit.setdefault(zzz, set()).add(cmt.sha)
                typeChange_project.setdefault(zzz, set()).add(p.name)
                if tca.hierarchyRelation != '' and "NO" not in tca.hierarchyRelation:
                    typeChange_hierarchy[zzz] = tca.hierarchyRelation
                elif tca.b4ComposesAfter:
                    typeChange_hierarchy[zzz] = "Composition"
                elif tca.primitiveInfo is not None:
                    if tca.primitiveInfo.boxing:
                        typeChange_primitiveInfo[zzz] = "Boxing"
                    elif tca.primitiveInfo.unboxing:
                        typeChange_primitiveInfo[zzz] = "Unboxing"
                    elif tca.primitiveInfo.narrowing:
                        typeChange_primitiveInfo[zzz] = "Narrowing"
                    elif tca.primitiveInfo.widening:
                        typeChange_primitiveInfo[zzz] = "Widening"
                typeChange_nameSpace[zzz] = prettyNameSpace1(tca.nameSpacesB4) + " -> " + prettyNameSpace1(
                    tca.nameSpaceAfter)

typeChangeSummary = []

renameTypeChange = {}



tciCounter = 0
for k, v in typeChanges.items():
    if len(typeChange_project[k]) > 1:
        f = dict(TypeChange=html.escape(k.before + " to " + k.after),
                 hierarchy=typeChange_hierarchy[k] if k in typeChange_hierarchy.keys() else "-",
                 primitiveInfo=typeChange_primitiveInfo[k] if k in typeChange_primitiveInfo.keys() else "-",
                 namespace=typeChange_nameSpace[k] if k in typeChange_nameSpace.keys() else "-")

        mapping = getStatementMapping(k)

        minedReplacements = {}

        for m in mapping:
            for em in m.mapping:
                minedReplacements.setdefault(em.replacement, []).append(
                    dict(frm=html.escape(em.b4 if em.b4 else m.b4), to=html.escape(em.aftr if em.aftr else m.after),
                         urlB4=m.urlbB4,
                         urlAftr=m.urlAftr, stmtB4=m.b4, strmtAftr=m.after))
        mappings = []

        if typeChange_nameSpace[k] == 'Jdk -> Jdk':
            pop_typeChange_nameSpace += C({'Jdk -> Jdk': 1})
        elif 'Internal' in typeChange_nameSpace[k]:
            pop_typeChange_nameSpace += C({'InvolvesInternal': 1})
        elif 'External' in typeChange_nameSpace[k]:
            pop_typeChange_nameSpace += C({'InvolvesExternal': 1})

        for key, val in minedReplacements.items():
            mappings.append(dict(name=key.replace("\\percent", ""), instances=val))

        pathToProjectTCI = os.path.join(pathToPages, "tci" + str(tciCounter) + ".html")
        with open(pathToProjectTCI, 'a') as fh:
            fh.write(templateTCI.render(mappings=mappings, TypeChange=html.escape(k.before + " to " + k.after),
                                        hierarchy=typeChange_hierarchy[k] if k in typeChange_hierarchy.keys() else "-",
                                        primitiveInfo=typeChange_primitiveInfo[
                                            k] if k in typeChange_primitiveInfo.keys() else "-",
                                        namespace=typeChange_nameSpace[k] if k in typeChange_nameSpace.keys() else "-",
                                        noOfInst=len(v), noOfCommits=len(typeChanges_commit[k]),
                                        noOfProjects=str(typeChange_project[k])))
            fh.write('\n')
            fh.close()
        tciCounter += 1

        typeChangeSummary.append(
            dict(b4=html.escape(k.before), after=html.escape(k.after), tcisLink=pathToProjectTCI, noOfTCI=len(v),
                 noOfCommits=len(typeChanges_commit[k]),
                 noOfProjects=len(typeChange_project[k]),
                 hierarchy=typeChange_hierarchy[k] if k in typeChange_hierarchy.keys() else "-",
                 primitiveInfo=typeChange_primitiveInfo[
                     k] if k in typeChange_primitiveInfo.keys() else "-",
                 namespace=typeChange_nameSpace[k] if k in typeChange_nameSpace.keys() else "-"))

typeChangeSummary = sorted(typeChangeSummary, key=lambda i: (i['noOfTCI']), reverse=True)

pathToProjectCommits = os.path.join(pathToPages, "TypeChangeSummary.html")
with open(pathToProjectCommits, 'a') as fh:
    fh.write(TypeChangeSummarytemplate.render(typeChangeAnalysisList=typeChangeSummary))
    fh.write('\n')
    fh.close()