import datetime
import pandas as pd
import sys
import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from typing import List

# CI
efgreen         = "#005953"
eflightgreen    = "#69a3a2"
eflightergreen  = "#a2c5c4"
eflightestgreen = "#e6efee"


def parse_status_dict(status_dict: dict) -> tuple[int, int, int, int]:
    ''' Parse a single registration status dictionary.
    Missing values will be set to zero. '''

    new       = status_dict.get("new", 0)
    approved  = status_dict.get("approved", 0)
    partially = status_dict.get("partially paid", 0)
    paid      = status_dict.get("paid", 0)
    checkedin = status_dict.get("checked in", 0)
    return (new, approved, partially, paid, checkedin)


def parse_sponsor_dict(sponsor_dict: dict) -> tuple[int, int, int]:
    ''' Parse a single sponsor status dictionary.
    Missing values will be set to zero. '''

    normal       = sponsor_dict.get("normal", 0)
    sponsor      = sponsor_dict.get("sponsor", 0)
    supersponsor = sponsor_dict.get("supersponsor", 0)
    return (normal, sponsor, supersponsor)


def split_tuplecol(df: pd.core.frame.DataFrame,
                   incol: str,
                   outcols: List[str]) -> pd.core.frame.DataFrame:
    ''' Given a column of tuples, make a set of new columns,
        containing the tuple elements. Drop input column. '''

    # Sanity check: Make sure every element of the input column contains
    # an iterable with as many elements as we have output columns.
    if not all(df[incol].apply(len) == len(outcols)):
        sys.exit(f"split.tuplecol: Malformed entry in column {incol}.")
    
    for i, outcol in enumerate(outcols):
        df[outcol] = [x[i] for x in df[incol]]

    df.drop(columns = [incol], inplace = True)
    return df


def read_parse_input(filename: str = "./data/log.txt") -> pd.core.frame.DataFrame:
    # For now, we only need the time stamp, the total count (for sanity
    # checks), the reg status and the sponsor category column.
    try:
        df = pd.read_json(filename, lines = True)
    except ValueError as e:
        sys.exit(f"read_parse_input: Error while loading source data: {e}")
    df = df.loc[:, ["CurrentDateTimeUtc", "TotalCount", "Status", "Sponsor"]]
    
    # Parse timestamp column via direct conversion
    df.CurrentDateTimeUtc = pd.to_datetime(df.CurrentDateTimeUtc)
    
    # Parse 'Status' and 'Sponsor' column from dicts to tuples.
    df.Status  = df.Status.apply(parse_status_dict)
    df.Sponsor = df.Sponsor.apply(parse_sponsor_dict)
    
    # Turn the two tuple columns into sets of individual columns.
    status_cols  = ["new", "approved", "partial", "paid", "checkedin"]
    sponsor_cols = ["normal", "sponsor", "supersponsor"]
    df           = split_tuplecol(df      = df,
                                  incol   = "Status",
                                  outcols = status_cols)
    df           = split_tuplecol(df      = df,
                                  incol   = "Sponsor",
                                  outcols = sponsor_cols)
    
    return df


def read_old_dashboard(filename: str = "./data/dashboard_per_28082023.csv") -> pd.core.frame.DataFrame:
    df_23 = pd.read_csv(filename)
    df_23.columns = ["idx", "date", "total", "unapproved", "approved", "partially_paid", "paid"]
    df_23.date = [x[:10] for x in df_23.date]
    df_23.date = pd.to_datetime(df_23.date) + pd.DateOffset(1)
    df_23.idx -= 4
    return df_23
    

