TreeHelper for Pascal lexer.
Requires plugin CudaTree to work.

Based on Python library PyPascalTokenizer.

Can parse and show these Pascal entities:
- standalone function/procedure
- class methods (func/proc/constructor/destructor)
- classes
- classes, nested into another classes (nesting level can be 2 or more)
- var/const declarations, both global and local in funcs/methods
- uses (both interface/implementation, under single node)
- properties
- interfaces
- resourcestrings
- anonymous functions


Author: Artem Gavrilov (@Artem3213212 at GitHub)
License: MIT
