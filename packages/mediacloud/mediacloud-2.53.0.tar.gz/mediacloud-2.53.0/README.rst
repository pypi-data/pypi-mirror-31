MediaCloud Python API Client
============================

This is the source code of the python client for the `MediaCloud API
v2 <https://github.com/berkmancenter/mediacloud/blob/master/doc/api_2_0_spec/api_2_0_spec.md>`__.

Usage
-----

First `sign up for an API
key <https://core.mediacloud.org/login/register>`__. Then

::

    pip install mediacloud

Examples
--------

To get the first 2000 the stories associated with a query and dump the
output to json:

.. code:: python

    import mediacloud, json, datetime
    mc = mediacloud.api.MediaCloud('MY_API_KEY')

    fetch_size = 1000
    stories = []
    last_processed_stories_id = 0
    while len(stories) < 2000:
        fetched_stories = mc.storyList('( obama AND policy ) OR ( whitehouse AND policy)', 
                                       solr_filter=[ mc.publish_date_query( datetime.date(2013,1,1), datetime.date(2015,1,1)), 
                                                                             'tags_id_media:1'],
                                        last_processed_stories_id=last_processed_stories_id, rows= fetch_size)
        stories.extend( fetched_stories)
        if len( fetched_stories) < fetch_size:
            break
        
        last_processed_stories_id = stories[-1]['processed_stories_id']
        
    print json.dumps(stories)

Find out how many sentences in the US mainstream media that mentioned
"Zimbabwe" and "president" in 2013:

.. code:: python

    import mediacloud, datetime
    mc = mediacloud.api.MediaCloud('MY_API_KEY')
    res = mc.sentenceCount('( zimbabwe AND president)', solr_filter=[mc.publish_date_query( datetime.date( 2013, 1, 1), datetime.date( 2014, 1, 1) ), 'tags_id_media:1' ])
    print res['count'] # prints the number of sentences found

Alternatively, this query could be specified as follows

.. code:: python

    import mediacloud
    mc = mediacloud.api.MediaCloud('MY_API_KEY')
    results = mc.sentenceCount('( zimbabwe AND president)', '+publish_date:[2013-01-01T00:00:00Z TO 2014-01-01T00:00:00Z} AND +tags_id_media:1')
    print results['count']

Find the most commonly used words in sentences from the US mainstream
media that mentioned "Zimbabwe" and "president" in 2013:

.. code:: python

    import mediacloud, datetime
    mc = mediacloud.api.MediaCloud('MY_API_KEY')
    words = mc.wordCount('( zimbabwe AND president)',  solr_filter=[mc.publish_date_query( datetime.date( 2013, 1, 1), datetime.date( 2014, 1, 1) ), 'tags_id_media:1' ] )
    print words[0]  #prints the most common word

To find out all the details about one particular story by id:

.. code:: python

    import mediacloud
    mc = mediacloud.api.MediaCloud('MY_API_KEY')
    story = mc.story(169440976)
    print story['url']  # prints the url the story came from

To save the first 100 stories from one day to a database:

.. code:: python

    import mediacloud, datetime
    mc = mediacloud.api.MediaCloud('MY_API_KEY')
    db = mediacloud.storage.MongoStoryDatabase('one_day')
    stories = mc.storyList(mc.publish_date_query( datetime.date (2014, 01, 01), datetime.date(2014,01,02) ), last_processed_stories_id=0,rows=100)
    [db.addStory(s) for s in stories]
    print db.storyCount()

Take a look at the ``apitest.py`` and ``storagetest.py`` for more
detailed examples.

Development
-----------

If you are interested in adding code to this module, first clone `the
GitHub repository <https://github.com/c4fcm/MediaCloud-API-Client>`__.

Testing
-------

First run all the tests. Copy ``mc-client.config.template`` to
``mc-client.config`` and edit it. Then run ``python tests.py``. Notice
you get a ``mediacloud-api.log`` that tells you about each query it
runs.

Distribution
------------

1. Run ``python test.py`` to make sure all the test pass
2. Update the version number in ``mediacloud/__init__.py``
3. Make a brief note in the version history section in the README file
   about the changes
4. Run ``python setup.py sdist`` to test out a version locally
5. Then run ``python setup.py sdist upload -r pypitest`` to release a
   test version to PyPI's test server
