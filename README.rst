lightspeed.py
=============

lightspeed.py is a modern, easy to use, feature-rich, and async ready API wrapper
for Lightspeed.

.. warning::
    This is alpha software. Please report bugs on GitHub issues if you will find any.

.. note::
    I made this project for learning Sphinx.

Key Features
-------------
- Modern Pythonic API using ``async``\/``await`` syntax
- Sane rate limit handling that prevents 429s
- Easy to use with an object oriented design
- Optimised for both speed and memory


Quick Example
--------------

.. code:: py

    import asyncio
    import lightspeed

    client = lightspeed.Client()

    async def main():
        name = input('Input name of user you wish to view: ')
        try:
            user = await client.fetch_user(name)
        except lightspeed.NotFound:
            print('Sorry,', name, 'does not exist.')
        else:
            print(user.name)
            print('-' * len(user.name))
            print(user.bio)

    asyncio.run(main())

Links
------

- `Documentation <https://lightspeed.readthedocs.io/en/latest/index.html>`_
