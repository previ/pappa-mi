# Introduction #

In order to properly setup the local development server, do the following steps:


# Pass 1: Install the Application #

  1. Download and install the Google App Engine Python runtime
  1. Download the Pappa-Mi source here: http://pappa-mi.googlecode.com/files/pappami-2.0.0.0.rar and expand the archive in a directory called "pappami"
  1. Run the App Engine Launcher and add the Pappa-Mi application selecting the previuosly created dir.
  1. Run the application

# Pass 2: Upload configuration data #
  1. Download the configuration data here: http://pappa-mi.googlecode.com/files/cfg.rar and expand it in a dir NOT under the previously created pappami dir
  1. Run a command prompt and run the following command: set PYTHONPATH=<path to pappami dir>
  1. Run the following commands:
    1. appcfg.py upload\_data --num\_threads=1 --url=http://localhost:8080/_ah/remote_api --filename=<cfg dir>/cy.dat
    1. appcfg.py upload\_data --num\_threads=1 --url=http://localhost:8080/_ah/remote_api --filename=<cfg dir>/cc.dat
    1. appcfg.py upload\_data --num\_threads=1 --url=http://localhost:8080/_ah/remote_api --filename=<cfg dir>/cm.dat
    1. appcfg.py upload\_data --num\_threads=1 --url=http://localhost:8080/_ah/remote_api --filename=<cfg dir>/ccc.dat
    1. appcfg.py upload\_data --num\_threads=1 --url=http://localhost:8080/_ah/remote_api --filename=<cfg dir>/zo.dat
    1. appcfg.py upload\_data --num\_threads=1 --url=http://localhost:8080/_ah/remote_api --filename=<cfg dir>/ccz.dat
    1. appcfg.py upload\_data --num\_threads=1 --url=http://localhost:8080/_ah/remote_api --filename=<cfg dir>/mn.dat
    1. appcfg.py upload\_data --num\_threads=1 --url=http://localhost:8080/_ah/remote_api --filename=<cfg dir>/pt.dat
    1. appcfg.py upload\_data --num\_threads=1 --url=http://localhost:8080/_ah/remote_api --filename=<cfg dir>/pg.dat
  1. The application is configured

# Pass 3: Run the app #
  1. Open the app at http://localhost:8080
  1. Register as a new User
  1. The "Città" list should be populated with "Milano" and "Torino"
  1. Selecting "Milano", the "Scuola" combo should contain about 440 items.
  1. Complete registration and use the app.
