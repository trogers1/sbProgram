#!/usr/bin/env python3
"""Module for app instantiation and shell context creation."""
import sys
import os
from app import create_app, db
from app.models import User, casc, FiscalYear, Project, Item, SbFile
from app.models import ProblemItem, PrincipalInvestigator
# from flask_socketio import SocketIO # We will use this for real-time feedback during database updates

app = create_app() # pylint: disable=C0103
# socketio = SocketIO(app)


@app.shell_context_processor
def make_shell_context():
    """Define shell context for FLASK_SHELL and import model classes.

    Returns:
        db -- SQLite database instance.
        User -- User database model class
        casc -- casc database model class
        FiscalYear -- FiscalYear database model class
        Project -- Project database model class
        Item -- Item database model class
        SbFile -- SbFile database model class
        ProblemItem -- ProblemItem database model class

    """
    return {
        'db': db,
        'User': User,
        'casc': casc,
        'FiscalYear': FiscalYear,
        'Project': Project,
        'Item': Item,
        'SbFile': SbFile,
        'ProblemItem': ProblemItem,
        'PrincipalInvestigator': PrincipalInvestigator
    }

if __name__ == "__main__":
    # socketio.run(app)
    app.run(debug = True, threaded = True)
