import time as tm
from datetime import date
import os
from pathlib import Path
import pandas as pd

from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool, BoxSelectTool, DataTable, TableColumn, CDSView, IndexFilter, DateFormatter, DatetimeTickFormatter, NumeralTickFormatter, CustomJS, Panel, Tabs, LinearAxis, Range1d, Paragraph, DatePicker, Div, BoxAnnotation
from bokeh.layouts import gridplot, column, row
from bokeh.io import output_notebook, curdoc
output_notebook()

#TODO - ADD THE REST OF UNITS
units = {
    "time": "Time (yyyy-MM-dd hh:mm:ss)",
    "alt": "Altitude (Meters)",
    "temp": "Temp (Celsius)",
    "windspeed": "Wind Speed (m/s)",
    "rh": "Rel. Hum. (%)",
    "baro": "Baro. (mb)",
    "magdir": "Mag. Dir. (Degrees)",
}


def field_test_information(
    fieldTestLabel,
    fieldTestLocation,
    fieldTestDate,
    fieldTestDescription,
    fieldTestTeam,
    dataAnalyst,
    deviceName,
    deviceNickName,
    trimmedDataFolderName,
    preprocessedDataFolderName
):

    #Information to indicate the history of changes made
    change_history = []

    #Convert fieldTestDate to a datetime object for easy manipulations
    try:
        fieldTestDate = date.fromisoformat(fieldTestDate)
        fieldTestDate = fieldTestDate.strftime("%A, %B %d, %Y")
    except ValueError as e:
        print(e)
    except Exception as e:
        print("Something went wrong. Restart the notebook")

    #Field test parameters into a dictionary
    fieldTestParameters = {
        "Field Test Label": fieldTestLabel,
        "Field Test Location": fieldTestLocation,
        "Field Test Date": fieldTestDate,
        "Field Test Description": fieldTestDescription,
        "Field Test Team": fieldTestTeam,
        "Data Analyst": dataAnalyst,
        "Device Name": deviceName,
        "Device Nickname": deviceNickName
    }

    #Echo field test parameters for user to confirm and change if necessary
    print("PLEASE CONFIRM THE FOLLOWING FIELD TEST PARAMETERS")
    print("-"*50)

    for parameter in fieldTestParameters:
        print(f"{parameter}: {fieldTestParameters[parameter]}")
        change_history.append(f"{parameter}: {fieldTestParameters[parameter]}")
        
    print("-"*50)

    #Get the directory that the notebook is currently in
    cwd = os.getcwd()

    #Create trimmed data directory
    try:
        trimmed_data_dir = Path(trimmedDataFolderName)
        trimmed_data_dir.mkdir()
        change_history.append(f"{trimmedDataFolderName} folder was created in {cwd}")
    except FileExistsError:
        print(f"The folder, {trimmedDataFolderName}, already exists")
    except Exception as e:
        print("Something went wrong. Restart the notebook")
    else:
        print(f"{trimmedDataFolderName} has been created in {cwd}")

    #Create preprocessed data directory
    try:
        preprocessed_data_dir = Path(preprocessedDataFolderName)
        preprocessed_data_dir.mkdir()
        change_history.append(f"{preprocessedDataFolderName} folder was created in {cwd}")
    except FileExistsError:
        print(f"The folder, {preprocessedDataFolderName}, already exists")
        print("Proceed to STEP 1")
    except Exception as e:
        print("Something went wrong. Restart the notebook")
    else:
        print(f"{preprocessedDataFolderName} has been created in {cwd}")
        print("Proceed to STEP 1")

    return fieldTestParameters, change_history

