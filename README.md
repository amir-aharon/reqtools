# reqtools

[![License](https://img.shields.io/github/license/amir-aharon/reqtools)](https://github.com/amir-aharon/reqtools/blob/main/LICENSE)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Code style](https://img.shields.io/badge/code%20style-black-black)

reqtools is a super simple ipython extension that allows you to pretty-print HTTP responses and convert between requests code and curl commands.

## installation

```bash
pip install magic-reqtools
```

manually loading:

```ipython
# Inside an IPython shell
%load_ext reqtools
```

Automatic loading:

```bash
echo "c.InteractiveShellApp.extensions = ['reqtools']" > ~/.ipython/profile_default/ipython_config.py
```

## Usage

```ipython
# Load the extension
In [1]: %load_ext reqtools

# `curl` magic
In [2]: %curl https://www.affirmations.dev/
Out[2]: <Response [200]>

In [3]: response = _

# `res` magic
In [4]: %res response
================================================================================
Status: 200 OK
URL:    https://www.affirmations.dev/
--------------------------------------------------------------------------------
Headers:
  Content-Length: 54
  Content-Type: application/json; charset=utf-8
  ...
--------------------------------------------------------------------------------
Body:
{
  "affirmation": "Your mind is full of brilliant ideas"
}
================================================================================
Out[4]: <Response [200]>

# `req` magic
In [5]: %req response.request
================================================================================
Method: GET
URL:    https://www.affirmations.dev/
--------------------------------------------------------------------------------
Headers:
  User-Agent: python-requests/2.32.5
  Accept-Encoding: gzip, deflate
  Accept: */*
  Connection: keep-alive
--------------------------------------------------------------------------------
Body:
  <empty>
================================================================================
Out[5]: <PreparedRequest [GET]>

In [6]: response_body = json.loads(bytes.decode(response.content))

# `jq` magic (add `-q` for quiet)
In [7]: %jq response_body .affirmation
"Your mind is full of brilliant ideas"
Out[7]: 'Your mind is full of brilliant ideas'

In [8]: %jq -q response_body .affirmation
Out[8]: 'Your mind is full of brilliant ideas'
```
