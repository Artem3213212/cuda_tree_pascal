TreeHelper for Pascal lexer.
Requires plugin CudaTree to work.

Based on Python library PyPascalTokenizer.

Can parse and show these Pascal entities:
- standalone functions/procedures
- class methods
- classes
- nested classes (nesting level: 2 or more)
- nested functions (nesting level: 2 or more)
- records
- interfaces
- var/const declarations, global and local (in funcs/methods)
- properties
- uses (both interface/implementation, shown under single node)
- resourcestrings
- anonymous funcs/methods
- procedural types


Author: Artem Gavrilov (@Artem3213212 at GitHub)
License: MIT
