sparkler
========

A command line tool for generating sparklines from GitHub stats.

GitHub has several APIs for extracting activity statistics in a raw JSON
format. Sparkler is a tool that can take this raw data and generate sparkline
images to show the activity level over a period of time.

Sparkler will create a sparkline of the commit activity over the last year.

Installing
----------

Sparkler can be installed with pip::

  $ pip install --user sparkler

Using
-----

There are two inputs required when running sparkler, the GitHub repo you wish
to graph and the name of the file to save the graph.

.. note::

   Due to some compatibility issues in some of the used libraries, only jpg
   file formats have been tested so far. PNG is known to have an issue.

To get the last year's commit activity for the kubernetes/kubernetes repo, use
the command line::

   sparkler kubernetes/kubernetes activity.jpg

Additional options are available for setting the foreground and background
colors of the generated graph. Refer to the help text for details::

   sparkler -h
   usage: sparkler [-h] [--version] [--background BACKGROUND] [--line LINE]
                   repo outfile

   positional arguments:
     repo                  The GitHub org/repo to report on.
     outfile               The file name for the generated image. Note: Due to
                           current library issues, this must be a jpg.

   optional arguments:
     -h, --help            show this help message and exit
     --version             show program's version number and exit
     --background BACKGROUND
                           The background color of the sparkline image.
     --line LINE           The sparkline image line color.

Feel free to open GitHub Issues or put up a pull request.
