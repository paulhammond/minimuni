# minimuni

This is the source code behind [minimuni.paulhammond.org]. It runs on
Google App Engine.

To get a dev environment set up:

 1. Install the App Engine SDK. Either follow [Google's instructions][install]
    or run `brew install google-app-engine` if you're using homebrew.
 2. run "dev_appserver.py ."

If you've made changes and you'd like to deploy them to Google's servers:

  1. sign up at http://appengine.google.com/, click "create an application"
     and fill in the form
  2. edit the first line of app.yaml to use your application identifier
  3. run "appcfg.py update ."

[minimuni]: http://minimuni.paulhammond.org
[install]: http://code.google.com/appengine/docs/gettingstarted/devenvironment.html

## License

Copyright (c) 2013 Paul Hammond. minimuni is available under the MIT license,
see LICENSE.txt for details.