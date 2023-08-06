Copyright (c) 2017 Stefan Badelt and contributors <badelt@caltech.edu>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Download-URL: https://github.com/DNA-and-Natural-Algorithms-Group/dsdobjects/archive/v0.6.tar.gz
Description: # dsdobjects - base classes for DSD design
        
        This module provides standardized Python parent classes for 
        domain-level strand displacement programming:
        
          - SequenceConstraint
          - DL_Domain
          - SL_Domain
          - DSD_Complex
          - DSD_Reaction
          - DSD_RestingSet
        
        An example is shown below:
        
        ```py
        from dsdobjects import DL_Domain
        
        # A personalized domain that extends the DL_Domain base class.
        class MyDomain(DL_Domain):
        
            def __init__(self, name, dtype=None, length=None):
                super(MyDomain, self).__init__(name, dtype, length)
         
            @property
            def complement(self):
                # Automatically initialize or return the complementary domain.
                if self._complement is None:
                    cname = self._name[:-1] if self.is_complement else self._name + '*'
                    if cname in DL_Domain.MEMORY:
                        self._complement = DL_Domain.MEMORY[cname]
                    else :
                        self._complement = MyDomain(cname, self.dtype, self.length)
                return self._complement
        
        ```
        
        Inheriting from the DL_Domain base class enables standardized built in
        functions such as '~', '==', '!=', and provides a built-in memory management
        raising the DSDDuplicationError when conflicting domain names are chosen.
        
        
        ```py
        >>> # Initialize a Domain.
        >>> x = MyDomain('hello', dtype='short')
        >>> # The '~' operator calls x.complement
        >>> y = ~x
        >>> (y == ~x)
        True
        
        ```
        
        These and many more functionalities and sanity checks are also available for
        other objects. See the respective docstrings for details.  
        
        ## Install
        To install this library, use the following command in the root directory:
        ```
        $ python ./setup.py install
        ```
        or use local installation:
        ```
        $ python ./setup.py install --user
        ```
        
        ## Version
        0.6 -- PIL parser supports concentration format
          * "non-equal" bugfixes in base_classes.py
          * supports rate-error bars when parsing PIL format
        
        0.5 -- improved canonical forms
        
        ## Author
        Stefan Badelt
        
        ### Contributors
        This library contains adapted code from various related Python packages coded
        in the [DNA and Natural Algorithms Group], Caltech:
          * "DNAObjecs" coded by Joseph Berleant and Joseph Schaeffer 
          * [peppercornenumerator] coded by Kathrik Sarma, Casey Grun and Erik Winfree
          * [nuskell] coded by Seung Woo Shin
        
        ## Projects depending on dsdobjects
          * [peppercornenumerator]
          * [nuskell]
        
        
        ## License
        MIT
        
        [nuskell]: <http://www.github.com/DNA-and-Natural-Algorithms-Group/nuskell>
        [peppercornenumerator]: <http://www.github.com/DNA-and-Natural-Algorithms-Group/peppercornenumerator>
        [DNA and Natural Algorithms Group]: <http://dna.caltech.edu>
        
Platform: UNKNOWN
Classifier: Development Status :: 3 - Alpha
Classifier: Programming Language :: Python :: 2.7
