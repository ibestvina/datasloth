
DataSloth
=========

*Natural language Pandas queries and data generation powered by GPT-3*


Installation
------------

``pip install datasloth``

Usage
-----

In order for DataSloth to work, you must have a working `OpenAI API
key <https://beta.openai.com/account/api-keys>`__ set in your
environment variable, or provide it to the DataSloth object. For more
info, refer to this
`guide <https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety>`__.

DataSloth automatically discovers all Pandas dataframes in your
namespace (filtering out names starting with an underscode). Before you
load any data, import DataSloth and create the ``sloth``:

.. code:: python

   from datasloth import DataSloth
   sloth = DataSloth()

Next, load any data you want to use. Try naming your dataframes and
columns in a meaningful way, as DataSloth uses these names to understand
what the data is about.

Once your data is loaded, simply run

``sloth.query('...')``

to query the data.
