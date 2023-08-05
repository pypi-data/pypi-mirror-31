=================================
August - a html-to-text converter
=================================

|pipeline-badge| |coverage-badge| |pypi-badge|


August is an html to text converter specifically intended for producing
text versions of HTML emails.


Getting Started
---------------

Install using PIP ::

    $ pip3 install august

Then, import it and run convert ::

    >>> import august
    >>>
    >>> html = '<p>I\'m <em>so</em> excited to try this</p>'
    >>> print(august.convert(html, width=20))
    I'm /so/ excited to
    try this

Known issues
------------

1. There's a few tags that are still not yet supported (which could
   benefit from some support) like <pre>, <var>, <tt>, and probably
   a bunch that I forgot. These are not commonly seen in emails so they
   are not high priority
2. There's no CSS support currently. Some support will probably happen
   sometime, but it's still unclear what is worth implementing.

Alternatives
------------

* html2text_: Coverts HTML into markdown, and supports a bazillion options.
  It's a great project if you want to produce markdown; but markdown, because
  it's designed to be turned into HTML, has a little more noise than is
  strictly necessary, and the header formatting is pretty unclear.
* html-to-text_: Converts HTML to text. Javascript/node project.


.. _html2text: https://pypi.org/project/html2text/
.. _html-to-text: https://www.npmjs.com/package/html-to-text


.. |pipeline-badge| image:: https://gitlab.com/alantrick/august/badges/master/pipeline.svg
   :target: https://gitlab.com/alantrick/august/
   :alt: Build Status

.. |coverage-badge| image:: https://gitlab.com/alantrick/august/badges/master/coverage.svg
   :target: https://gitlab.com/alantrick/august/
   :alt: Coverage Status

.. |pypi-badge| image:: https://img.shields.io/pypi/v/august.svg
   :target: https://pypi.org/project/august/
   :alt: Project on PyPI

