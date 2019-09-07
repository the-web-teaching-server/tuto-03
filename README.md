# Tutorial 03 - Url shortener

This tutorial aims to produce an URL shortener service like [bitly.com]([http://bitly.com). We are using
[Flask](http://flask.pocoo.org/), a "micro-framework" in Python to handle most of the machinery needed
for the web.

1. Make the name of the project as short as possible (all one letter names seem to be taken on Glitch; you may have a chance with a two-letter name.).

**Note:** the "Show > next to the code" feature is a bit buggy in Glit when dealing
with redirections. You should use "Show > in a new window" instead.

## A bit of Python

Before we start, if you are not familiar with this concept,
read **the first part** of [this article on keyword arguments
in Python](https://treyhunner.com/2018/04/keyword-arguments-in-python/#What_are_keyword_arguments?),  since Flask uses it a lot.

## Create new shortcuts

1. Browse to the files `server.py`, `tempates/index.html` and `templates/layout.html`.
   * What is their roles?
   * How do we pass data from the server to the templates?
   * Does `{{ ... }}` and `{% ... %}` belong to HTML? What are their role?
   * With the `/demo/` route, can we perform the attack described at the end of
     [the lecture's slides](https://slides.com/sebbes/http-communication)?
1. Modify the home page to display a form with `method=POST`, `action=/new-shortcut`,
   containing a text field named `url` and a submit button.
1. Add a handler in the server which catches the `POST` requests on the `/new-shortcut` route.
   This handler will:
   * get the url sent by the user: you will need to use `request.form` (`request` has to be imported from the `flask` module),
   * generate a new key for this key (use the given function!),
   * add the key/url in the `SHORTCUTS` dict,
   * send the new key back as raw text.
1. Directly answering to a `POST` request
   is not great: if the user refreshes the page (e.g. with "F5"),
   the POST request will be played again, creating a new ressource. The correct process is to redirect the browser to a GET request.
   Hence:
   * create a handler catching `GET` requests on the `/view-key/<key>` route. This
     handler will get the corresponding URL to the given key and render a template
     displaying this association (eg. "The key EbA356Ak redirects to http://www.example.com").
     The created template should extend `layout.html`.
   * At the end to the `POST` handler created at the previous step, use the `flask.redirect` function
     to redirect the user to the `/view-key/<key>` (with `<key>` replaced by the generated key).
1. Make it possible to come back to the home page from any page of your site: modify the
   `layout.html` to add a link on the `<h1>` title.
1. Keep in mind that the requests are "user input". So you CANNOT suppose the request is correctly formed.
   For instance, what is happening if the `url` parameter is missing in a request to `/new-shortcut`?
   Try to spot all the places where things can go wrong and handle all possible cases.

   Note:
   you can use the following structure when searching data in a dictionary:
   ```python
   try:
     value = dico[key]
     launch_rocket(value)
   except KeyError:
     # handle the case if the key does not exist.
   ```
   You can add a template named `error.html` waiting a `message` as parameter.
   For instance if the `url` parameter is missing in the request for creating
   a shortcut, you can:
   ```python
   return render_template("error.html", message="The 'url' parameter is missing!"), 400
   ```
   The number after the comma is the HTTP code for `Bad request`. You may also need
   the code `404 Not Found` for other handlers.

## Perform the redirection

1. Create a handler `/r/<key>` which actually redirects the requests to the destination.
   Name the function `redir`.
   This route should simply look in the `SHORTCUTS` dict and return a redirection.
1. Now, you just have to show a copyable link to your users. Flask provides an easy way
   to do this: in the `view-key.html` template, you can use the following
   snippet:
   ```jinja2
   {{ url_for('redir', key=key, _external=True) }}
   ```
   Note: inside `{{ ... }}` you can write almost any Python expression you want.
   The previous one is simply a function call (`url_for` is a function defined by Flask).


## Search the urls

We will enable  the users to search over all the shortened links.

1. In the home page, create a `GET`-form with a text field named `query` and a submit button.
1. Catch the request sent by this form in a handler and list all the keys/urls where
   the query is part of the url; store these pairs of key/urls in a list of tuples.

   Note: to check if a string `s1` is a substring of another string `s2` we can
   use:
   ```python
   s1 in s2
   ```
   wich will return a boolean.
1. You can perform loops and conditionnal branching in the templates with the following Jinja tags,
   for example:
    ```jinja2
    <ul>
    {% for element in list %}
      <li>{{ element }}</li>
    {% endfor %}
    </ul>

    {% if condition %}
       The condition is <em>true</em>!
    {% else %}
       The condition is <em>false</em>!
    {% endif %}
    ```
    Use those tags to show the key and the corresponding
    url for each search result. You may also display "no result :(" if there are not any results!

## Use a database

Storing the shortcuts in the `SHORTCUTS` global variable is fine for toy applications but it should never be used
in production:
* data is deleted every time the server restarts (it happens for instance when you modify the source code on Glitch),
* each request runs in its own thread; if two simultaneous requests write data in `SHORTCUTS` at the same time,
  it can mess up the internal structure of `SHORTCUTS` thus make it unusable.

Instead, we will use a SQL database. For the sake of simplicity, we will use SQLite3 which is natively
supported in Python. Once again, this tool is not the best fit for "real applications" with regards
to performance, but it solves the two above issues and should be sufficient for the projects you will
develop in the course.

In SQLite, a database is a simple file. We will name it `.data/shortcuts.db` and it will contain only one table `shortcuts`.
The `.data` folder is a special one in Glitch: its content will not be available from other users, and it will
not be copied when the app is "remixed".


This part will mainly consist in observing existing code and understanding how it works.

1. Copy-paste this code in a file named `db_init.py`:
    ```python
    import sqlite3

    conn = sqlite3.connect('.data/shortcuts.db')
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS shortcuts')

    cur.execute('''
    CREATE TABLE shortcuts
    (key TEXT PRIMARY KEY, url TEXT)''')

    print("Table created!")

    cur.execute('INSERT INTO shortcuts VALUES (?, ?), (?, ?) ',
                ('EbA356Ak', "http://www.example.com", 'aoM4apKh', "http://www.mozilla.org")
    )

    conn.commit()


    cur.execute("SELECT key, url FROM shortcuts")

    print("Fake data inserted:")
    for key, url in cur.fetchall():
      print(key, "->", url)

    conn.close()
    ```
    * What is the structure of the created table?
    * How many lines do we insert in this table?
    * What does the `cur.commit()` statement achieve?
    * What is the role of the `?` in the `INSERT TO` SQL command? In a
      next lecture, we will see WHY we should not use naive string interpolation
      like `.format(...)`.
1. The script you have pasted is not executed by default, you have
     to manually run it (which is preferable:
     we do not want to erase the whole database every time the app starts).
     Open the glitch console (`Tools > Logs > Console` or `Tools > Full page console`)
     and run `python3 db_init.py`.Then, you can launch `sqlite3 .data/shortcuts.db`:
     you can type SQL commands like `SELECT * FROM shortcuts;` (do not forget the
     ending `;`!).
1. [Inspect the server code of the solution](https://glitch.com/edit/#!/eh?path=server.py) (or
   copy-paste the `server.py` in your `server.py`). For each handler, read the corresponding
   code. You should be able to understand the role of:
   * `cur.execute(...)`,
   * `cur.fetchone()`,
   * `cur.fetchall()`,
   * `db.commit()` (note that we are commiting on the "database" and not on the "cursor").

