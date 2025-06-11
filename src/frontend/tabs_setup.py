from services.gui_service import Table


def goto_tab(main_win):
    goto_late_rides = Table(
        title="Late Rides",
        columns=["Ride ID", "End Time", "Future Ride", "Future Ride Time"]
    )
    goto_late_rides.start_loading()
    main_win.build_tab(title="Goto", color="#201c6c", widgets=[goto_late_rides])
    
    return {'late_rides': goto_late_rides}


def autotel_tab(main_win):
    batteries_table = Table(
        title="Batteries",
        columns=["Ride ID", "License Plate", "Battery", "Location"],
    )
    long_rides_table = Table(
        title="Long Rides",
        columns=["Ride ID", "Driver ID", "Duration", "Location"]
    )
    batteries_table.start_loading()
    long_rides_table.start_loading()
    
    main_win.build_tab(title="Autotel", color="#80c454", widgets=[batteries_table, long_rides_table])
    
    return {'batteries': batteries_table, 'long_rides': long_rides_table}

def setup_tabs_and_tables(main_win):
    """
    Sets up the GOTO and Autotel tabs in the main window.
    
    Args:
        main_win: The main window instance where the tabs will be added.
    """
    goto_tables = goto_tab(main_win)
    
    autotel_tables = autotel_tab(main_win)
    
    return {**goto_tables, **autotel_tables}