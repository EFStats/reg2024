
def plot_statuses(df: pd.core.frame.DataFrame) -> None:
    s = 20
    
    fig, ax = plt.subplots(figsize=(7,7))
    ax.plot(df.CurrentDateTimeUtc,
            df.paid,
            c      = efgreen,
            lw     = 2,
            marker = "",
            label  = "Paid")
    ax.plot(df.CurrentDateTimeUtc,
            df.approved,
            c     = eflightgreen,
            lw    = 2,
            marker = "",
            label = "Approved")
    ax.plot(df.CurrentDateTimeUtc,
            df.new,
            c     = eflightergreen,
            lw    = 2,
            marker = "",
            label = "New")
    
    # x axis
    ax.set_xlabel(xlabel   = "Time",
                  fontsize = s,
                  labelpad = 10)
    ax.set_xlim([datetime.date(2024, 1, 1),
                 datetime.date(2024, 9, 18)])
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
                   labelsize = s)

    # y axis
    ax.set_ylabel(ylabel = "Count",
                  fontsize = s,
                  labelpad = 10)    
    ax.set_ylim((-5, 10000))
    ax.hlines(y      = [1000 * i for i in range(50)],
              xmin   = datetime.date(2024, 1, 1),
              xmax   = datetime.date(2024, 9, 18),
              colors = "lightgrey",
              ls     = "-",
              lw     = 0.5)
    ax.tick_params(axis      = "y",
                   which     = "both",
                   labelsize = s)
    
    # Legend
    ax.legend(loc      = 9,
              fontsize = 15,
              ncols    = 3,
              frameon  = False)
    
    # Annotations
    last     = str(df.CurrentDateTimeUtc.tolist()[-1]).split(".")[0]
    new      = df.new.tolist()[-1]
    approved = df.approved.tolist()[-1]
    paid     = df.paid.tolist()[-1]
    total    = new + approved + paid
    annot    = \
f'''Last update {last} (UTC).
{total} total regs ({new} new, {approved} approved, {paid} paid).
For questions, contact @GermanCoyote.'''
    ax.annotate(text     = annot,
                xy       = (0.005, 0.005),
                xycoords = 'figure fraction',
                fontsize = s/3)

    # Export
    plt.savefig(fname       = "../out/Fig1.svg",
                bbox_inches = "tight")


def plot_breakdown(df: pd.core.frame.DataFrame) -> None:
    nb_normal = df.iloc[-1,:].normal
    nb_spons  = df.iloc[-1,:].sponsor
    nb_super  = df.iloc[-1,:].supersponsor
    
    s = 20
    fig, ax = plt.subplots(figsize=(7,7))
    
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
    ax.set_xlabel(xlabel   = "Nb. Regs",
                  fontsize = s,
                  labelpad = 10)
    ax.tick_params(axis      = "x",
                   which     = "both",
                   labelsize = s)
    ax.set_xlim((0,10000))
 
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
    new      = df.new.tolist()[-1]
    approved = df.approved.tolist()[-1]
    paid     = df.paid.tolist()[-1]
    total    = new + approved + paid
    annot    = \
f'''Last update {last} (UTC).
{total} total regs ({nb_normal} normal, {nb_spons} sponsors, {nb_super} supersp).
For questions, contact @GermanCoyote.'''
    ax.annotate(text     = annot,
                xy       = (0.005, 0.005),
                xycoords = 'figure fraction',
                fontsize = s/3)
    # Export
    plt.savefig(fname       = "../out/Fig2.svg",
                bbox_inches = "tight")
