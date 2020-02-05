import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import statistics





def violin(map):
    sns.set(font_scale=0.80)
    fig, axes = plt.subplots(figsize=(8, 3))
    if len(map) > 6:
        map = dict(sorted(map.items(), key=lambda item: statistics.median(item[1]), reverse=True)[:6])
    r = axes.violinplot(dataset=list(map.values()), showmeans=True, showmedians=True)
    r['cmeans'].set_color('r')
    r['cmedians'].set_color('g')
    labels = list(map.keys())
    axes.set_xticks(np.arange(1, len(labels) + 1))
    axes.set_xticklabels(labels)
    axes.set_xlabel('Visibility', fontweight='bold')
    axes.set_ylabel('Ratio', fontweight='bold')
    plt.show()

