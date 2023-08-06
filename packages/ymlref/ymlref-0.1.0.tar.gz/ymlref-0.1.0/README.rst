ymlref: load Yaml documents with possibility to resolve references.
==========================================================================

|License: MIT|

**ymlref** is a library that allows you to load Yaml documents and resolve JSON-pointer references
inside them.

Usage example
-----------

.. code:: python

   import ymlref


   DOCUMENT = """

   authors:
     shakespear:
       first_name: William
       last_name: Shakespear
     dostoevsky:
       first_name: Fyodor
       last_name: Dostoevsky
   books:
      - title: Makbet
	author:
	  $ref: "#/authors/shakespear"
      - title: Crime and punishment
	author:
	  $ref: "#/authors/dostoevsky"
   """

   doc = ymlref.loads(DOCUMENT)
   print('Books in document: \n')
   for book in doc['books']:
       print(book['title'])
       print('Author: ' + book['author']['first_name'] + ' ' + book['author']['last_name'])
       print('---')

Exposed API
----------------
**ymlref** provides two functions: **load** and **loads**. The first one loads document from file-like object, while the second one loads document from `str` object.

.. |License: MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
