# calculate.py
# Copyright 2012 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Calculate performances from a file of chess game results."""

if __name__=='__main__':

    from . import APPLICATION_NAME

    try:
        from solentware_misc.gui.startstop import (
            start_application_exception,
            stop_application,
            application_exception,
            )
    except Exception as error:
        import tkinter.messagebox
        try:
           tkinter.messagebox.showerror(
               title='Start Exception',
               message='.\n\nThe reported exception is:\n\n'.join(
                   ('Unable to import solentware_misc.gui.startstop module',
                    str(error))),
               )
        except:
            pass
        raise SystemExit('Unable to import start application utilities')
    try:
        from .gui.calculator import Calculator
    except Exception as error:
        start_application_exception(
            error,
            appname=APPLICATION_NAME,
            action='import')
        raise SystemExit(' import '.join(('Unable to', APPLICATION_NAME)))
    try:
        app = Calculator()
    except Exception as error:
        start_application_exception(
            error,
            appname=APPLICATION_NAME,
            action='initialise')
        raise SystemExit(' initialise '.join(('Unable to', APPLICATION_NAME)))
    try:
        app.widget.mainloop()
    except SystemExit:
        stop_application(app, app.widget)
        raise
    except Exception as error:
        application_exception(
            error,
            app,
            app.widget,
            title='Chess Performace Calculator',
            appname=APPLICATION_NAME)