def open_file(filename):
    cwd = os.getcwd()

    delay_time = 0.1
    print(f"Locating \"{filename}\"", end="")

    for i in range(2):
        tm.sleep(delay_time)
        print(".", end="")
    tm.sleep(delay_time)
    print(".")
    tm.sleep(delay_time)

    if filename not in os.listdir():
        print(f"\"{filename}\" does not exist in the current directory: {cwd}")
        print(f"\nDid you type in the name correctly?")
        print(f"Did you move the file to the wrong directory?")
    else:
        print(f"\n\"{filename}\" has been located")

    #Variables to prevent cells from accidentally being run again, and potentially messing up the workflow
        timedeltas_read = False

        #Check if there's anything wrong with the file in the first place
        try:
            print(f"Opening \"{filename}\"", end="")
            
            for i in range(2):
                tm.sleep(delay_time)
                print(".", end="")
            tm.sleep(delay_time)
            print(".")
            tm.sleep(delay_time)
            
            f = open(filename, "r")
            print("File opened successfully")

        except Exception as e:
            print("Something went wrong")
            print(e)
            
        else:
            #READ PROLOGUE   
            try:
                #Iterate over prologue
                print("\nReading prologue")
                print("-"*50)
                pl = 0
                prologue = []

                while True:
                    l = f.readline()
                    prologue.append(l)
                    print(l)
                    tm.sleep(delay_time)
                    if l == "\n":
                        break
                    else:
                        pl += 1
                print("-"*50)        
                print("Prologue read successfully")

                print(f"Prologue is {pl} lines long")

            except Exception as e:
                print("Something went wrong")
                print(e)
                print("Try rerunning STEP 2")

            #READ HEADERS, UNITS, AND DATA
            try:
                #Obtaining headers and units
                print("\nObtaining headers")
                tm.sleep(delay_time)
                headers = f.readline().split(",")
                headers.pop(-1)
                print("Headers obtained successfully")
                tm.sleep(delay_time)

                print("\nObtaining units")
                tm.sleep(delay_time)
                units = f.readline().split(",")
                units.pop(-1)
                print("Units obtained successfully")
                tm.sleep(delay_time)

                #Combine the headers and units into one row
                columns = []
                for i in range(len(headers)):
                    columns.append(headers[i] + " (" + units[i] + ")")

                #Store the data values into a pandas dataframe
                print("\nObtaining measurements")
                tm.sleep(delay_time)        
                df = pd.read_csv(f, names=columns)
                df_rows = df.shape[0]
                print("Data obtained successfully")
                tm.sleep(delay_time)
                f.close()
                print(f"\n{df_rows} rows in file")
                print("\nReview data and proceed to STEP 3")

            except Exception as e:
                print("Something went wrong")
                print(e)

    return df, prologue, columns, headers, units, timedeltas_read

def error_check(df):
    #LOOK FOR ANY CORRUPT FIELDS, NAN, ETC
    #ERROR CHECKING ON UNITS 
    indices = []
    invalidcols = []
    nullcols = []

    asterisks_bool = False
    nulls_bool = False

    #Find columns with *** entries
    asterisks = df.isin(["***"])
    for col in asterisks.columns:
        if asterisks[col].values.any():
            invalidcols.append(col)

    if len(invalidcols) != 0:
        asterisks_bool = True
        
    #Find columns with NaN values
    nulls = df.isnull()
    for col in nulls.columns:
        if nulls[col].values.any():
            nullcols.append(col)

    if len(nullcols) != 0:
        nulls_bool = True

    #Find the specific rows in the entire dataframe
    if asterisks_bool and nulls_bool:
        for i in range(len(df)):
            invalid = df.iloc[i]
            if invalid.hasnans: 
                indices.append(i)
            if ("***" in invalid.values): #reference https://stackoverflow.com/questions/30944577/check-if-string-is-in-a-pandas-dataframe
                indices.append(i)
    elif asterisks_bool:
        for i in range(len(df)):
            invalid = df.iloc[i]
            if ("***" in invalid.values): #reference https://stackoverflow.com/questions/30944577/check-if-string-is-in-a-pandas-dataframe
                indices.append(i)
    elif nulls_bool:
        for i in range(len(df)):
            invalid = df.iloc[i]
            if invalid.hasnans: 
                indices.append(i)

    indices = set(indices) #Use a set to ignore duplicates

    if len(indices) == 0:
        print("No errors have been detected")
        print("Proceed to STEP 3")

    if asterisks_bool and nulls_bool:
        print("*** entries have been detected in the following columns")
        print(*invalidcols, sep="\n")
        print("NaN entries have been detected in the following columns")
        print(*nullcols, sep = "\n")
        print("\nProceed to STEP 2A to identify them and STEP 2B for any further action")

    elif asterisks_bool:
        print("*** entries have been detected in the following columns")
        print(*invalidcols, sep="\n")
        print("\nProceed to STEP 2A to identify them and STEP 2B for any further action")
        
    elif nulls_bool:
        print("NaN entries have been detected in the following columns")
        print(*nullcols, sep = "\n")
        print("\nProceed to STEP 2A to identify them and STEP 2B for any further action")
        
    #check nlls reference https://www.geeksforgeeks.org/check-for-nan-in-pandas-dataframe/

    return asterisks, indices, invalidcols, nullcols

