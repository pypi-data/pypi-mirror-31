=====
Usage
=====

Authenticating
--------------

minds-cli supports user authentication and profile management::

    Options:
      -u TEXT             username of minds channel
      -p TEXT             password of minds channel
      --proxy TEXT        proxy for minds requests
      -c, --profile TEXT  load local profile config

Profiles are saved by default in ``$XDG_CONFIG/minds`` directory when authentication is successful.

For example, your first post would be::

    minds -u "username" -p "password" post newsfeed "hello world, posting from api!"

Afterwards you can load your config through ``-c`` command:

    minds -c username post newsfeed "hello world, posting from api AGAIN!"


Posting
-------

minds-cli ``post`` commands can take message from 3 sources:

1. command line argument, e.g. ``minds post newsfeed "my message"``
2. through local editor (will use $EDITOR env variable). This is default if cli argument is not supplied
3. stdin - allows multiline stdin input:
4. file - reads contents from file

Reading
-------

minds-cli supports basic formatted terminal output for reading posts, comments and notifications;

e.g.::

    $ minds newsfeed channel tinarg
    Working from Chiang Mai, Thailand this month!
    Got a condo with this view, pool and a gym for 400€ per month.
    Pretty lovely place so far!

    #chiangmai #thailand #digitalnomad #workspaceview
    https://www.minds.com/fs/v1/thumbnail/825548664578514944
    ―――tinarg―――4/0――――――――――――――――――――――https://minds.com/newsfeed/825549491984670720―――――――――――――――――――――――C:0―――R:0―――
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


