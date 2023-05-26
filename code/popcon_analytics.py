#!/usr/bin/env python

import requests
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.signal import resample

custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="white", rc=custom_params)

start_date = '2016-03-03'
end_date = '2023-05-25'
query_url_datalad = \
    f'https://qa.debian.org/cgi-bin/popcon-data?packages=datalad+python3-datalad;from_date={start_date};to_date={end_date}'
query_url_total_submissions = \
    f'https://qa.debian.org/cgi-bin/popcon-data?packages=popularity-contest&from_date={start_date}&to_date={end_date}'


def plot_downloads(outpath):
    """Plot Debian popularity contest data for DataLad"""
    # get installation data from datalad, and from the popcon package as a baseline
    data = requests.get(query_url_datalad)
    submitter = requests.get(query_url_total_submissions)
    assert data.status_code == 200 and submitter.status_code == 200

    # read the data into dataframes
    df = pd.DataFrame.from_dict({(i, j): data.json()[i][j]
                                 for i in data.json().keys()
                                 for j in data.json()[i].keys()},
                                orient='index').sort_index()
    submitter_df = pd.DataFrame.from_dict({(i, j): submitter.json()[i][j]
                                 for i in submitter.json().keys()
                                 for j in submitter.json()[i].keys()},
                                 orient='index').sort_index()

    # resample the total number of submitting users to match the number of data
    # points in DataLad installation data
    submitters = resample(
        submitter_df[['no_files', 'old', 'vote', 'recent']].values.sum(axis=1),
        len(df)
    )
    # calculate popularity as percent of installations of all submitters
    df['installations (% of users)'] = df[['no_files', 'old', 'vote', 'recent']].values.sum(axis=1) / submitters * 100

    # drop unused columns
    df = df.drop(columns=['no_files', 'old', 'vote', 'recent'])
    # resolve the multiIndex
    df = df.reset_index(names=['software', 'Date'])
    # combine debian and python package:
    df = df.groupby('Date').sum(numeric_only=True)
    # plot
    fig = sns.lineplot(data=df, y='installations (% of users)', x='Date')
    tiks = fig.axes.get_xticklabels()[::200]
    plt.setp(fig.axes.get_xticklabels(), visible=False)
    plt.setp(tiks, visible=True)
    plt.xticks(rotation=30)
    plt.title('DataLad package downloads from Debian users over time')
    # add a line when handbook was first released
    plt.axvline(x=1187, label="First Handbook commit", color='orange',
                linestyle='dotted')
    plt.axvline(x=1396, label="First Handbook release", color='red',
                linestyle='dotted')
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath)


if __name__ == '__main__':
    # poor man's argparse
    try:
        outpath = sys.argv[1]
    except IndexError as e:
        print("Provide to graphics directory to save the figure as an argument,"
              " or as interactive input below , e.g., 'graphics/popcon.png'")
        outpath = input("Path to the file: ")
    plot_downloads(outpath)
