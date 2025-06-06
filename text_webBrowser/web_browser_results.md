# Visiting Python.org
Address: https://python.org
Title: Welcome to Python.org
Viewport position: Showing page 1 of 2.
=======================


**Notice:** While JavaScript is not essential for this website, your interaction with the content will be limited. Please turn JavaScript on for the full experience.

[Skip to content](#content "Skip to content")

[▼ Close](#python-network)

* [Python](/ "The Python Programming Language")
* [PSF](https://www.python.org/psf/ "The Python Software Foundation")
* [Docs](https://docs.python.org "Python Documentation")
* [PyPI](https://pypi.org/ "Python Package Index")
* [Jobs](/jobs/ "Python Job Board")
* [Community](/community/)

[▲ The Python Network](#top)

# [python™](/)

[Donate](https://psfmember.org/civicrm/contribute/transact?reset=1&id=2)
[≡ Menu](#site-map)

Search This Site

GO

* **A A**
  + Smaller
  + Larger
  + Reset

* Socialize
  + [LinkedIn](https://www.linkedin.com/company/python-software-foundation/)
  + [Mastodon](https://fosstodon.org/%40ThePSF)
  + [Chat on IRC](/community/irc/)
  + [Twitter](https://twitter.com/ThePSF)

* [About](/about/)
  + [Applications](/about/apps/)
  + [Quotes](/about/quotes/)
  + [Getting Started](/about/gettingstarted/)
  + [Help](/about/help/)
  + [Python Brochure](http://brochure.getpython.info/)
* [Downloads](/downloads/)
  + [All releases](/downloads/)
  + [Source code](/downloads/source/)
  + [Windows](/downloads/windows/)
  + [macOS](/downloads/macos/)
  + [Other Platforms](/download/other/)
  + [License](https://docs.python.org/3/license.html)
  + [Alternative Implementations](/download/alternatives)
* [Documentation](/doc/)
  + [Docs](/doc/)
  + [Audio/Visual Talks](/doc/av)
  + [Beginner's Guide](https://wiki.python.org/moin/BeginnersGuide)
  + [Developer's Guide](https://devguide.python.org/)
  + [FAQ](https://docs.python.org/faq/)
  + [Non-English Docs](http://wiki.python.org/moin/Languages)
  + [PEP Index](https://peps.python.org)
  + [Python Books](https://wiki.python.org/moin/PythonBooks)
  + [Python Essays](/doc/essays/)
* [Community](/community/)
  + [Diversity](/community/diversity/)
  + [Mailing Lists](/community/lists/)
  + [IRC](/community/irc/)
  + [Forums](/community/forums/)
  + [PSF Annual Impact Report](/psf/annual-report/2021/)
  + [Python Conferences](/community/workshops/)
  + [Special Interest Groups](/community/sigs/)
  + [Python Logo](/community/logos/)
  + [Python Wiki](https://wiki.python.org/moin/)
  + [Code of Conduct](/psf/conduct/)
  + [Community Awards](/community/awards)
  + [Get Involved](/psf/get-involved/)
  + [Shared Stories](/psf/community-stories/)
* [Success Stories](/success-stories/ "success-stories")
  + [Arts](/success-stories/category/arts/)
  + [Business](/success-stories/category/business/)
  + [Education](/success-stories/category/education/)
  + [Engineering](/success-stories/category/engineering/)
  + [Government](/success-stories/category/government/)
  + [Scientific](/success-stories/category/scientific/)
  + [Software Development](/success-stories/category/software-development/)
* [News](/blogs/ "News from around the Python world")
  + [Python News](/blogs/ "Python Insider Blog Posts")
  + [PSF Newsletter](/psf/newsletter/ "Python Software Foundation Newsletter")
  + [PSF News](http://pyfound.blogspot.com/ "PSF Blog")
  + [PyCon US News](http://pycon.blogspot.com/ "PyCon Blog")
  + [News from the Community](http://planetpython.org/ "Planet Python")
* [Events](/events/)
  + [Python Events](/events/python-events/)
  + [User Group Events](/events/python-user-group/)
  + [Python Events Archive](/events/python-events/past/)
  + [User Group Events Archive](/events/python-user-group/past/)
  + [Submit an Event](https://wiki.python.org/moin/PythonEventsCalendar#Submitting_an_Event)

* [>\_
  Launch Interactive Shell](/shell/)

* ```
  # Python 3: Fibonacci series up to n
  >>> def fib(n):
  >>>     a, b = 0, 1
  >>>     while a < n:
  >>>         print(a, end=' ')
  >>>         a, b = b, a+b
  >>>     print()
  >>> fib(1000)
  0 1 1 2 3 5 8 13 21 34 55 89 144 233 377 610 987
  ```

  # Functions Defined

  The core of extensible programming is defining functions. Python allows mandatory and optional arguments, keyword arguments, and even arbitrary argument lists. [More about defining functions in Python 3](//docs.python.org/3/tutorial/controlflow.html#defining-functions)
* ```
  # Python 3: List comprehensions
  >>> fruits = ['Banana', 'Apple', 'Lime']
  >>> loud_fruits = [fruit.upper() for fruit in fruits]
  >>> print(loud_fruits)
  ['BANANA', 'APPLE', 'LIME']

  # List and the enumerate function
  >>> list(enumerate(fruits))
  [(0, 'Banana'), (1, 'Apple'), (2, 'Lime')]
  ```

  # Compound Data Types

  Lists (known as arrays in other languages) are one of the compound data types that Python understands. Lists can be indexed, sliced and manipulated with other built-in functions. [More about lists in Python 3](//docs.python.org/3/tutorial/introduction.html#lists)
* ```
  # Python 3: Simple arithmetic
  >>> 1 / 2
  0.5
  >>> 2 ** 3
  8
  >>> 17 / 3  # classic division returns a float
  5.666666666666667
  >>> 17 // 3  # floor division
  5
  ```

  # Intuitive Interpretation

  Calculations are simple with Python, and expression syntax is straightforward: the operators `+`, `-`, `*` and `/` work as expected; parentheses `()` can be used for grouping. [More about simple math functions in Python 3](http://docs.python.org/3/tutorial/introduction.html#using-python-as-a-calculator).
* ```
  # For loop on a list
  >>> numbers = [2, 4, 6, 8]
  >>> product = 1
  >>> for number in numbers:
  ...    product = product * number
  ...
  >>> print('The product is:', product)
  The product is: 384
  ```

  # All the Flow You’d Expect

  Python knows the usual control flow statements that other languages speak — `if`, `for`, `while` and `range` — with some of its own twists, of course. [More control flow tools in Python 3](//docs.python.org/3/tutorial/controlflow.html)
* ```
  # Simple output (with Unicode)
  >>> print("Hello, I'm Python!")
  Hello, I'm Python!
  # Input, assignment
  >>> name = input('What is your name?\n')
  What is your name?
  Python
  >>> print(f'Hi, {name}.')
  Hi, Python.

  ```

  # Quick & Easy to Learn

  Experienced programmers in any other language can pick up Python very quickly, and beginners find the clean syntax and indentation structure easy to learn. [Whet your appetite](//docs.python.org/3/tutorial/) with our Python 3 overview.

Python is a programming language that lets you work quickly and integrate systems more effectively. [Learn More](/doc/)

## Get Started

Whether you're new to programming or an experienced developer, it's easy to learn and use Python.

[Start with our Beginner’s Guide](/about/gettingstarted/)

## Download

Python source code and installers are available for download for all versions!

Latest: [Python 3.13.2](/downloads/release/python-3132/)

## Docs

Documentation for Python's standard library, along with tutorials and guides, are available online.

[docs.python.org](https://docs.python.org)

## Jobs

Looking for work or have a Python related position that you're trying to hire for? Our **relaunched community-run job board** is the place to go.

[jobs.python.org](//jobs.python.org)

## Latest News

[More](https://blog.python.org "More News")

* 2025-02-04
  [Python 3.13.2 and 3.12.9 now available!](https://pythoninsider.blogspot.com/2025/02/python-3132-and-3129-now-available.html)
* 2025-01-15
  [PSF Newsletter: Awards, Grants, & PyCon US 2025!](https://mailchi.mp/python/python-software-foundation-july-2024-newsletter-19875956)
* 2025-01-14
  [Python 3.14.0 alpha 4 is out](https://pythoninsider.blogspot.com/2025/01/python-3140-alpha-4-is-out.html)
* 2025-01-14
  [Powering Python together in 2025, thanks to our community!](https://pyfound.blogspot.com/2025/01/powering-python-together-in-2025-thanks.html)
* 2024-12-19
  [PSF Grants: Program & Charter Updates (Part 2)](https://pyfound.blogspot.com/2024/12/psf-grants-program-charter-updates-part-2.html)

## Upcoming Events

[More](/events/calendars/ "More Events")

* 2025-02-08
  [PyCascades 2025](/events/python-events/1890/)
* 2025-02-15
  [Python Barcamp Karlsruhe 2025](/events/python-user-group/1841/)
* 2025-02-21
  [Django Girls Koforidua](/events/python-user-group/1868/)



## Finding 'Python' on the page
Address: https://python.org
Title: Welcome to Python.org
Viewport position: Showing page 1 of 2.
=======================


**Notice:** While JavaScript is not essential for this website, your interaction with the content will be limited. Please turn JavaScript on for the full experience.

[Skip to content](#content "Skip to content")

[▼ Close](#python-network)

* [Python](/ "The Python Programming Language")
* [PSF](https://www.python.org/psf/ "The Python Software Foundation")
* [Docs](https://docs.python.org "Python Documentation")
* [PyPI](https://pypi.org/ "Python Package Index")
* [Jobs](/jobs/ "Python Job Board")
* [Community](/community/)

[▲ The Python Network](#top)

# [python™](/)

[Donate](https://psfmember.org/civicrm/contribute/transact?reset=1&id=2)
[≡ Menu](#site-map)

Search This Site

GO

* **A A**
  + Smaller
  + Larger
  + Reset

* Socialize
  + [LinkedIn](https://www.linkedin.com/company/python-software-foundation/)
  + [Mastodon](https://fosstodon.org/%40ThePSF)
  + [Chat on IRC](/community/irc/)
  + [Twitter](https://twitter.com/ThePSF)

* [About](/about/)
  + [Applications](/about/apps/)
  + [Quotes](/about/quotes/)
  + [Getting Started](/about/gettingstarted/)
  + [Help](/about/help/)
  + [Python Brochure](http://brochure.getpython.info/)
* [Downloads](/downloads/)
  + [All releases](/downloads/)
  + [Source code](/downloads/source/)
  + [Windows](/downloads/windows/)
  + [macOS](/downloads/macos/)
  + [Other Platforms](/download/other/)
  + [License](https://docs.python.org/3/license.html)
  + [Alternative Implementations](/download/alternatives)
* [Documentation](/doc/)
  + [Docs](/doc/)
  + [Audio/Visual Talks](/doc/av)
  + [Beginner's Guide](https://wiki.python.org/moin/BeginnersGuide)
  + [Developer's Guide](https://devguide.python.org/)
  + [FAQ](https://docs.python.org/faq/)
  + [Non-English Docs](http://wiki.python.org/moin/Languages)
  + [PEP Index](https://peps.python.org)
  + [Python Books](https://wiki.python.org/moin/PythonBooks)
  + [Python Essays](/doc/essays/)
* [Community](/community/)
  + [Diversity](/community/diversity/)
  + [Mailing Lists](/community/lists/)
  + [IRC](/community/irc/)
  + [Forums](/community/forums/)
  + [PSF Annual Impact Report](/psf/annual-report/2021/)
  + [Python Conferences](/community/workshops/)
  + [Special Interest Groups](/community/sigs/)
  + [Python Logo](/community/logos/)
  + [Python Wiki](https://wiki.python.org/moin/)
  + [Code of Conduct](/psf/conduct/)
  + [Community Awards](/community/awards)
  + [Get Involved](/psf/get-involved/)
  + [Shared Stories](/psf/community-stories/)
* [Success Stories](/success-stories/ "success-stories")
  + [Arts](/success-stories/category/arts/)
  + [Business](/success-stories/category/business/)
  + [Education](/success-stories/category/education/)
  + [Engineering](/success-stories/category/engineering/)
  + [Government](/success-stories/category/government/)
  + [Scientific](/success-stories/category/scientific/)
  + [Software Development](/success-stories/category/software-development/)
* [News](/blogs/ "News from around the Python world")
  + [Python News](/blogs/ "Python Insider Blog Posts")
  + [PSF Newsletter](/psf/newsletter/ "Python Software Foundation Newsletter")
  + [PSF News](http://pyfound.blogspot.com/ "PSF Blog")
  + [PyCon US News](http://pycon.blogspot.com/ "PyCon Blog")
  + [News from the Community](http://planetpython.org/ "Planet Python")
* [Events](/events/)
  + [Python Events](/events/python-events/)
  + [User Group Events](/events/python-user-group/)
  + [Python Events Archive](/events/python-events/past/)
  + [User Group Events Archive](/events/python-user-group/past/)
  + [Submit an Event](https://wiki.python.org/moin/PythonEventsCalendar#Submitting_an_Event)

* [>\_
  Launch Interactive Shell](/shell/)

* ```
  # Python 3: Fibonacci series up to n
  >>> def fib(n):
  >>>     a, b = 0, 1
  >>>     while a < n:
  >>>         print(a, end=' ')
  >>>         a, b = b, a+b
  >>>     print()
  >>> fib(1000)
  0 1 1 2 3 5 8 13 21 34 55 89 144 233 377 610 987
  ```

  # Functions Defined

  The core of extensible programming is defining functions. Python allows mandatory and optional arguments, keyword arguments, and even arbitrary argument lists. [More about defining functions in Python 3](//docs.python.org/3/tutorial/controlflow.html#defining-functions)
* ```
  # Python 3: List comprehensions
  >>> fruits = ['Banana', 'Apple', 'Lime']
  >>> loud_fruits = [fruit.upper() for fruit in fruits]
  >>> print(loud_fruits)
  ['BANANA', 'APPLE', 'LIME']

  # List and the enumerate function
  >>> list(enumerate(fruits))
  [(0, 'Banana'), (1, 'Apple'), (2, 'Lime')]
  ```

  # Compound Data Types

  Lists (known as arrays in other languages) are one of the compound data types that Python understands. Lists can be indexed, sliced and manipulated with other built-in functions. [More about lists in Python 3](//docs.python.org/3/tutorial/introduction.html#lists)
* ```
  # Python 3: Simple arithmetic
  >>> 1 / 2
  0.5
  >>> 2 ** 3
  8
  >>> 17 / 3  # classic division returns a float
  5.666666666666667
  >>> 17 // 3  # floor division
  5
  ```

  # Intuitive Interpretation

  Calculations are simple with Python, and expression syntax is straightforward: the operators `+`, `-`, `*` and `/` work as expected; parentheses `()` can be used for grouping. [More about simple math functions in Python 3](http://docs.python.org/3/tutorial/introduction.html#using-python-as-a-calculator).
* ```
  # For loop on a list
  >>> numbers = [2, 4, 6, 8]
  >>> product = 1
  >>> for number in numbers:
  ...    product = product * number
  ...
  >>> print('The product is:', product)
  The product is: 384
  ```

  # All the Flow You’d Expect

  Python knows the usual control flow statements that other languages speak — `if`, `for`, `while` and `range` — with some of its own twists, of course. [More control flow tools in Python 3](//docs.python.org/3/tutorial/controlflow.html)
* ```
  # Simple output (with Unicode)
  >>> print("Hello, I'm Python!")
  Hello, I'm Python!
  # Input, assignment
  >>> name = input('What is your name?\n')
  What is your name?
  Python
  >>> print(f'Hi, {name}.')
  Hi, Python.

  ```

  # Quick & Easy to Learn

  Experienced programmers in any other language can pick up Python very quickly, and beginners find the clean syntax and indentation structure easy to learn. [Whet your appetite](//docs.python.org/3/tutorial/) with our Python 3 overview.

Python is a programming language that lets you work quickly and integrate systems more effectively. [Learn More](/doc/)

## Get Started

Whether you're new to programming or an experienced developer, it's easy to learn and use Python.

[Start with our Beginner’s Guide](/about/gettingstarted/)

## Download

Python source code and installers are available for download for all versions!

Latest: [Python 3.13.2](/downloads/release/python-3132/)

## Docs

Documentation for Python's standard library, along with tutorials and guides, are available online.

[docs.python.org](https://docs.python.org)

## Jobs

Looking for work or have a Python related position that you're trying to hire for? Our **relaunched community-run job board** is the place to go.

[jobs.python.org](//jobs.python.org)

## Latest News

[More](https://blog.python.org "More News")

* 2025-02-04
  [Python 3.13.2 and 3.12.9 now available!](https://pythoninsider.blogspot.com/2025/02/python-3132-and-3129-now-available.html)
* 2025-01-15
  [PSF Newsletter: Awards, Grants, & PyCon US 2025!](https://mailchi.mp/python/python-software-foundation-july-2024-newsletter-19875956)
* 2025-01-14
  [Python 3.14.0 alpha 4 is out](https://pythoninsider.blogspot.com/2025/01/python-3140-alpha-4-is-out.html)
* 2025-01-14
  [Powering Python together in 2025, thanks to our community!](https://pyfound.blogspot.com/2025/01/powering-python-together-in-2025-thanks.html)
* 2024-12-19
  [PSF Grants: Program & Charter Updates (Part 2)](https://pyfound.blogspot.com/2024/12/psf-grants-program-charter-updates-part-2.html)

## Upcoming Events

[More](/events/calendars/ "More Events")

* 2025-02-08
  [PyCascades 2025](/events/python-events/1890/)
* 2025-02-15
  [Python Barcamp Karlsruhe 2025](/events/python-user-group/1841/)
* 2025-02-21
  [Django Girls Koforidua](/events/python-user-group/1868/)



## Scrolling down the page
Address: https://python.org
Title: Welcome to Python.org
Viewport position: Showing page 2 of 2.
=======================
* 2025-02-22
  [PyConf Hyderabad 2025](/events/python-events/1895/)
* 2025-02-22
  [DjangoCongress JP 2025](/events/python-events/1874/)

## Success Stories

[More](/success-stories/ "More Success Stories")

> [Generating realistic location data for users for testing or modeling simulations is a hard problem. Current approaches just create random locations inside a box, placing users in waterways or on top of buildings. This inability to make accurate, synthetic location data stifles a lot of innovative projects that require diverse and complex datasets to fuel their work.](/success-stories/using-python-with-gretelai-to-generate-synthetic-location-data/)

| [Using Python with Gretel.ai to Generate Synthetic Location Data](/success-stories/using-python-with-gretelai-to-generate-synthetic-location-data/) *by Alex Watson, co-founder and CPO, Gretel.ai* |
| --- |

## Use Python for…

[More](/about/apps "More Applications")

* **Web Development**:
  [Django](http://www.djangoproject.com/), [Pyramid](http://www.pylonsproject.org/), [Bottle](http://bottlepy.org), [Tornado](http://tornadoweb.org), [Flask](http://flask.pocoo.org/), [web2py](http://www.web2py.com/)
* **GUI Development**:
  [tkInter](http://wiki.python.org/moin/TkInter), [PyGObject](https://wiki.gnome.org/Projects/PyGObject), [PyQt](http://www.riverbankcomputing.co.uk/software/pyqt/intro), [PySide](https://wiki.qt.io/PySide), [Kivy](https://kivy.org/), [wxPython](http://www.wxpython.org/), [DearPyGui](https://dearpygui.readthedocs.io/en/latest/)
* **Scientific and Numeric**:
  [SciPy](http://www.scipy.org), [Pandas](http://pandas.pydata.org/), [IPython](http://ipython.org)
* **Software Development**:
  [Buildbot](http://buildbot.net/), [Trac](http://trac.edgewall.org/), [Roundup](http://roundup.sourceforge.net/)
* **System Administration**:
  [Ansible](http://www.ansible.com), [Salt](https://saltproject.io), [OpenStack](https://www.openstack.org), [xonsh](https://xon.sh)

## >>> [Python Software Foundation](/psf/)

The mission of the Python Software Foundation is to promote, protect, and advance the Python programming language, and to support and facilitate the growth of a diverse and international community of Python programmers. [Learn more](/psf/)

[Become a Member](/users/membership/)
[Donate to the PSF](/psf/donations/)

[▲ Back to Top](#python-network)

* [About](/about/)
  + [Applications](/about/apps/)
  + [Quotes](/about/quotes/)
  + [Getting Started](/about/gettingstarted/)
  + [Help](/about/help/)
  + [Python Brochure](http://brochure.getpython.info/)
* [Downloads](/downloads/)
  + [All releases](/downloads/)
  + [Source code](/downloads/source/)
  + [Windows](/downloads/windows/)
  + [macOS](/downloads/macos/)
  + [Other Platforms](/download/other/)
  + [License](https://docs.python.org/3/license.html)
  + [Alternative Implementations](/download/alternatives)
* [Documentation](/doc/)
  + [Docs](/doc/)
  + [Audio/Visual Talks](/doc/av)
  + [Beginner's Guide](https://wiki.python.org/moin/BeginnersGuide)
  + [Developer's Guide](https://devguide.python.org/)
  + [FAQ](https://docs.python.org/faq/)
  + [Non-English Docs](http://wiki.python.org/moin/Languages)
  + [PEP Index](https://peps.python.org)
  + [Python Books](https://wiki.python.org/moin/PythonBooks)
  + [Python Essays](/doc/essays/)
* [Community](/community/)
  + [Diversity](/community/diversity/)
  + [Mailing Lists](/community/lists/)
  + [IRC](/community/irc/)
  + [Forums](/community/forums/)
  + [PSF Annual Impact Report](/psf/annual-report/2021/)
  + [Python Conferences](/community/workshops/)
  + [Special Interest Groups](/community/sigs/)
  + [Python Logo](/community/logos/)
  + [Python Wiki](https://wiki.python.org/moin/)
  + [Code of Conduct](/psf/conduct/)
  + [Community Awards](/community/awards)
  + [Get Involved](/psf/get-involved/)
  + [Shared Stories](/psf/community-stories/)
* [Success Stories](/success-stories/ "success-stories")
  + [Arts](/success-stories/category/arts/)
  + [Business](/success-stories/category/business/)
  + [Education](/success-stories/category/education/)
  + [Engineering](/success-stories/category/engineering/)
  + [Government](/success-stories/category/government/)
  + [Scientific](/success-stories/category/scientific/)
  + [Software Development](/success-stories/category/software-development/)
* [News](/blogs/ "News from around the Python world")
  + [Python News](/blogs/ "Python Insider Blog Posts")
  + [PSF Newsletter](/psf/newsletter/ "Python Software Foundation Newsletter")
  + [PSF News](http://pyfound.blogspot.com/ "PSF Blog")
  + [PyCon US News](http://pycon.blogspot.com/ "PyCon Blog")
  + [News from the Community](http://planetpython.org/ "Planet Python")
* [Events](/events/)
  + [Python Events](/events/python-events/)
  + [User Group Events](/events/python-user-group/)
  + [Python Events Archive](/events/python-events/past/)
  + [User Group Events Archive](/events/python-user-group/past/)
  + [Submit an Event](https://wiki.python.org/moin/PythonEventsCalendar#Submitting_an_Event)
* [Contributing](/dev/)
  + [Developer's Guide](https://devguide.python.org/)
  + [Issue Tracker](https://github.com/python/cpython/issues)
  + [python-dev list](https://mail.python.org/mailman/listinfo/python-dev)
  + [Core Mentorship](/dev/core-mentorship/)
  + [Report a Security Issue](/dev/security/)

[▲ Back to Top](#python-network)

* [Help & General Contact](/about/help/)
* [Diversity Initiatives](/community/diversity/)
* [Submit Website Bug](https://github.com/python/pythondotorg/issues)
* [Status](https://status.python.org/)

Copyright ©2001-2025.
 [Python Software Foundation](/psf-landing/)
 [Legal Statements](/about/legal/)
 [Privacy Notice](https://policies.python.org/python.org/Privacy-Notice/)




## Web Search Results for 'Python programming'
Address: google: Python programming
Title: Python programming - Search
Viewport position: Showing page 1 of 1.
=======================
A Google search for 'Python programming' found 7 results:

## Web Results
1. [Welcome to Python.org](https://www.python.org/)
Source: Python.org

The official home of the Python Programming Language.

2. [Introduction to Python](https://www.w3schools.com/python/python_intro.asp)
Source: W3Schools

Python is a popular programming language. It was created by Guido van Rossum, and released in 1991. It is used for:

3. [Python (programming language)](https://en.wikipedia.org/wiki/Python_(programming_language))
Source: Wikipedia

Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.

4. [Python Tutorial | Learn Python Programming Language](https://www.geeksforgeeks.org/python-programming-language-tutorial/)
Date published: Jan 28, 2025
Source: GeeksforGeeks

Python is a versatile and beginner-friendly programming language known for its simplicity, extensive libraries, and wide applications in web ...

5. [Python Courses & Tutorials](https://www.codecademy.com/catalog/language/python)
Source: Codecademy

Python is a general-purpose, versatile, and powerful programming language. It's a great first language because Python code is concise and easy to read.

6. [Learn Python Programming](https://www.programiz.com/python-programming)
Source: Programiz

Python is one of the top programming languages in the world, widely used in fields such as AI, machine learning, data science, and web development.

7. [Python Programming Tutorials](https://pythonprogramming.net/)
Source: PythonProgramming.net

Python Programming tutorials from beginner to advanced on a massive variety of topics. All video and text tutorials are free.


## Archived Version of Python.org from 2010
Web archive for url https://python.org, snapshot taken at date 20100102:
Address: http://web.archive.org/web/20100102215115/http://www.python.org:80/
Title: Python Programming Language -- Official Website
Viewport position: Showing page 1 of 2.
=======================

# [homepage](/web/20100102215115/http%3A//www.python.org/)

[![skip to navigation](/web/20100102215115im_/http://www.python.org/images/trans.gif)](#left-hand-navigation)
[![skip to content](/web/20100102215115im_/http://www.python.org/images/trans.gif)](#content-body)

[Advanced Search](/web/20100102215115/http%3A//www.python.org/search)

* [About](/web/20100102215115/http%3A//www.python.org/about/ "About The Python Language")
* [News](/web/20100102215115/http%3A//www.python.org/news/ "Major Happenings Within the Python Community")
* [Documentation](/web/20100102215115/http%3A//www.python.org/doc/ "Tutorials, Library Reference, C API")
* [Download](/web/20100102215115/http%3A//www.python.org/download/ "Start Running Python Under Windows, Mac, Linux and Others")
* [Community](/web/20100102215115/http%3A//www.python.org/community/ "Mailing Lists, Jobs, Conferences, SIGs, Online Chats")
* [Foundation](/web/20100102215115/http%3A//www.python.org/psf/ "Python Software Foundation")
* [Core Development](/web/20100102215115/http%3A//www.python.org/dev/ "Development of the Python language and website")
* [Links](/web/20100102215115/http%3A//www.python.org/links/ "Pointers to Useful Information")

#### [Help](/web/20100102215115/http%3A//www.python.org/about/help/)

#### [Quick Links (2.6.4)](/web/20100102215115/http%3A//www.python.org/download/releases/2.6.4/)

* [Documentation](http://web.archive.org/web/20100102215115/http%3A//docs.python.org/ "Manuals for Latest Stable Release")
* [Windows Installer](/web/20100102215115/http%3A//www.python.org/ftp/python/2.6.4/python-2.6.4.msi "Easy Installer of Python under Windows")
* [Source Distribution](/web/20100102215115/http%3A//www.python.org/ftp/python/2.6.4/Python-2.6.4.tar.bz2 "Grab the Source for the Latest Stable Release")
* [Package Index](http://web.archive.org/web/20100102215115/http%3A//pypi.python.org/pypi "Community Collection of Shared Python Modules")

#### [Quick Links (3.1.1)](/web/20100102215115/http%3A//www.python.org/download/releases/3.1.1/)

* [Documentation](http://web.archive.org/web/20100102215115/http%3A//docs.python.org/3.1/ "Manual for Python 3.1 Release")
* [Windows Installer](/web/20100102215115/http%3A//www.python.org/ftp/python/3.1.1/python-3.1.1.msi "Easy Installer of Python under Windows")
* [Source Distribution](/web/20100102215115/http%3A//www.python.org/ftp/python/3.1.1/Python-3.1.1.tar.bz2 "Grab the Source for the Python 3.1 Release")

#### [Python Jobs](/web/20100102215115/http%3A//www.python.org/community/jobs/ "Employers and Job Openings")

#### [Python Merchandise](/web/20100102215115/http%3A//www.python.org/community/merchandise/ "T-shirts & more; a portion goes to the PSF")

#### [Report Website Bug](http://web.archive.org/web/20100102215115/http%3A//wiki.python.org/moin/PythonWebsiteCreatingNewTickets "Submission System for Problems/Suggestions with the Website")

#### [Help Fund Python](/web/20100102215115/http%3A//www.python.org/psf/donations/)

[![](/web/20100102215115im_/http://www.python.org/images/donate.png)](/web/20100102215115/http%3A//www.python.org/psf/donations/)

# Python Programming Language -- Official Website

[![[Come to PyCon 2010 in Atlanta]](/web/20100102215115im_/http://www.python.org/images/pycon-2010-banner.png)](http://web.archive.org/web/20100102215115/http%3A//us.pycon.org/2010/about/)
#### Visualize data with Python...

[![success story photo](/web/20100102215115im_/http://www.python.org/images/success/mayavi.jpg)](/web/20100102215115/http%3A//www.python.org/about/success/mayavi/)

... joining users such as [Rackspace](about/success/rackspace/),
[Industrial Light and Magic](about/success/ilm/),
[AstraZeneca](about/success/astra/),
[Honeywell](about/success/honeywell/),
[and many others](about/success/).

#### What they are saying...

**ITA Software:**

Since then, we've changed how we use Python a ton internally. We have
lots more production software written in Python. We've basically
reimplemented all our production service monitoring in Python and also
our production software management infrastructure for a significant
amount of what we run.

A big component to that has been our use of Twisted Python. We're
pretty reliant on the Twisted framework, and we use it for our
base-line management software that we use to run the great majority of
production services that we have, our monitoring infrastructure and
the next-generation thing that we have coming, which is a suite of
programs that will automate the upgrade process for us.

-- Dan Kelley, director of application integration at ITA Software,
quoted in [eWeek](http://web.archive.org/web/20100102215115/http%3A//www.eweek.com/article2/0%2C1895%2C2100629%2C00.asp).

[more...](/web/20100102215115/http%3A//www.python.org/about/quotes "more quotes")

#### Using Python For...

* [Web Programming](http://web.archive.org/web/20100102215115/http%3A//wiki.python.org/moin/WebProgramming)
* [CGI](http://web.archive.org/web/20100102215115/http%3A//wiki.python.org/moin/CgiScripts),
  [Zope](http://web.archive.org/web/20100102215115/http%3A//www.zope.org/),
  [Django](http://web.archive.org/web/20100102215115/http%3A//www.djangoproject.com/),
  [TurboGears](http://web.archive.org/web/20100102215115/http%3A//www.turbogears.org/),
  [XML](http://web.archive.org/web/20100102215115/http%3A//wiki.python.org/moin/PythonXml)
* [Databases](http://web.archive.org/web/20100102215115/http%3A//wiki.python.org/moin/DatabaseProgramming/)
* [ODBC](http://web.archive.org/web/20100102215115/http%3A//www.egenix.com/files/python/mxODBC.html),
  [MySQL](http://web.archive.org/web/20100102215115/http%3A//sourceforge.net/projects/mysql-python)
* [GUI Development](http://web.archive.org/web/20100102215115/http%3A//wiki.python.org/moin/GuiProgramming)
* [wxPython](http://web.archive.org/web/20100102215115/http%3A//wiki.python.org/moin/WxPython),
  [tkInter](http://web.archive.org/web/20100102215115/http%3A//wiki.python.org/moin/TkInter),
  [PyGtk](http://web.archive.org/web/20100102215115/http%3A//wiki.python.org/moin/PyGtk),
  [PyQt](http://web.archive.org/web/20100102215115/http%3A//wiki.python.org/moin/PyQt)
* [Scientific and Numeric](http://web.archive.org/web/20100102215115/http%3A//wiki.python.org/moin/NumericAndScientific)
* [Bioinformatics](http://web.archive.org/web/20100102215115/http%3A//www.pasteur.fr/recherche/unites/sis/formation/python/index.html),
  [Physics](http://web.archive.org/web/20100102215115/http%3A//www.pentangle.net/python/handbook/)
* [Education](/web/20100102215115/http%3A//www.python.org/community/sigs/current/edu-sig)
* [pyBiblio](http://web.archive.org/web/20100102215115/http%3A//www.openbookproject.net/pybiblio/),
  [Software Carpentry Course](http://web.archive.org/web/20100102215115/http%3A//osl.iu.edu/~lums/swc/)
* [Networking](/web/20100102215115/http%3A//www.python.org/about/apps)
* [Sockets](http://web.archive.org/web/20100102215115/http%3A//docs.python.org/howto/sockets.html),
  [Twisted](http://web.archive.org/web/20100102215115/http%3A//twistedmatrix.com/trac/)
* [Software Development](/web/20100102215115/http%3A//www.python.org/about/apps)
* [Buildbot](http://web.archive.org/web/20100102215115/http%3A//buildbot.net/trac),
  [Trac](http://web.archive.org/web/20100102215115/http%3A//www.edgewall.com/trac/),
  [Roundup](http://web.archive.org/web/20100102215115/http%3A//roundup.sourceforge.net/),
  [IDEs](http://web.archive.org/web/20100102215115/http%3A//wiki.python.org/moin/IntegratedDevelopmentEnvironments)
* [Game Development](/web/20100102215115/http%3A//www.python.org/about/apps)
* [PyGame](http://web.archive.org/web/20100102215115/http%3A//www.pygame.org/news.html),
  [PyKyra](http://web.archive.org/web/20100102215115/http%3A//www.alobbs.com/pykyra),
  [3D Rendering](http://web.archive.org/web/20100102215115/http%3A//www.vrplumber.com/py3d.py)

[more...](/web/20100102215115/http%3A//www.python.org/about/apps)

**Python is a programming language that lets you work more quickly and
integrate your systems more effectively. You can learn to use Python
and see almost immediate gains in productivity and lower maintenance
costs.**

Python runs on Windows, Linux/Unix, Mac OS X, 


## File Download Result
File was downloaded and saved under path ./downloads/file.png.