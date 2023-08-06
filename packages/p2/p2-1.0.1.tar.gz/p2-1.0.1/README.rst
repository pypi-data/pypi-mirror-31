p2: Rerun command when given filed changed
==========================================

.. image:: http://img.shields.io/pypi/v/p2.svg?style=flat
   :target: https://pypi.org/project/p2/

.. code-block:: sh

  % p2 'make' *.plim static/*.scss
  Player Two is watching about 6 files:
  (' base.plim content.plim index.plim oldcontent.plim oldindex.plim '
   'static/index.scss')
  FIGHT!
  make
  python -mscss < static/index.scss > static/index.css
  plimc -H -o index.html index.plim
  CONTINUE?
  content.plim changed
  FIGHT!
  make
  python -mscss < static/index.scss > static/index.css
  plimc -H -o index.html index.plim
  CONTINUE?
  ^CGAMEOVER

Installation
------------

.. code-block::

  pip install p2
