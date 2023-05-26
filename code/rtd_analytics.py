#!/usr/bin/env python

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys

custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="white", rc=custom_params)


def plot_monthly_views(data, outpath):
    """Plot average monthly documentation views side-by-side."""
    df = pd.read_csv(data)
    # melt from wide to long
    rtd = pd.melt(df, id_vars=['Date'],
                  value_vars=['handbook.datalad.org', 'docs.datalad.org'],
                  value_name='Views per month', var_name='Documentation source')
    fig = sns.lineplot(data=rtd, y='Views per month', x='Date',
                       hue='Documentation source')
    tiks = fig.axes.get_xticklabels()[::3]
    plt.setp(fig.axes.get_xticklabels(), visible=False)
    plt.setp(tiks, visible=True)
    plt.xticks(rotation=30)
    plt.title('Average documentation page views')
    plt.tight_layout()
    plt.savefig(outpath)


def main():
    # poor man's argparse
    try:
        data = sys.argv[1]
    except IndexError as e:
        print("Provide path to RTD data csv file as an argument to the script, "
              "or as interactive input below , e.g., 'data/rtd_analytics.csv'")
        data = input("Path to the file: ")
    try:
        outpath = sys.argv[2]
    except IndexError as e:
        print("Provide to graphics directory to save the figure as an argument,"
              " or as interactive input below , e.g., 'graphics/rtd.png'")
        outpath = input("Path to the file: ")
    plot_monthly_views(data, outpath)


if __name__ == '__main__':
    main()
