lynkz
=====

A python wrapper for the https://lynkz.me api

Usage
-----

.. code:: python

    import lynkz

    output = lynkz.shorten("https://your.website/here")

    # output now is an array that looks like this:
    # ["https://lynkz.me/ID-HERE", "YOUR DELETE KEY"]

    # To delete the shortend link:

    lynkz.delete("https://lynkz.me/ID-HERE", "YOUR DELETE KEY") # do NOT put a slash after the link id

    # OR

    lynkz.delete(output[0], output[1]) # if you still have the origional array
