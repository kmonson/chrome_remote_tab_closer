Chrome Remote Tab Closer
------------------------

With remote schooling being inevitable in our school district in the fall of 
2020 I needed a way to *quickly and immediately* block and unblock websites in Chrome
remotely. Sites such as Youtube are necessary for schoolwork some of the time
but are also a huge distraction.

This is accomplished by opening Chrome with remote debugging enabled and
using pychrome to periodically close any open tab with an offending URL.

This is done in two parts:
- A service that reads one or more configuration files and enforces the bans.
- A simple web server for updating the configurations remotely. (TODO)