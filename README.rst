Huffman
-------

Huffman coding is a lossless data compression algorithm that is used to reduce
the size of data by using a combination of a binary tree and prefix code.

It creates a binary tree of nodes, where each node has a value and a weight.
The tree is then traversed to create a prefix code for each value.

See Tom Scott's excellent 
`"How Computers Compress Text: Huffman Coding and Huffman Trees"
<https://www.youtube.com/watch?v=JsTptu56GM8>`_
for a great explanation of Huffman coding.

Languages
=========

Currently it is only implemented for Python.
In the future I hope to write a C++ and Rust version.

Python
~~~~~~

Install the dependencies with:
::
    poetry install

If you want to use the visualiser, you need to install the :code:`pydot` library.
This can be done adding :code:`-E vis` to your :code:`poetry install` command,
or you can install the :code:`pydot` library with whatever is your preferred package manager (e.g pip)
in which case you can run the program as you would normally run a python file.

Then you can run the program with :code:`poetry run python3 huffman.py`

C++
~~~

Rust
~~~~

See also
========
`Wikipedia article on Huffman coding <https://en.wikipedia.org/wiki/Huffman_coding>`_.

`Wikipedia article on prefix codes <https://en.wikipedia.org/wiki/Prefix_code>`_.