def calculate_timedeltas(df, columns, timedeltas_read, change_history):
    if not timedeltas_read:
        #Date column as string variable
        date = columns[0]

        try:
            #Also here if the error checking steps were skipped
            if df[date].dtype != "<M8[ns]":
                df[date] = pd.to_datetime(df[date])         
                change_history.append(f"The \"{date}\" column was converted to type datetime\n")
                print(f"The \"{date}\" column was converted to type datetime\n")

            #List to store deltas
            deltas = []

            #Total number of data entry rows
            rows = len(df)

            #Calculate all time deltas and store in list
            i = 0
            while i != (rows-1):
                time1 = df.loc[i,date]
                time2 = df.loc[i+1,date]
                delta = time2 - time1
                deltas.append(delta)
                i+=1
            deltas.append("LAST TIME ENTRY") #Helper text

            #Convert list to series
            deltas = pd.Series(deltas, name="Time Delta")

            #Store the sampling interval of 2s, or whatever sampling interval was chosen (which should be the most common)        
            mode = deltas.mode()

            #Create separate series of time deltas in seconds
            td_seconds = []
            for td in deltas:
                if isinstance(td, str): #Necessary for entries with helper text
                    td_seconds.append(td)
                else:
                    td_seconds.append(td.total_seconds())
            td_seconds = pd.Series(td_seconds, name="Time Delta (seconds)")

            #Initialize dataframe with datetime columns
            times = pd.DataFrame(df[date]).rename(columns={date:"Datetime"})

            #Create datetime + 1 and datetime - 1 series to be added into times df
            dtplusone = pd.Series(index=range(rows), name="Datetime_i+1", dtype="object")
            dtminusone = pd.Series(index=range(rows), name="Datetime_i-1", dtype="object")

            #Append necessary values
            dtplusone[0:-1] = df.loc[1:, date]
            dtplusone[rows-1] = "LAST TIMESTAMP" #Helper text---is it necessary?

            dtminusone[1:] = df.loc[:rows-2, date]
            dtminusone[0] = "FIRST TIMESTAMP" #Helper text---is it necessary?

            times = times.join([deltas, td_seconds, dtminusone, dtplusone])

            #Reorder columns to desired order
            times = times[["Datetime", "Datetime_i+1", "Time Delta", "Time Delta (seconds)", "Datetime_i-1"]]

            ### Appending the time deltas to the main df
            df = df.join([deltas, td_seconds])

            #Reordering columns
            df = df[[
            'Time (yyyy-MM-dd hh:mm:ss)',
            'Time Delta',
            'Time Delta (seconds)',
            'Temp (Celsius)',
            'Wet Bulb Temp. (Celsius)', 
            'Rel. Hum. (%)', 'Baro. (mb)',
            'Altitude (Meters)', 
            'Station P. (mb)', 
            'Wind Speed (m/s)',
            'Heat Index (Celsius)', 
            'Dew Point (Celsius)', 
            'Dens. Alt. (Meters)',
            'Crosswind (m/s)', 
            'Headwind (m/s)', 
            'Mag. Dir. (Degrees)',
            'True Dir. (Degrees)', 
            'Wind Chill (Celsius)', 
            ]]

            print("Time Deltas have been calculated")
            print(f"Most common sampling time in datafile is {mode[0].seconds} seconds")
            display(df[df.columns[1:3]])
            print("Proceed to STEP 4")
            timedeltas_read = True
        except Exception as e:
            print(e)

        ch_bound_1 = len(change_history)
    else:
        print("Time Deltas have already been calculated")
        print(f"Most common sampling time in datafile is {mode[0].seconds} seconds")
        display(df[df.columns[1:3]])
        print("Proceed to STEP 4")
        ch_bound_1 = len(change_history)
    return df, times, deltas, mode, timedeltas_read, ch_bound_1, change_history,