6. Run ``pip install -i https://testpypi.python.org/pypi mediacloud``
   somewhere and then use it with Python to make sure the test release
   works.
7. When you're ready to push to pypi run
   ``python setup.py sdist upload -r pypi``
8. Run ``pip install mediacloud`` somewhere and then try it to make sure
   it worked.

Version History
---------------

-  **v2.53.0**: add random\_seed option to wordCount call
-  **v2.52.0**: added new topicSnapshotWord2VecModel endpoint
-  **v2.51.0**: added sort options to mediaList
-  **v2.50.0**: added profiling timing at debug log level
-  **v2.49.0**: fix return value in ``topicReset``
-  **v2.48.0**: add dangerous ``topicReset`` function
-  **v2.47.0**: add labelled metadata to story list results
-  **v2.46.0**: add labelled metadata to media list and media results
-  **v2.45.0**: add new ``max_stories`` param to topic read, create and
   update endpoints
-  **v2.44.0**: add new ``storyIsSyndicatedFromAP`` endpoint and tests
-  **v2.43.3**: fix source suggestion collection support
-  **v2.43.2**: fix raw story detail cliff and nytlabels endpoints
-  **v2.43.1**: make JSON posts py3 compatible
-  **v2.43.0**: topicList limit option, story-update endpoint, remove
   story coreNLP support, remove sentence-level tagging
-  **v2.42.0**: add is\_logogram option to topic creation and updating
-  **v2.41.0**: updates to topic stories and media sorting, and
   ngram\_size param to word count endpoints
-  **v2.40.1**: auth api fixes
-  **v2.40.0**: add support for listing topics by name, or by if they
   are public or not
-  **v2.39.2**: work on feed-related calls
-  **v2.39.1**: fix topicMediaList to accept q as a param
-  **v2.39.0**: new user reg endpoints, handle unicode in GET queries
   better
-  **v2.38.2**: don't default wordcount to English
-  **v2.38.1**: fix bug in mediaSuggestionsMark for approving media
   suggestions
-  **v2.38.0**: add topic media map support
-  **v2.37.0**: media source feed scraping, topic create/update,
   snapshot generate, mediaUpdate change
-  **v2.36.2**: fixed defaults on updateTag
-  **v2.36.1**: fixed system stats endpoint
-  **v2.36.0**: added mediaSuggest workflow endpoints
-  **v2.35.6**: mediaCreate fixes, storyList feed support
-  **v2.35.5**: create media fixes
-  **v2.35.4**: create collection fixes
-  **v2.35.3**: fixes to clear\_others support in tag\* calls
-  **v2.35.2**: fixes to updateMedia
-  **v2.35.1**: fixes to createTagSet
-  **v2.35.0**: tons of new source-related endpoints
-  **v2.34.0**: new permissons endpoints
-  **v2.33.1**: move topic endpoints to standard client so users can run
   them
-  **v2.33.0**: lots of new api endpoints for topic management
-  **v2.32.0**: fix links in topicStoryList and topicMediaList
-  **v2.31.0**: migrate dumpsList and timesliceList to snapshotList and
   timespanList
-  **v2.30.0**: migrate controversyList and controversy to topicList and
   topic
-  **v2.29.1**: fixes to topicWordCount method return value
-  **v2.29.0**: add topicSentenceCount, and paging for topicMediaList &
   topicStoriesList endpoints
-  **v2.28.0**: add storyWordMatrix, support long queries via POST
   automatically
-  **v2.27.0**: first topic endpoints
-  **v2.26.1**: chunk sentence tag calls to avoid URI length limit in
   PUT requests
-  **v2.26.0**: add storyCount endpoint, cleanup some failing test cases
-  **v2.25.0**: add mediaHealth endpoint, support ``ap_stories_id`` flag
   in storiesList, fix ``controversy_dump_time_slices`` endpoint, remove
   mediaSet and Dashboard endpoints
-  **v2.24.1**: fixes tab/spaces bug
-  **v2.24.0**: adds new params to the ``mediaList`` query (searching by
   controversy, solr query, tags\_id, etc)
-  **v2.23.0**: adds solr date generation helpers
-  **v2.22.2**: fixes the PyPI readme
-  **v2.22.1**: moves ``sentenceList`` to the admin client, preps for
   PyPI release
-  **v2.22.0**: adds the option to enable ``all_fields`` at the API
   client level (ie. for all requests)
