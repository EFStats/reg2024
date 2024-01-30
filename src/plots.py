import datetime
import pandas as pd
import sys
import matplotlib.pyplot as plt  # type: ignore
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
    partially = status_dict.get("partially_paid", 0)
    paid      = status_dict.get("paid", 0)
    return (new, approved, partially, paid)


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
    status_cols  = ["new", "approved", "partial", "paid"]
    sponsor_cols = ["normal", "sponsor", "supersponsor"]
    df           = split_tuplecol(df      = df,
                                  incol   = "Status",
                                  outcols = status_cols)
    df           = split_tuplecol(df      = df,
                                  incol   = "Sponsor",
                                  outcols = sponsor_cols)
    
    # Sanity checks: The three sponsorship categories must add up to the
    # total count, as well as the four reg status. Return, when passed.
    if not all(df.TotalCount == df[sponsor_cols].sum(axis=1)):
        sys.exit("read_parse_input: Consistency check failed.")
    if not all(df.TotalCount == df[status_cols].sum(axis=1)):
        sys.exit("read_parse_input: Consistency check failed.")
    return df


def doubleplot(df: pd.core.frame.DataFrame) -> None:
    s = 20
    fig, axes = plt.subplots(nrows = 1, ncols = 2, figsize = (15,7))

    #############
    # Left plot #
    #############

    # Plot itself
    ax = axes.flat[0]
    ax.plot(df.CurrentDateTimeUtc,
            df.new,
            c      = eflightergreen,
            lw     = 2,
            marker = "",
            label  = "New")
    ax.plot(df.CurrentDateTimeUtc,
            df.approved,
            c      = eflightgreen,
            lw     = 2,
            marker = "",
            label  = "Approved")
    ax.plot(df.CurrentDateTimeUtc,
            df.paid,
            c      = efgreen,
            lw     = 2,
            marker = "",
            label  = "Paid")
    
    # x axis
    ax.set_xlabel(xlabel   = "Time",
                  fontsize = s,
                  labelpad = 10)
    ax.set_xticks([datetime.date(2024, 1, 1),
                   datetime.date(2024, 2, 1),
                   datetime.date(2024, 3, 1),
                   datetime.date(2024, 4, 1),
                   datetime.date(2024, 5, 1),
                   datetime.date(2024, 6, 1),
                   datetime.date(2024, 7, 1),
                   datetime.date(2024, 8, 1),
                   datetime.date(2024, 9, 1)])
    ax.set_xticklabels(["Jan", "Feb", "Mar",
                        "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep"])
    ax.tick_params(axis      = "x",
                   which     = "both",
                   labelsize = s,
                   pad       = 10)
    ax.set_xlim([datetime.date(2024, 1, 1),
                 datetime.date(2024, 3, 1)]) # target: 18th Sept

    # y axis
    ax.set_ylabel(ylabel = "Count",
                  fontsize = s,
                  labelpad = 10)    
    ax.set_ylim((-5, 1000))
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
    
    # Legend
    ax.legend(loc      = 9,
              fontsize = 15,
              ncols    = 3,
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
    ax.set_xlim((0,1000))
 
    # y axis
    ax.set_ylabel(ylabel  = "")
    ax.set_ylim((-1.5, 1.5))
    ax.set_yticks([])
    
    # Legend
    ax.legend(loc      = 9,
              fontsize = 15,
              ncols    = 2,
              frameon  = False)


    # Annotations
    last     = str(df.CurrentDateTimeUtc.tolist()[-1]).split(".")[0]
 
    annot    = \
f'''Last update {last} (UTC).
For questions, contact @GermanCoyote.'''
    ax.annotate(text     = annot,
                xy       = (0.005, 0.005),
                xycoords = 'figure fraction',
                fontsize = s/3)

    new      = df.new.tolist()[-1]
    approved = df.approved.tolist()[-1]
    paid     = df.paid.tolist()[-1]
    total    = new + approved + paid
    annot    = \
f'''{total} total regs ({new} new, {approved} approved, {paid} paid).'''
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
    x = read_parse_input()
    doubleplot(x)