def calculate_timedelta_outliers(df, deltas):
    mode = deltas.mode()
    outliers = []
    outliers_index = []
    rows = len(df)    
    date = "Time (yyyy-MM-dd hh:mm:ss)"

    #Find the time deltas != chosen sampling interval
    for count, i in enumerate(deltas):
        if not (i==mode).any():
            outliers.append(i)
            outliers_index.append(count)
    outliers = pd.Series(outliers, name="Time Deltas != sampling interval")

    #Time deltas in seconds
    outliers_seconds = []
    for td in outliers:
        if isinstance(td, str): #Necessary for entries with helper text
            outliers_seconds.append(td)
        else:
            outliers_seconds.append(td.total_seconds())
    outliers_seconds = pd.Series(outliers_seconds, name="Time Delta (seconds)")

    print("Time delta outliers successfully calculated")

    #Initialize time delta != sampling interval comparison chart
    td = "Time Delta"
    tds = "Time Delta (Seconds)"
    dt = "Datetime"
    dtmin = "Datetime_i-1"
    dtplus = "Datetime_i+1"
    columnnames = [dt, dtplus, td, tds, dtmin] #REARRANGE COLUMNS HERE TO DESIRED LAYOUT

    td = columnnames.index(td)
    tds = columnnames.index(tds)
    dt = columnnames.index(dt)
    dtmin = columnnames.index(dtmin)
    dtplus = columnnames.index(dtplus)

    outliers_df = pd.DataFrame(index=outliers_index, columns=columnnames)

    #Append Time Deltas
    for index, value in enumerate(outliers):
        outliers_df.iloc[index, td] = value

    for index, value in enumerate(outliers_seconds):
        outliers_df.iloc[index, tds] = value

    #Append Datetimes
    for row, index in enumerate(outliers_index):
        if index == 0:
            outliers_df.iloc[row, dt] = df.loc[index, date] #Datetime
            outliers_df.iloc[row, dtmin] = "FIRST ENTRY"#Datetime_i-1
            outliers_df.iloc[row, dtplus] = df.loc[index+1, date]#Datetime_i+1
        elif index == rows-1:
            outliers_df.iloc[row, dt] = df.loc[index, date] #Datetime
            outliers_df.iloc[row, dtmin] = df.loc[index-1, date]#Datetime_i-1
            outliers_df.iloc[row, dtplus] = "NO ENTRY"#Datetime_i+1
        else:
            outliers_df.iloc[row, dt] = df.loc[index, date] #Datetime
            outliers_df.iloc[row, dtmin] = df.loc[index-1, date]#Datetime_i-1
            outliers_df.iloc[row, dtplus] = df.loc[index+1, date]#Datetime_i+1
    print("Time delta outliers chart successfully created")
    print(f"\nMost common sampling time in datafile is {mode[0].seconds} seconds")
    print("\nProceed to STEP 5")

    return outliers_df


