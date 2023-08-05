Description
===========

Python-based tool for presentation-ready slides

Installation
============

.. code-block:: shell

  pip install pyslides


Also, you need to have ``acroread`` in your path.


Community
============

For bug reports and new ideas, feel free to join the  `Mailing list <https://groups.google.com/forum/#!forum/pyslides>`_

Usage
=====

.. code-block:: python


  from pyslides.presentation import Presentation as P

  P = P(biblio_file='biblio.bib')

  P.add_slide(model = 'title', title = 'An example of presentation with PySlides',\
                               author      = 'Francesco Rossi',\
                               affiliation = 'Free University')


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
           text = 'Example of adding text')


  P.add_figure(x=0.7,y=0.5,L=0.3,filename='https://wesaturate.s3.amazonaws.com/photos/ofinqs_shane1536.jpg')


  P.render(show_pdf=True)


Author
======

Giuseppe Romano (romanog@mit.edu)