def daywise(df: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    ''' Calculate day-wise count'''

    # Working copy
    out          = df.copy()

    # Get last count for every day
    out["Date"]  = pd.to_datetime(df['CurrentDateTimeUtc']).dt.strftime('%m/%d/%Y')
    out          = out.groupby("Date").agg("last").reset_index()
    out          = out.loc[:, ["Date", "TotalCount"]]
    
    # Add day index, shifted by offset of three,
    # s.t. day 0 is the day of reg opening
    out["idx"] = np.arange(0, len(out)) - 3

    return out


def tripleplot(df: pd.core.frame.DataFrame,
               df_last_daywise: pd.core.frame.DataFrame) -> None:
        
    # Prepare figure
    s = 20
    fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize = (15,15))
    plt.subplots_adjust(hspace = .3, wspace=.3)
    #axes.flat[3].set_visible(False)

    #############
    # Left plot #
    #############

    ax           = axes.flat[0]
    df["totals"] = df.new + df.approved + df.partial + df.paid + df.checkedin
    
    ax.plot(df.CurrentDateTimeUtc,
            df.checkedin,
            c      = efgreen,
            lw     = 2,
            marker = "",
            label  = "Checked in")
    ax.plot(df.CurrentDateTimeUtc,
            df.totals,
            c      = eflightgreen,
            lw     = 2,
            marker = "",
            label  = "Total")
    ax.plot(df.CurrentDateTimeUtc,
            df.paid + df.partial + df.checkedin,
            c      = eflightergreen,
            lw     = 2,
            marker = "",
            label  = "Paid (incl. partial)")

    # x axis
    ax.set_xlabel(xlabel   = "Time",
                  fontsize = s,
                  labelpad = 10)
    
    ax.set_xticks([datetime.date(2024, 2, 1),
                  datetime.date(2024, 3, 1),
                  datetime.date(2024, 4, 1),
                  datetime.date(2024, 5, 1),
                  datetime.date(2024, 6, 1),
                  datetime.date(2024, 7, 1),
                  datetime.date(2024, 8, 1),
                  datetime.date(2024, 9, 1)])
    ax.set_xticklabels(["Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"])

    ax.tick_params(axis      = "x",
                   which     = "both",
                   labelsize = s,
                   pad       = 10)
    
    ax.set_xlim([datetime.date(2024, 1, 25),
                 datetime.date(2024, 9, 25)]) # target: 18th Sept (2024, 9, 18)

    # y axis
    ax.set_ylabel(ylabel = "Count",
                  fontsize = s,
                  labelpad = 10)
    ax.set_yticks([0, 1000, 2000, 3000, 4000, 5000, 6000])
    ax.hlines(y      = [1000 * i for i in range(50)],
              xmin   = datetime.date(2024, 1, 1),
              xmax   = datetime.date(2024, 9, 18),
              colors = "lightgrey",
              ls     = "-",
              lw     = 0.5)
    ax.tick_params(axis      = "y",
                   which     = "both",
                   labelsize = s,
                   pad       = 10)
    ax.set_ylim((0, 6000))
    
    # Legend
    ax.legend(loc      = 9,
              fontsize = 15,
              ncols    = 2,
              frameon  = False)
    

    ##############
    # Right plot #
    ##############

    ax = axes.flat[1]
    nb_normal = df.iloc[-1,:].normal
    nb_spons  = df.iloc[-1,:].sponsor
    nb_super  = df.iloc[-1,:].supersponsor
    
    ax.barh(y     = 0,
            width = nb_normal,
            color = eflightergreen,
            label = "Normal")
    ax.barh(y     = 0,
            width = nb_spons,
            left  = nb_normal,
            color = eflightgreen,
            label = "Sponsor")
    ax.barh(y     = 0,
            width = nb_super,
            left  = nb_normal + nb_spons,
            color = efgreen,
            label = "Supersponsor")
    
    
    # x axis
    ax.set_xlabel(xlabel   = "Count",
                  fontsize = s,
                  labelpad = 10)
    ax.tick_params(axis      = "x",
                   which     = "both",
                   labelsize = s,
                   pad       = 10)
    ax.set_xlim((0,6000))
 
    # y axis
    ax.set_ylabel(ylabel  = "")
    ax.set_ylim((-1.5, 1.5))
    ax.set_yticks([])
    
    # Legend
    ax.legend(loc      = 9,
              fontsize = 15,
              ncols    = 2,
              frameon  = False)
    
    
    ####################
    # Bottom-left plot #
    ####################
        
    # We need daywise data for the bottom-left plot.
    # This year, the data from the last con (2023) is only
    # availably on a daywise basis, so we don't need to
    # preprocess those.
    df_daywise = daywise(df)
    
    ax = axes.flat[2]
    ax.plot(df_daywise.idx,
            df_daywise.TotalCount,
            lw     = 2,
            c      = efgreen,
            label  = "2024",
            zorder = 100)
    ax.plot(df_last_daywise.idx,
            df_last_daywise.total,
            lw    = 2,
            c     = eflightgreen,
            label = "2023")
    ax.vlines([230], 0, 10000, color = "grey", ls=":", label = "EF 2024 Begins")

    
    # x axis
    ax.set_xlabel(xlabel   = "Day After Reg Opening",
                  fontsize = s,
                  labelpad = 10)
    ax.tick_params(axis      = "x",
                   which     = "both",
                   labelsize = s,
                   pad       = 10)
    ax.set_xlim((-5, 250))
 
    # y axis
    ax.set_ylabel(ylabel  = "Total Regs",
                 fontsize = s,
                 labelpad = 10)
    ax.tick_params(axis      = "y",
                   which     = "both",
                   labelsize = s,
                   pad       = 10)
    ax.set_ylim((0, 6000))
    
    # Legend
    ax.legend(loc      = 2,
              fontsize = 15,
              ncols    = 1,
              frameon  = False)

    #####################
    # Bottom-right plot #
    #####################

    ax           = axes.flat[3]
    
    ax.plot(df.CurrentDateTimeUtc,
            df.checkedin,
            c      = efgreen,
            lw     = 2,
            marker = "",
            label  = "Checked in")

    # x axis
    ax.set_xlabel(xlabel   = "Date",
                  fontsize = s,
                  labelpad = 10)
    
    ax.set_xticks([datetime.date(2024, 9, 17),
                  datetime.date(2024, 9, 18),
                  datetime.date(2024, 9, 19),
                  datetime.date(2024, 9, 20),
                  datetime.date(2024, 9, 21)])
    ax.set_xticklabels(["17th", "18th", "19th", "20th", "21st"])

    ax.tick_params(axis      = "x",
                   which     = "both",
                   labelsize = s,
                   pad       = 10)
    
    ax.set_xlim([datetime.date(2024, 9, 16),
                 datetime.date(2024, 9, 22)]) # target: 18th Sept (2024, 9, 18)

    # y axis
    ax.set_ylabel(ylabel = "Checked In",
                  fontsize = s,
                  labelpad = 10)
    ax.set_yticks([0, 1000, 2000, 3000, 4000, 5000, 6000])
    ax.hlines(y      = [1000 * i for i in range(50)],
              xmin   = datetime.date(2024, 9, 16),
              xmax   = datetime.date(2024, 9, 22),
              colors = "lightgrey",
              ls     = "-",
              lw     = 0.5)
    ax.tick_params(axis      = "y",
                   which     = "both",
                   labelsize = s,
                   pad       = 10)
    ax.set_ylim((0, 6000))
                   

    
    ###############
    # Annotations #
    ###############
    
    last     = str(df.CurrentDateTimeUtc.tolist()[-1]).split(".")[0]
 
    annot    = \