def helper_plots(df, fieldTestParameters, columns):
    #Data
    #Column Names
    time = "Time (yyyy-MM-dd hh:mm:ss)"
    tdseconds = "Time Delta (seconds)"
    temp = "Temp (Celsius)"
    alt = "Altitude (Meters)"
    windspeed = "Wind Speed (m/s)"
    rh = "Rel. Hum. (%)"
    baro = "Baro. (mb)"
    magdir = "Mag. Dir. (Degrees)"

    source = ColumnDataSource(data=dict(
        index=df.index, 
        datetime=df[time], 
        timedelta=df[tdseconds], 
        temp=df[temp],
        alt=df[alt],
        windspeed=df[windspeed],
        rh=df[rh],
        baro=df[baro],
        magdir=df[magdir],
        )
    )

    tempvstime = ColumnDataSource(data=dict(x=[], y=[]))
    altvstime = ColumnDataSource(data=dict(x=[], y=[]))
    windspeedvstime = ColumnDataSource(data=dict(x=[], y=[]))
    rhvstime = ColumnDataSource(data=dict(x=[], y=[]))
    barovstime = ColumnDataSource(data=dict(x=[], y=[]))
    magdirvstime = ColumnDataSource(data=dict(x=[], y=[]))

    trimmedvalues = ColumnDataSource(data=dict(
        index = [],
        time = [],
        temp = [],
        alt = [],
        windspeed = [],
        rh = [],
        baro = [],
        magdir = []
    ))

    sources = [tempvstime, altvstime, windspeedvstime, rhvstime, barovstime, magdirvstime]

    #Formatting
    datefmt = DateFormatter(format="%F %I:%M:%S %p") #Format API reference: https://docs.bokeh.org/en/latest/docs/reference/models/widgets/tables.html?highlight=datatable#bokeh.models.DataTable
    width = 1000
    height = 300
    hovercolor = "black"
    barocolor = "orange"

    datetimevsindexhover = HoverTool( #API Reference: https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#hovertool
        tooltips=[
            ("Index", "$index"),
            ("Date", "@datetime{%F %I:%M:%S %p}"),
            ("Time Delta", "@{timedelta} seconds")
        ],

        formatters={
            "@datetime" : "datetime",
            #"@y1" : "numeral"
        },
        #mode = "vline"
    )

    options = dict(x_axis_label = "Row Index", tools=[datetimevsindexhover, "pan, wheel_zoom, xwheel_pan, ywheel_pan, box_select, box_zoom, reset"], plot_width=700, plot_height=300)
    links = dict(width=width, height=height, x_axis_type="datetime")
    #view = CDSView(source=source, filters=[IndexFilter(x)])
    sz = 5

    #INITIALIZING PLOTS************************************************************************************************

    #Datetime vs. Index
    f1 = figure(title = "Datetime vs. Index", y_axis_label = "Date", y_axis_type="datetime", **options)
    f1.line("index", "datetime", hover_color="red", source=source)
    f1.circle("index", "datetime", size=sz, hover_color="red", source=source, selection_color = "firebrick",) #API Reference: https://docs.bokeh.org/en/latest/docs/user_guide/styling/plots.html#selected-and-unselected-glyphs


    #Time Delta vs. Index
    f2 = figure(title = "Time Delta vs. Index", y_axis_label="Time Delta (s)", x_range=f1.x_range, **options)
    #f2.yaxis.formatter = DatetimeTickFormatter(seconds=["%S"])
    f2.line("index", "timedelta", hover_color="red", source=source)
    f2.circle("index", "timedelta", size=sz, hover_color="red", source=source, selection_color = "firebrick")

    columns = [
        TableColumn(field="datetime", title="Datetime", formatter= datefmt), #Reference: https://stackoverflow.com/questions/40942168/how-to-create-a-bokeh-datatable-datetime-formatter
        TableColumn(field="timedelta", title="Change in time (seconds)")
    ]

    dt1 = DataTable(background = "red", source=source, columns=columns)

    #TIME SERIES PLOTS*************************************************************************************************
    timegraphs = {
        "Altitude vs. Time": "red", 
        "Wind Speed vs. Time": "magenta", 
    }

    hover_timeseries = HoverTool(
        tooltips=[
            ("Index", "@index"),
            ("Time", "@time{%F %I:%M:%S %p}"),        
            ("Temperature", "@temp"),  
            ("Altitude", "@alt"),
            ("Windspeed", "@windspeed"),
            ("Relative Humidity", "@rh"),
            ("Barometric Pressure", "@baro"),
            ("Magnetic Direction", "@magdir"),  
        ],

        formatters={
            "@time" : "datetime",
        },
        #mode = "vline"
    )

    #TIME SERIES PLOTS SEPARATE******************************************************************************8
    timeylabels = [alt, windspeed]
    timeysourceskeys = ["alt", "windspeed"]
    time_series_options = dict(tools=[hover_timeseries, "pan, wheel_zoom, box_select, tap, reset"], plot_width=700, plot_height=300)
    p1, p2 = figure(), figure()
    timefigures = [p1, p2]

    for f, g, l, key in zip(timefigures, timegraphs, timeylabels, timeysourceskeys):
        i = timefigures.index(f)
        f = figure(title=g, x_range=timefigures[0].x_range, x_axis_label = "Time", y_axis_label=l, x_axis_type = "datetime", **time_series_options)
        f.title.text_color = timegraphs[g]
        f.yaxis.axis_label_text_color = timegraphs[g]
        f.yaxis.major_label_text_color = timegraphs[g]
        f.yaxis.axis_line_color = timegraphs[g]
        f.xaxis.formatter=DatetimeTickFormatter(
            hours="%I:%M:%S %p",
            minutes="%I:%M:%S %p")
        #f.background_fill_color = (204, 255, 255)
        timefigures[i] = f
        f.line("time", key, color=timegraphs[g], hover_color=hovercolor, source=trimmedvalues)
        f.circle("time", key, color=timegraphs[g], hover_color=hovercolor, source=trimmedvalues)
        
    tab1 = Panel(child=column(timefigures[0:2]), title="Time Series Plots")


    #RANGE INDICATOR*********************************************************************
    ranges = Paragraph(text="""SELECTED INDICES: """)

    #FIELD TEST INFO FOR PLOTS****************************************************************
    fieldtestinfo = Div(text=
    f"""
    <p>FIELD TEST: <b>{fieldTestParameters["Field Test Label"]}</b></p>
    <p>LOCATION: <b>{fieldTestParameters["Field Test Location"]}</b></p>
    <p>DATE: <b>{fieldTestParameters["Field Test Date"]}</b></p>
    <p>DEVICE: <b>{fieldTestParameters["Device Nickname"]}</b></p>
    """
    )

    #TODO DATE PICKER*************************************************************************
    #Filters to first entry with selected date
    """
    start_date = df[date].min().date()
    end_date = df[date].max().date()

    date_picker = DatePicker(title="Select Date of Field Test", value=start_date, min_date=start_date, max_date=end_date)"""

    #PLOT GENERATION**************************************************************************************************************************************************************
    #Reference for array performance https://github.com/bokeh/bokeh/blob/main/examples/interaction/js_callbacks/js_on_change.py
    source.selected.js_on_change("indices", CustomJS(args=dict(
        origin=source, 
        trimmedvalues=trimmedvalues,
        ranges=ranges
    ), 
    code="""
        const inds = cb_obj.indices; //Gets unsorted if you do a shift click selection in datatable
        console.log("INDS: " + inds)

        const d1 = origin.data;
        const d2 = trimmedvalues.data;

        const cols = ["temp", "alt", "windspeed", "rh", "baro", "magdir"];

        inds.sort(function(a, b){return a - b});

        //To clear for every box select
        d2["time"] = [];
        d2["index"] = [];

        for (let x in cols)
        {
            d2[cols[x]] = []
        }

        //Generate the plots
        for (let i = 0; i < inds.length; i++) 
        {
            d2["time"].push(d1["datetime"][inds[i]]);
            
            d2["index"].push(inds[i]);

            for (let x in cols)
            {
                const label = cols[x]
                d2[label].push(d1[label][inds[i]]);
            } 
        }

        //Display the range selection
        ranges.text = "SELECTED INDICES: " + inds[0] + " - " + inds[inds.length-1]

        //Refresh
        trimmedvalues.change.emit()

    """
        )
    )

    #ORGANIZING PLOTS INTO TABS********************************************
    #tab1 = Panel(child=f3, title="Temp")
    #Displaying the data
    layout1 = row(column(children=[f1, f2]), column(children=[dt1, ranges]))
    layout2 = row(Tabs(tabs=[tab1]), fieldtestinfo)

    show(column(layout1, layout2))

