pyfca
=====

https://github.com/pyfca/pyfca

Python Formal Concept Analysis (`FCA`_).

The purpose is to collect algoritms for FCA.

Algorithms
----------

So far:

lattice construction:

- AddIntent

implications basis:

- Koenig

lattice drawing:

- create lattice diagram and output in 

    - svg
    - tkinter

Plan
----

- Create a basic lattice data structure:

- Merge existing sources available online.

  Lattice construction:

  - FCbO
  - InClose2
  - ...

  Implications basis:

  - Closure
  - LinClosure
  - Wild's Closure
  - ...


.. _`FCA`: https://en.wikipedia.org/wiki/Formal_concept_analysis



Usage
-----

It can be used to create a concept lattice and to draw it either using tkinter() or svg().

.. code::

    import pyfca
    fca = pyfca.Lattice([{1,2},{2},{1,3}])
    diagram = pyfca.LatticeDiagram(fca,4*297,4*210)
    diagram.svg().saveas('tmp.svg')
    import cairosvg
    cairosvg.svg2png(url="file:///<path to tmp.svg>", write_to='tmp.png')



The ``AddIntent`` algorithm is from the paper:

    AddIntent: A New Incremental Algorithm for Constructing Concept Lattices


The lattice drawing algorithm is from:

    `Galicia <http://www.iro.umontreal.ca/~galicia/>`_




Implications
------------

This uses the python int as a bit field to store the FCA context.

See this `blog`_ for more.


.. _`blog`: http://rolandpuntaier.blogspot.com/2015/07/implications.html


