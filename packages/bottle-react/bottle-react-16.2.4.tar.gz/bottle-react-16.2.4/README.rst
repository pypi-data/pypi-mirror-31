.. figure:: https://user-images.githubusercontent.com/2049665/34214474-37c285c6-e568-11e7-963e-407533d01d80.png
   :alt: image

   image

Bottle-React
============

***NOW SUPPORTS FLASK!*** See
`examples/hello\_world/run\_flask.py <examples/hello_world/run_flask.py>`__.

Description
-----------

This library allows you to return react components from either Bottle or
Flask. Originally created for https://www.hvst.com/.

Example (Hello World)
---------------------

Assume you have a normal JSX file ``hello_world.jsx``:

.. code:: js

    var HelloWorld = React.createClass({
      render: function() {
        return (
          <div className='hello_world'>
            <h1>Hello {this.props.name}!</h1>
            <div>
              Thanks for trying bottle-react!
            </div>
          </div>
        );
      }
    })
    bottlereact._register('HelloWorld', HelloWorld)

And some python code:

.. code:: python

    app = bottle.Bottle()
    br = BottleReact(app)

    @app.get('/')
    def root():
      return br.render_html(
        br.HelloWorld({'name':'World'})
      )

When your route is called the react component will be rendered. See
`examples/hello\_world <examples/hello_world>`__ for details.

Principles
----------

Why did we develop this? We had several goals:

-  [x] Don't cross-compile javascript during development.

Compiling with ``webpack`` is too slow for non-trivial applications.
(One of the niceties about web developement it ``alt-Tab``/``ctrl-R`` to
see your changes.) And it causes too many subtle bugs between dev and
prod that waste developer resources.

-  [x] Don't merge all javascript into one ginormous bundle.

Making your user download a 1.5Mb ``kitchensink.min.js`` every
deployment is horrible. And 99% of it isn't used on most pages. Loading
40kb total from multiple resources with HTTP keep-alive takes just a few
ms per file and is much faster in practice.

-  [x] React components should be composable from Python.

A lot of our routes look like this:

.. code:: python

    @app.get('/something')
    def something():
      user = bottle.request.current_user
      return br.render_html(
        br.HvstApp({'user':user.to_dict()}, [
          br.HelloWorld({'name':user.name}),
        ])
      )

The React component ``HvstApp`` (which renders the title bar and left
nav) is taking two parameters. The first is a ``dict`` that will be
passed as the JSON props to the React component. The second is a
``list`` that will become the children. This list can (and usually does)
contain other React components.

Install
-------

.. code:: python

    sudo pip install bottle-react

NGINX Integration
-----------------

By default (in production mode) ``bottle-react`` writes to
``/tmp/bottlereact/hashed-assets/``. To make NGINX serve these files
directly, use the following:

::

      location ^~ /__br_assets__/ {
        alias /tmp/bottlereact/hashed-assets/;
        expires max;
      }

Server Side Rendering
---------------------

To use server side rendering, please install the npm package
```node-jsdom`` <https://www.npmjs.com/package/node-jsdom>`__ with:

::

    $ sudo npm install -g node-jsdom

Then pass either ``True`` or a callable into the ``render_server``
parameter. For example:

.. code:: python

    def render_server():
      ua = bottle.request.environ.get('HTTP_USER_AGENT')
      return util.is_bot(ua)

BTW... Before enabling it for everyone, run some benchmarks. We find
that it has very little impact on total page load time, at a
considerable CPU expense and double the downloaded HTML size. So we only
do it for search bots (as you can see in the example above).

You will also likely have to shim some missing browser features. At
minimum, React likes to put itself under ``window`` when run inside
``nodejs``, so we have:

.. code:: javascript

    // react in nodejs will put itself under window
    if(typeof React == 'undefined') {
      React = window.React;
    }

In our ``application.js``, since all our code expects it to be a global.
Likewise, for things ``node-jsdom`` hasn't yet implemented, you'll
likely find a few checks are needed, like:

.. code:: javascript

    if (typeof DOMParser=='undefined') {
      // i guess we're not using DOMParser inside nodejs...
    }

Documentation
-------------

See the `full documentation <DOCS.md>`__.
