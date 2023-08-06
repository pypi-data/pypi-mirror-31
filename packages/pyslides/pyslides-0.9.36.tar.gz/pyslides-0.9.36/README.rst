Description
===========

Python-based tool for presentation-ready slides

Installation & Usage
====================

.. code-block:: shell

  pip install --upgrade pyslides

  mkdir -p example_pyslides && cd example_pyslides

  download_pyslides_example

  python example.py


The file ``slides.pdf`` is created. 

Requirements
============

latex package ``type1cm`` 

Community
=========

For bug reports and new ideas, feel free to join the  `Mailing list <https://groups.google.com/forum/#!forum/pyslides>`_

Example
=======

.. code-block:: python


  from pyslides.presentation import Presentation as P

  P = P(biblio_file='https://www.dropbox.com/s/6x55qbs8p0fb3yl/biblio.bib?dl=1')

  P.add_slide(model = 'title', title = 'An example of presentation with PySlides',\
                               author      = 'Name',\
                               affiliation = 'Affiliation')

  P.add_slide(model='one_figure',\
             figure = 'https://wesaturate.s3.amazonaws.com/photos/zbihcy_silvestre90.jpg',\
             title='Example')

  P.add_citation('einstein1935can')


  P.add_slide()
  P.add_bullets(y = 0.5,\
                text = [r'''Cats are cute''',r'''Especially this one'''])

  P.add_text(x = 0.5,\
             y = 0.1,\
             color='red',\
             text = '$E=m^2$')

  P.add_figure(x=0.7,y=0.5,L=0.3,filename='https://wesaturate.s3.amazonaws.com/photos/ofinqs_shane1536.jpg')

  P.render()


See `PDF <https://www.dropbox.com/s/ggox95x08zjckbj/example.pdf?dl=1>`_

Support
=======

This is a personal, unfunded project. If you like it, kindly consider a `donation <https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=78PRMGHZYAEB8>`_ !


Author
======

Giuseppe Romano (romanog@mit.edu)


