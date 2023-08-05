import re
from ConnyUtils import IOUtil
from ConnyUtils import Common
import numpy as np
from matplotlib import pyplot as plt

# helper to determine how many of the passe strings start with a special char
from ConnyUtils.Common import splitListAtElement


# helper to calculate similarity
def getSimilarity(a, b, model, logging=True):
    s = 0.0
    try:
        s = model.similarity(a, b)
    except KeyError as err:
        print("Error", err, a, "<-->", b)
        pass
    if (logging):
        print(a, "<-->", b, " = ", s, " negative example: ")
    return s, a, b


def evalSynonymsV2(fastTextModel, skill_synonyms_file_name=None):
    if skill_synonyms_file_name == None:
        raw_synonyms = IOUtil.readToArrayFromPackage('skill_relations.txt')  # load from file
    else:
        raw_synonyms = IOUtil.readToArray(skill_synonyms_file_name, encoding=None)

    synonymes = Common.LamdaList(raw_synonyms) \
        .map(lambda s: s.decode('utf-8')) \
        .map(lambda s: re.sub(r" +", ' ', s)) \
        .map(lambda s: s.split(" ")).result()

    results_synonymes = []
    results_no_synonymes = []
    results_synonymes_full = []
    results_no_synonymes_full = []
    # iterate over all synonyme lines
    for synonymArray in synonymes:
        # build n x n synonym matrix
        real_synonymes, negative_examples = splitListAtElement("-not-", synonymArray)
        for synx in real_synonymes:
            for negative_example in negative_examples:
                s, a, b = getSimilarity(synx, negative_example, fastTextModel, logging=False)
                results_no_synonymes_full.append(str(s) + " " + a + " - " + b + "(negative)")
                results_no_synonymes.append(s)
            for syny in real_synonymes:
                s, a, b = getSimilarity(synx, syny, fastTextModel, logging=False)
                results_synonymes_full.append(str(s) + " " + a + " - " + b)
                results_synonymes.append(s)
    print("--->  mean synonyms", np.mean(results_synonymes), "mean non-synonyms", np.mean(results_no_synonymes))
    print("Top 5 worst synonyms\n", np.sort(results_synonymes_full, axis=0)[:5])
    print("Top 5 worst non-synonyms\n", np.sort(results_no_synonymes_full, axis=0)[-5:])
    return [
        [results_synonymes, np.mean(results_synonymes), results_synonymes_full],
        [results_no_synonymes, np.mean(results_no_synonymes), results_no_synonymes_full]
    ]


# FastTextModel expected
def evalRelationsV2(fastTextModel, skill_relations_file=None):
    if skill_relations_file == None:
        raw_relations = IOUtil.readToArrayFromPackage('skill_relations.txt')  # load from file
    else:
        raw_relations = IOUtil.readToArray(skill_relations_file, encoding=None)
    # or for a file-like stream:
    _relations = Common.LamdaList(raw_relations) \
        .map(lambda s: s.decode('utf-8')) \
        .map(lambda s: s.split(" ")).result()
    # reshape array to dict with key as target_relation and value as source_relations array.
    _relations = [(x[0], x[1:]) for x in _relations]

    relations = []
    no_relations = []
    results = []

    # iterate to get relating pairs
    last_target_relation = _relations[-1][0]
    for target_relation, source_relations in _relations:
        for source_relation in source_relations:
            relations.append({"target_relation": target_relation, "source_relation": source_relation})
            assert target_relation != last_target_relation
            no_relations.append({"target_relation": last_target_relation, "source_relation": source_relation})
        last_target_relation = target_relation

    relations_result = [
        getSimilarity(syn.get("target_relation"), syn.get("source_relation"),
                      fastTextModel, logging=True
                      )[0] for syn in relations]
    no_relations_result = [
        getSimilarity(syn.get("target_relation"), syn.get("source_relation"),
                      fastTextModel, logging=True
                      )[0] for syn in no_relations]

    # return {"relations_result_mean": np.mean(relations_result), "relations_result": relations_result,
    #         "no_relations_result_mean": np.mean(no_relations_result), "no_relations_result": no_relations_result}

    return [
        [relations_result, np.mean(relations_result)],
        [no_relations_result, np.mean(no_relations_result)]
    ]

