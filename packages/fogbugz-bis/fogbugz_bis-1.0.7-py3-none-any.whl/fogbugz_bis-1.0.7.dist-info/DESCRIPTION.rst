All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list
of conditions and the following disclaimer.  Redistributions in binary form must
reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the
distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Description: Python FogBugz API Wrapper
        --------------------------
        
        This Python API is simply a wrapper around the FogBugz API, with some help from Leonard Richardson's BeautifulSoup (http://www.crummy.com/software/BeautifulSoup/) and the magic of Python's __getattr__().
        
        Getting Started:
        ----------------
        
        To use the FogBugz API, install the package either by downloading the source and running
        
          $ python setup.py install
        
        or by using pip
        
          $ pip install fogbugz
        
        A Quick Example:
        ----------------
        
        ::
        
          >>> from fogbugz import FogBugz
          >>> fb = FogBugz("http://example.fogbugz.com/") # URL is to your FogBugz install
          >>> fb.logon("logon@example.com", "password")
          >>> resp = fb.search(q="assignedto:tyler") # All calls take named parameters, per the API
          >>> resp # Responses are BeautifulSoup objects of the response XML.
          <response><cases count="2"><case ixbug="1" operations="edit,assign,resolve,email,remind"></case><case ixbug="2" operations="edit,spam,assign,resolve,reply,forward,remind"></case></cases></response>
          >>> # You shouldn't need to know too much about BeautifulSoup, but the documentation can be found here:
          >>> # http://www.crummy.com/software/BeautifulSoup/documentation.html
          >>> for case in resp.cases.childGenerator(): # One way to access the cases
          ...     print case['ixbug']
          ...
          1
          2
          >>> for case in resp.findAll('case'): # Another way to access the cases
          ...     print case['operations']
          ...
          edit,assign,resolve,email,remind
          edit,spam,assign,resolve,reply,forward,remind
          >>> resp = fb.edit(ixbug=1, sEvent="Edit from the API") # Note the named parameters
          >>> resp
          <response><case ixbug="1" operations="edit,assign,resolve,email,remind"></case></response>
        
        Note that, per API v5.0, all data between tags, such as the token, is now wrapped in CDATA.  BeautifulSoup's implementation of CData generally allows for it to be treated as a string, except for one important case: CData.__str__() (a.k.a. str(CData)) returns the full text, including the CDATA wrapper (e.g. "<![CDATA[foo]]>").  To avoid accidentally including the CDATA tage, use CData.encode('utf-8')
        
        Additional Details:
        -------------------
        
        If your script requires a certain version of the FogBugz API, make sure to pass it as an argument to the constructor. This will protect you from unexpected differences should we make backwards-incompatible changes.
        
          >>> from fogbugz import FogBugz
          >>> fb = FogBugz("http://example.fogbugz.com", api_version=5)
        
        For more info on the API:
        http://help.fogcreek.com/the-fogbugz-api
        
        Much of the API has not been thoroughly tested.  Please report bugs to customer-service@fogcreek.com
        
        ``fogbugz_bis`` is a fork of the FogCreek codebase to support Python 3 and
        BeautifulSoup 4. You should install/require only one of ``fogbugz`` or
        ``fogbugz_bis`` as they both implement the same module.
        
Platform: UNKNOWN
Classifier: Development Status :: 5 - Production/Stable
Classifier: Intended Audience :: Developers
Classifier: Natural Language :: English
Classifier: Operating System :: MacOS :: MacOS X
Classifier: Operating System :: Microsoft :: Windows
Classifier: Operating System :: POSIX
Classifier: Operating System :: POSIX :: BSD
Classifier: Operating System :: POSIX :: Linux
Classifier: Programming Language :: Python
Classifier: Topic :: Internet :: WWW/HTTP
Classifier: Topic :: Software Development
Classifier: Topic :: Software Development :: Bug Tracking
Classifier: Topic :: Software Development :: Libraries
Classifier: Topic :: Software Development :: Libraries :: Python Modules
Classifier: Topic :: Software Development :: Version Control
Classifier: Topic :: Utilities
Requires: BeautifulSoup
Requires: lxml