def trim_data(df, start_index, end_index, units = units):
    time = units["time"]
    alt = units["alt"]
    temp = units["temp"]
    windspeed = units["windspeed"]
    rh = units["rh"]
    baro = units["baro"]
    magdir = units["magdir"]
    
    df_indices = df.index

    if start_index not in df_indices:
        print(f"Specified start index, {start_index}, is not in the index range of {df_indices.start} and {df_indices.stop}")
        
    elif end_index not in df_indices:
        print(f"Specified end index, {end_index}, is not in the index range of {df_indices.start} and {df_indices.stop}")

    elif end_index < start_index:
        print(f"Specified END index, {end_index}, is less than the specified START index, {start_index}")

    else:
        trim_date_start = df[time][start_index].strftime("%A, %B %d, %Y, %I:%M:%S %p")
        trim_date_end = df[time][end_index].strftime("%A, %B %d, %Y, %I:%M:%S %p")
        print(f"TRIMMING FROM INDEX {start_index} to INDEX {end_index}")
        print("-"*50, trim_date_start, "to", trim_date_end,"-"*50, sep="\n")
        df_trim = df.loc[start_index:end_index]
        print(f"Review the data and proceed to STEP 8")
        display(df_trim)
        
        hovercolor = "black"

        trimmedvalues2 = ColumnDataSource(data=dict(
            index = df_trim.index,
            time = df_trim[time],
            alt = df_trim[alt],
            windspeed = df_trim[windspeed],
            temp=df_trim[temp],
            rh=df_trim[rh],
            baro=df_trim[baro],
            magdir=df_trim[magdir],
        ))

        timegraphs = {
            "Altitude vs. Time": "red", 
            "Wind Speed vs. Time": "magenta", 
        }

        hover_timeseries = HoverTool(
            tooltips=[
                ("Index", "@index"),
                ("Time", "@time{%F %I:%M:%S %p}"),        
                ("Temperature", "@temp"),  
                ("Altitude", "@alt"),
                ("Windspeed", "@windspeed"),
                ("Relative Humidity", "@rh"),
                ("Barometric Pressure", "@baro"),
                ("Magnetic Direction", "@magdir"),  
            ],

            formatters={
                "@time" : "datetime",
            },
            #mode = "vline"
        )

        timeylabels = [alt, windspeed]
        timeysourceskeys = ["alt", "windspeed"]
        time_series_options = dict(tools=[hover_timeseries, "pan, wheel_zoom, box_select, tap, reset"], plot_width=700, plot_height=300)
        p1, p2 = figure(), figure()
        timefigures = [p1, p2]

        for f, g, l, key in zip(timefigures, timegraphs, timeylabels, timeysourceskeys):
            i = timefigures.index(f)
            f = figure(title=g, x_range=timefigures[0].x_range, x_axis_label = "Time", y_axis_label=l, x_axis_type = "datetime", **time_series_options)
            f.title.text_color = timegraphs[g]
            f.yaxis.axis_label_text_color = timegraphs[g]
            f.yaxis.major_label_text_color = timegraphs[g]
            f.yaxis.axis_line_color = timegraphs[g]
            f.xaxis.formatter=DatetimeTickFormatter(
                hours="%I:%M:%S %p",
                minutes="%I:%M:%S %p")
            #f.background_fill_color = (204, 255, 255)
            timefigures[i] = f
            f.line("time", key, color=timegraphs[g], hover_color=hovercolor, source=trimmedvalues2)
            f.circle("time", key, color=timegraphs[g], hover_color=hovercolor, source=trimmedvalues2)

        show(column(timefigures[0:2]))

