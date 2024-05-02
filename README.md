# c4py
A tiny C compiler and virtual machine, a Python language port of 'c4 - C in four functions', capable of enabling self-compilation.<p>


&gt; python c4py.py hello.c<br>
&gt; python c4py.py -s hello.c<br>
&gt; python c4py.py -d hello.c<p>

&gt; python c4py.py c4.c hello.c<br>
&gt; python c4py.py c4.c -s hello.c<br>
&gt; python c4py.py c4.c -d hello.c<p>

&gt; python c4py.py c4.c c4.c hello.c<p>

// c4.c - C in four functions<br>
// char, int, and pointer types<br>
// if, while, return, and expression statements<br>
// just enough features to allow self-compilation and a bit more<br>
https://github.com/rswier/c4
