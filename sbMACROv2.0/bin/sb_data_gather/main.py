"""Main module from which all Science Base data gathering branches."""
import os
from datetime import datetime
import gl
import fiscal_years
import projects
import db_save


def full_hard_search(app):
    """Perform hard search on any ids older than 1 day.

    This function calls get_all_cscs() to populate the fy_obj_list list with
    fiscal year objects for each of the fiscal years present in each CSC.
    It begins the parsing process by calling parse_fiscal_years(), which finds
    all projects in each fiscal year and each item in each project to create a
    comprehensive database for each fiscal year in each CSC. All CSCs, fiscal
    years, projects, items, etc are added to their respective relational
    database tables.

    Arguments:
        app -- (App class) As defined in the package's __init__.py, the class
               gives access to the application instance, the database, and the
               db models.

    Raises:
        Exception -- If something was wrong and fy_obj_list was not cleared by
                     the end of the process.

    """
    # To run this package from command line:
    # python -c 'from __init__ import start; start()'

    fy_obj_list = fiscal_years.get_all_cscs()

    if __debug__:
        print("fy_obj_list:\n{0}".format(fy_obj_list))
    fy_obj_list = fiscal_years.parse_fiscal_years(app, fy_obj_list)
    update_casc_total_data(app)
    if not fy_obj_list:
        print("""

    ===========================================================================

                    Hard Search is now finished.""")
        exit(0)
    print("WHY AM I HERE???")
    assert False, "Should never get here!!!!"
    raise Exception("Something went wrong in full_hard_search()")


def defined_hard_search(app):
    """Perform hard search on specific fiscal years via user-input.

    This hard search function collects fiscal years from a user that are
    parsed to find projects, which are parsed to find items. All CSCs, fiscal
    years, projects, items, etc are added to their respective relational
    database tables.

    Arguments:
        app -- (App class) As defined in the package's __init__.py, the class
               gives access to the application instance, the database, and the
               db models.

    Raises:
        Exception -- If something was wrong and fy_obj_list was not cleared by
                     the end of the process.

    """
    # To run this function from command line:
    # python -c 'from main import defined_hard_search; defined_hard_search()'

    fy_id_list = fiscal_years.get_user_input_fys()
    fy_obj_list = fiscal_years.create_fy_objs(fy_id_list)

    if __debug__:
        print("fy_obj_list:\n{0}".format(fy_obj_list))
    fiscal_years.parse_fiscal_years(app, fy_obj_list)
    update_casc_total_data(app)
    if not fy_obj_list:
        print("""

    ===========================================================================

                    Defined Hard Search is now finished.""")
        exit(0)
    print("WHY AM I HERE???")
    assert False, "Should never get here!!!!"
    raise Exception("Something went wrong in full_hard_search()")


def debug_projects():
    """For debugging/testing, find all items and calculate project size.

    The function can be given a fiscal year ID and CSC, or use a 'dummy'
    default (SWCSC FY 2011) if not important. It will then parse the project
    and its items as it normally would and print the results.
    """
    # To run this from the terminal, use the following:
    # python -c 'from main import debug_projects; debug_projects()'

    project_id = '1'
    while len(project_id) != 24:
        print("Please provide a Science Base Project ID.")
        project_id = input("Project ID: ")
    print("Provide a fiscal year ID and CSC, or use Dummy Fiscal Year?")
    preference = input("> ").lower()
    if "dum" in preference:
        # Dummy Fiscal Year:
        fiscal_year = gl.SbFiscalYear("50070504e4b0abf7ce733fd7", "SWCSC")
    else:
        fy_id = input("Fiscal Year ID: ")
        fy_csc = input("CSC: ")
        fiscal_year = gl.SbFiscalYear(fy_id, fy_csc)

    project = gl.SbProject(project_id, fiscal_year)
    projects.parse_project(project)
    print("\n\nAnother? (Y / N)")
    answer = input("> ").lower()
    if 'y' in answer:
        debug_projects()
    elif 'n' in answer:
        exit(0)
    else:
        print("Neither answer selected. Program ended.")


def id_in_list(obj_list, sb_object):
    """Check if an Science Base object exists in a list.

    Arguments:
        obj_list -- (list) a list of objects with an 'ID' attribute.
        sb_object -- (item_id, SbFiscalYear, SbProject, or SbItem)
                     Any item with an '.ID' field.

    Returns:
        True -- (boolean) returned if an item is encountered in obj_list with
                an .ID attribute that matches the .ID attribute of sb_object.
        False -- (boolean) returned if no such item is encountered after
                 iterating through obj_list.

    """
    if __debug__:
        print("Checking if sb_object in list...")
    for sb_objects in obj_list:
        if sb_object.ID == sb_objects.ID:
            if __debug__:
                print("Object in list.")
            return True
    if __debug__:
        print("Object not in list")
    return False


def get_date():
    """Return the current date as a string."""
    now = datetime.now()
    date = now.strftime("%Y%m%d")
    return date

def save_to_db(app, fiscal_year):
    """Save Fiscal Year data to database.
    
    Call functions from the module 'db_save.py' to save Fiscal Year, Projects,
    Items, etc to the database.
    
    Arguments:
        app -- (App class) As defined in the package's __init__.py, the class
               gives access to the application instance, the database, and the
               db models.
        fiscal_year -- (SbFiscalYear) A completed SbFiscalYear object (defined
                       in 'gl.py') to be parsed and saved to the database.

    """
    # Save casc to db and get db model for casc
    casc_model = db_save.save_casc(app, fiscal_year)

    fy_model = db_save.save_fy(app, fiscal_year, casc_model)

    for project in fiscal_year.projects:
        proj_model = db_save.save_proj(app, project, fy_model, casc_model)
        for item in project.project_items["Project_Item_List"]:
            item_model = db_save.save_item(app, item, proj_model, fy_model,
                                           casc_model)
            for file_json in item.file_list:
                db_save.save_file(app, file_json, item_model, proj_model,
                                  fy_model, casc_model)


def update_casc_total_data(app):
    print("""
------------------------------------------------------------------------------
          """)
    print("Updating all CASC `.total_data` fields...")
    cascs = app.db.session.query(app.casc).all()
    print("CASCs found:")
    num = 0
    for casc in cascs:
        num += 1
        total_data = 0
        print("\t{0}. {1}".format(num, casc.name))
        fys = casc.fiscal_years.all()
        for fy in fys:
            total_data += fy.total_data
            if (total_data - fy.total_data) == 0:
                print("{}".format(fy.total_data), end="")
            else:
                print(" + {}".format(fy.total_data), end="")
        print("\n")
        casc.total_data = total_data
        app.db.session.commit()
        print("Total Data in {0}:\n\t{1}\n\n"
              .format(casc.name, casc.total_data))

    print("""
------------------------------------------------------------------------------
          """)