def baseline(indices, change_history, ch_bound_2, data, values, method, baseline_val_constant):       
    import numpy as np
    from sklearn import datasets, linear_model
    print("modules imported")    
    delay_time = 0.1
    time = "Time (yyyy-MM-dd hh:mm:ss)"
    #Check for valid index range (reference: https://datascienceparichay.com/article/python-flatten-a-list-of-lists-to-a-single-list/)
    validranges = [index for sublist in indices for index in sublist]
    validrange = True
    for i in validranges:
        if i not in data.index:
            validrange = False
    
    if validrange:
        print("valid range(s)")    
        print(indices)
        validmethods = ["LINEAR", "CONSTANT", "AVERAGE"]
        method = method.upper()
        if method in validmethods:
            print("valid method")    
            change_history = change_history[:ch_bound_2] #Refresh the change_history

            time_series = data["Elapsed Time (seconds)"].astype("int") #Elapsed Time is of type float and therefore can't be combined with a boolean operation
            time_filter = time_series & False
            values_series = values

            for ranges in indices:
                start = ranges[0]
                end = ranges[1] + 1
                baseline_starttime = data.loc[ranges[0], time].strftime("%I:%M:%S %p")
                baseline_endtime = data.loc[ranges[1], time].strftime("%I:%M:%S %p") 
                print(f"Baselining from {baseline_starttime} at index {start} to {baseline_endtime} at index {end} using baselining method: {method}")
                change_history.append(f"Data baselined from {baseline_starttime} to {baseline_endtime}")
                tm.sleep(delay_time)
                time_filter = time_filter | (time_series[start:end] | True)
                
            time_baseline = time_series[time_filter].values
            
            values_baseline = values_series[time_filter].values

            time_baseline = time_baseline.reshape(len(time_baseline), 1)
            values_baseline = values_baseline.reshape(len(values_baseline), 1)

            if method == "AVERAGE":
                print(f"\nPerforming {method} baseline procedure")
                tm.sleep(delay_time)
                baseline_avg = np.average(values_baseline)
                print(f"Baseline average: {baseline_avg}")
                baseline_array = np.full((len(time_series), 1), baseline_avg)
                change_history.append(f"Baseline procedure used: {method}. Baseline average: {baseline_avg}")

            elif method == "CONSTANT":
                print(f"\nPerforming {method} baseline procedure")
                print(f"Baseline constant used: {baseline_val_constant}")
                tm.sleep(delay_time)
                baseline_array = np.full((len(time_series), 1), baseline_val_constant)
                change_history.append(f"Baseline procedure used: {method}. Baseline constant used: {baseline_val_constant}")
            
            elif method == "LINEAR":
                change_history.append(f"Baseline procedure used: {method}")
                print(f"\nPerforming {method} baseline procedure")
                
                tm.sleep(delay_time)
                regr = linear_model.LinearRegression()
                regr.fit(time_baseline, values_baseline)
                time_array = time_series.values
                time_array = time_array.reshape(len(time_array),1)
                baseline_array = regr.predict(time_array)
                
                #Slope
                print("Slope =", regr.coef_)
                
                #Intercept
                print("Intercept =", regr.intercept_)
                
                #R^2
                r2 = regr.score(time_baseline, values_baseline)
                print("R^2 =", r2)  

            print(f"\n{method} baseline procedure completed successfully")
            baseline_est = pd.Series(baseline_array[:,0], name = "Altitude Baseline (Meters)")
            print("\nEstimated baseline values (Meters)")
            print(baseline_est)

            #Obtain the baselined values
            values_above_baseline = values_series - baseline_est
            values_above_baseline.rename("AOG (Meters)", inplace=True)
            print("\nAltitude Above Ground values (Meters)")
            print(values_above_baseline)

            return(baseline_est, values_above_baseline)
            
        else:
            print(f"'{method}' is an invalid method for baseline estimation")
            print("Valid methods are: LINEAR, AVERAGE, CONSTANT")

    else:
        print(f"Specified baseline ranges,{validranges}, do not fall within {data.index.start} and {data.index.stop}")
    
