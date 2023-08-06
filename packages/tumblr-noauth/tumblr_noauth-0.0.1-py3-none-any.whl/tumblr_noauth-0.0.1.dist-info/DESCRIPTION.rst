# Tumblr with no OAuth

TL;DR: `tumblr_noauth` is a Python package which provides a
`TumblrSession(email, password)` class which extends
[`requests.Session`][session] and provides a Tumblr login/logout process.

Tumblr supplies an [OAuth API][api] which you can use for fairly simple tasks,
mostly for **dashboard-like functions**; there’s a lot left out, such as

* Checking if a URL is available for creating a new blog; the endpoint at
  `www.tumblr.com/check_if_tumblelog_name_is_available` requires authentication
* Probably others which I forget

With no official way to access that data, `tumblr_noauth` provides a workaround:
emulate a whole Tumblr “session”; you feed it a username and password (which
**aren’t stored, even in the `TumblrSession` object,** and it performs a login
request (and a logout request with `__exit__`).

Under the hood, a `TumblrSession` is a [`requests.Session`][session] with some
special behavior optimized for use with Python’s [`with` statements][with].

The following methods in a `TumblrSession` object are specialized to make the
`https://www.tumblr.com/` prefix optional:

* `delete`
* `get`
* `head`
* `options`
* `patch`
* `post`
* `put`

i.e. the high-level HTTP requests.

Example usage:

    import json
    import tumblr_noauth

    with open('creds.json') as f:
        creds = json.load(f)

    with TumblrSession(creds['email'], creds['password']) as session:
        data = {'name': staff}
        resp = session.post('check_if_tumblelog_name_is_available',
        data=data)

        print(resp, ';', resp.text)

Where the `with` clause automatically logs in and out of Tumblr.

For additional “authenticity”, you might want to set your headers to something
like...

    # this is lying
    headers = {
        'Host': 'www.tumblr.com',
        'Origin': 'https://www.tumblr.com',
        'Referer': 'https://www.tumblr.com/dashboard',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

[requests]: http://docs.python-requests.org/en/master/
[session]: http://docs.python-requests.org/en/master/api/#request-sessions
[api]: https://www.tumblr.com/docs/en/api/v2
[with]: https://docs.python.org/3/reference/compound_stmts.html#the-with-statement