# public usage ready
def evalRelationsV2AndPlot(fastTextModel):
    evalResult = evalRelationsV2(fastTextModel)
    plotEvalResult([evalResult[0][0], evalResult[1][0]],
                   ["relations result", "no relations result"],
                   title="Evaluation Relations Result"
                   )

# public usage ready
def evalSynonymsV2AndPlot(fastTextModel):
    evalResult = evalSynonymsV2(fastTextModel)
    plotEvalResult([evalResult[0][0], evalResult[1][0]],
                   ["synonyms result", "no synonyms result"],
                   title="Evaluation Synonyms Result"
                   )

# public usage ready
def plotEvalResult(values2D, labels, linestyle='o', title='Evaluation Results'):
    assert len(values2D) == len(labels), "values and labels should have same length. "
    # evenly sampled time at 200ms intervals
    for y_values, label in zip(values2D, labels):
        x = np.arange(0, len(y_values), 1)
        plt.plot(x, y_values, linestyle, label=label)

    plt.xlabel('nth test')
    plt.ylabel('Accuracy')
    plt.title(title)
    plt.legend(loc=1, borderaxespad=0.2)
    plt.show()


def _testPlotEvalResult():
    print("testing")
    values = [[2, 3, 4, 3, 4, 3, 4], [8, 7, 6, 7, 8, 7, 8]]
    labels = ["eins", "zwei"]
    plotEvalResult(values, labels)


def _loadTestModel():
    from gensim.models.wrappers import FastText
    pathToModelFolder = "D:/data/fasttest-docker/data/"
    absPath = pathToModelFolder + "fastText-0.1.0/result/fil9.bin"
    return FastText.load_fasttext_format(absPath)


def _testevalV2AndPlot():
    print("Loading test model...")
    test_model = _loadTestModel()
    print("Test model loaded.")
    evalSynonymsV2AndPlot(test_model)
    evalRelationsV2AndPlot(test_model)


if __name__ == "__main__": _testevalV2AndPlot()


# ---------------------------------------------------------------------------------
# ------------------------------old stuff----------------------------------
# ---------------------------------------------------------------------------------


# FastTextModel expected
def evalRelations(fastTextModel):
    # Load relations
    import pkg_resources
    resource_package = __name__  # Could be any module/package name
    resource_path = '/'.join(('packageData', 'skill_relations.txt'))  # Do not use os.path.join(), see below

    raw_relations = pkg_resources.resource_string(resource_package, resource_path).splitlines()
    # or for a file-like stream:
    _relations = Common.LamdaList(raw_relations) \
        .map(lambda s: s.decode('utf-8')) \
        .map(
        lambda s: s.split(" ")).result()
    # reshape array to dict with key as target_relation and value as source_relations array.
    relations = dict([(x[0], x[1:]) for x in _relations])

    results = []
    # iterate to get relating pairs
    for target_relation, source_relations in relations.items():
        for source_relation in source_relations:
            s, a, b = getSimilarity(target_relation, source_relation, fastTextModel, logging=True)
            results.append(s)
    return {"mean_result": np.mean(results), "results": results}


# FastTextModel expected
def evalSynonymes(fastTextModel):
    import pkg_resources
    resource_package = __name__  # Could be any module/package name
    resource_path = '/'.join(('packageData', 'skill_synonyms.txt'))  # Do not use os.path.join(), see below

    raw_synonyms = pkg_resources.resource_string(resource_package, resource_path).splitlines()
    # load from file
    synonymes = Common.LamdaList(raw_synonyms) \
        .map(lambda s: s.decode('utf-8')) \
        .map(lambda s: re.sub(r" +", ' ', s)) \
        .map(lambda s: s.split(" ")).result()

    results_synonymes = []
    results_synonymes_full = []
    # iterate over all synonyme lines
    for synonymArray in synonymes:
        # build n x n synonym matrix
        for synx in synonymArray:
            for syny in synonymArray:
                s, a, b = getSimilarity(synx, syny, fastTextModel, logging=False)
                results_synonymes_full.append(str(s) + " " + a + " - " + b)
                results_synonymes.append(s)
    print("--->  mean_result", np.mean(results_synonymes))
    print("Top 5 worst\n", np.sort(results_synonymes_full, axis=0)[:5])
    return {"mean_result": np.mean(results_synonymes), "results_synonymes_full": results_synonymes_full}