def review_baseline(baseline_series, AOG_series, baseline_ranges, baseline_method, data, return_df = True):    
    trimmed_file_baselined = data.join([baseline_series, AOG_series])
    time = "Time (yyyy-MM-dd hh:mm:ss)"
    alt = "Altitude (Meters)"

    #Reorder columns
    trimmed_file_baselined = trimmed_file_baselined[[
    'Time (yyyy-MM-dd hh:mm:ss)',
    'Elapsed Time (seconds)',
    'Sampling Interval (seconds)',
    'Temp (Celsius)',
    'Wet Bulb Temp. (Celsius)', 
    'Rel. Hum. (%)', 'Baro. (mb)',
    'Altitude (Meters)',
    baseline_series.name,
    AOG_series.name,
    'Station P. (mb)', 
    'Wind Speed (m/s)',
    'Heat Index (Celsius)', 
    'Dew Point (Celsius)', 
    'Dens. Alt. (Meters)',
    'Crosswind (m/s)', 
    'Headwind (m/s)', 
    'Mag. Dir. (Degrees)',
    'True Dir. (Degrees)', 
    'Wind Chill (Celsius)', 
    ]]  
    dot_size = 0.5
    
    altvstimehover = HoverTool( #API Reference: https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#hovertool
        tooltips=[
            ("Index", "$index"),
            ("Date", "@time{%F %I:%M:%S %p}"),
            ("Altitude", "@alt meters")
        ],

        formatters={
            "@time" : "datetime",
            #"@y1" : "numeral"
        },
        mode = "vline"
    )

    source = ColumnDataSource(data=dict(
        index = trimmed_file_baselined.index, 
        time = trimmed_file_baselined[time],
        alt = trimmed_file_baselined[alt],
        ab = trimmed_file_baselined[baseline_series.name],
        aog = trimmed_file_baselined[AOG_series.name]
        )
    )

    options = dict(x_axis_label = "Time", tools=[altvstimehover, "pan, wheel_zoom, box_zoom, reset"], plot_width=600, plot_height=400)
    ##############################################################################
    #Altitude Baseline Plot
    ab = figure(title="Altitude Baseline (shaded areas indicate values used as baseline)", y_axis_label = alt, **options)
    ab.xaxis.formatter = DatetimeTickFormatter(
        seconds=["%I:%M:%S %p"],
        minutes=["%I:%M:%S %p"],
        hours=["%I:%M:%S %p"]
    )
    ab.line("time", "alt", source=source, color="orange", legend_label = "Barometric Altitude")
    ab.circle("time", "alt", source=source, size = dot_size, color="orange")
    
    if baseline_method == "LINEAR":
        ab.line("time", "ab", source=source, color="green", line_width=2, legend_label = "Baseline Altitude")

    #Highlight the selected ranges
    for period in baseline_ranges:
        leftbound = trimmed_file_baselined.loc[period[0], time]
        rightbound = trimmed_file_baselined.loc[period[1], time]
        baseline_box = BoxAnnotation(left=leftbound, right=rightbound, fill_alpha=0.2, fill_color="green")
        ab.add_layout(baseline_box)

    ##############################################################################
    #Altitude Above Ground Plot
    aog = figure(title = "Altitude Above Ground", x_range = ab.x_range, y_axis_label = alt, **options)
    aog.xaxis.formatter = DatetimeTickFormatter(
        seconds=["%I:%M:%S %p"],
        minutes=["%I:%M:%S %p"],
        hours=["%I:%M:%S %p"]
    )
    aog.line("time", "aog", source=source)
    aog.circle("time", "aog", source=source, size = dot_size)

    show(column(ab, aog))

    if return_df:
        return trimmed_file_baselined

def plot_altvstime(trimmed_file):
    time = units["time"]
    alt = units["alt"]

    baseline = ColumnDataSource(data=dict(
        index = trimmed_file.index, 
        time = trimmed_file[time], 
        alt = trimmed_file[alt]
        )
    )

    altvstimehover = HoverTool( #API Reference: https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#hovertool
        tooltips=[
            ("Index", "$index"),
            ("Date", "@time{%F %I:%M:%S %p}"),
        ],

        formatters={
            "@time" : "datetime",
            #"@y1" : "numeral"
        },
        mode = "vline"
    )

    options = dict(x_axis_label = "Time", tools=[altvstimehover, "pan, wheel_zoom, box_select, tap, reset"], plot_width=700, plot_height=400)

    f = figure(title = "Altitude vs. Time", y_axis_label = alt, **options)
    f.xaxis.formatter = DatetimeTickFormatter(
        seconds=["%I:%M:%S %p"],
        minutes=["%I:%M:%S %p"],
        hours=["%I:%M:%S %p"]
    )
    f.line("time", "alt", source=baseline)
    f.circle("time", "alt", source=baseline, size = 5)

    ranges = Paragraph(text="""SELECTED INDICES: """)

    ####################################################################
    #TODO
    baseline.selected.js_on_change("indices", CustomJS(args=dict(ranges=ranges),
    code="""
        
        const inds = cb_obj.indices; //Gets unsorted if you do a shift click selection in datatable
        console.log("INDS: " + inds)
        //If condition necessary to optimize performance (so the code doesn't run for any accidental selections)
            
        //Display the range selection
        ranges.text = "SELECTED INDICES: " + inds[0] + " - " + inds[inds.length-1]

    """
        )
    )                             
    ####################################################################
    show(column(f, ranges))