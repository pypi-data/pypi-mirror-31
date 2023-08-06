rss2toot
===========
.. code-block:: python


   # Import and run
   '''
   >>> import rss2toot
   >>> rss2toot.toot('http://planetpython.org/rss20.xml', 'https://somemastodon.instance')
   First run of this tool, we need to generate access token.
   Username: your.mastodon@username.com
   Password: YourVerySecretMastodonPassword
   '''
   # and we are done
   
   # Let's run the same again with verbose flag (no username or password needed this time):
   '''
   >>> rss2toot.toot('http://planetpython.org/rss20.xml', 'https://somemastodon.instance', verbose=True)
   Found 25 items in total for feed http://planetpython.org/rss20.xml
   Found 0 new items for feed http://planetpython.org/rss20.xml
   '''