f'''Last update {last} (UTC).
For questions, contact @GermanCoyote.'''
    ax.annotate(text     = annot,
                xy       = (0.005, 0.005),
                xycoords = 'figure fraction',
                fontsize = s/3)

    new       = df.new.tolist()[-1]
    approved  = df.approved.tolist()[-1]
    partial   = df.partial.tolist()[-1]
    paid      = df.paid.tolist()[-1]
    checkedin = df.checkedin.tolist()[-1]
    total     = new + approved + partial + paid + checkedin
    annot     = \
f'''{total} total regs ({partial + paid + checkedin} paid, out of which {checkedin} checked in).'''
    axes.flat[0].annotate(text     = annot,
                          xy       = (0.005, 0.005),
                          xycoords = 'axes fraction',
                          fontsize = s/3)


    total    = nb_normal + nb_spons + nb_super
    annot    = \
f'''{total} total regs ({nb_normal} normal, {nb_spons} sponsors, {nb_super} supersponsors).'''
    axes.flat[1].annotate(text     = annot,
                          xy       = (0.005, 0.005),
                          xycoords = 'axes fraction',
                          fontsize = s/3)



    # Export
    plt.savefig(fname       = "./out/Fig1.svg",
                bbox_inches = "tight")


if __name__ == "__main__":
    # This year's data, from our own logger
    ef2024         = read_parse_input()
    
    # Last year's data is only available on a daily basis,
    # which is why we have two different read-functions.
    # This is a bit inelegant, but starting next year,
    # all logs will be in the same format, and the code
    # will become less cluttered.
    ef2023_daywise = read_old_dashboard()
    
    tripleplot(ef2024, ef2023_daywise)
