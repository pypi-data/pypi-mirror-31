
=====
Kopi
=====

Description:
~~~~~~~~~~~~
A collection of light weight modules to
create **publication quality** graph in pdf format
using CSON (CoffeeScript-Object-Notation) to manipulate
the plot style.

Installation
~~~~~~~~~~~~
Python 3 as default Python::

	pip install kopi

Python as Python3::

pip3 install kopi

Features
~~~~~~~~
The output pdf file is *readily editable*
using Adobe Illustrator or equivalent tool.
(Keynote nowadays keep the fidelity of the pdf file)

The style can be easily manipulated by changing the
parameters in the accompanying .cson files.

The auto-generated coffee (*.cson) itself is a useful
documentation to provide basic guide to manipulate
the graph property.


========
Examples
========

Example 1 ::

   import kopi as kp
   x = [1,2,3]
   y = [1,4,9]
   kp.plot(x,y)

or use numpy array::

	import numpy as np
	x = np.array([1,2,3])
	y = x**2
	kp.plot(x,y)


To modify the labels, title, and othe plot sytle other
than the default values::

   kp.plot(x,y, coffee = "myflavour.cson")

In the *myflavor.cson*::

   # This is myflovour.cson
   ...
   xLabel:
      Text: "Your label for x-axis"
      ...
	  ...
   Xaxis:
      ...
	  LineWidth: 1.0
      ...
   ...

To plot multiple curves in one graph,
put the x and y arrays in separate list::

   x = np.array([1,2,3])
   y1 = x
   y2 = x**2
   y3 = x**3
   k.plot([x, x, x], [y1, y2, y3])


Use mplot to create multiple subplots in one graph.
Bundle the list of array in a global list::
    x = np.array([1,2,3])
    y1 = x
    y2 = x**2
    y3 = x**3
   k.mplot([
      [x, y1], # 1st subplot
      [x, y2], # 2nd subplot
      [[x,x],[y1, y2]] # 3rd subplot with two curves
	])

Terminology
~~~~~~~~~~~
#. kopi:
    Malay word for coffee. The term is widely used in Malaysia and Singapore.

#. coffee:
    Name of the cson file to adjust the the graph properties in a single plot.

#. latte:
    Name of the cson file to adjust the appearance of multiple plots in a single page (or figure)

#. sugar :
    Dictionary (in class format) to overwrite the content in
	coffee (plot style .cson file )

#. milk :
    Dictionary to overwrite the content in
	latte (multi plot style .cson file )
