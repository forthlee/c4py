// Brainfuck in C
// Slightly altered to work in C4
// Original code borrowed from:
//    http://phimuemue.com/posts/2011-08-04-intermezzo-a-brainf-interpreter.html
//    http://www.github.com/phimuemue

// Usage:
//   ./c4 tests/brainf.c "`cat tests/prime.bf`" 30000
// First argument is code to run. Must be quoted.
// Second argument is tape length. 30000 works for the prime number generator.

// int abs(int n) { return n < 0 ? n * -1 : n; }
// void putchar(char c) { printf("%c", c); }

#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <unistd.h>
#include <fcntl.h>

int main(int a,char**s){
	int *b, *z, p;
	char *c, v, w;

	if(a < 3)
		return printf("Usage: %s \"code\" length\n"
		              "Where:\n"
		              "   \"code\"   Quoted code to run. Try \"`cat file`\".\n"
		              "    length  Tape length. Try 30000.\n", s[0]);

	// p = atoi(s[2])
	p = 0; while(*s[2]) p = p * 10 + (*s[2]++ - '0');
	if(!(b = z = malloc(p))) return printf("Failed to allocate %ld bytes\n", p);
	c = s[1];

	while(*c) {
		p = 1;
		*c-'>' || (++z);
		*c-'<' || (--z);
		*c-'+' || (++*z);
		*c-'-' || (--*z);
		*c-'.' || (printf("%c", *z));
		*c-',' || (*z =getchar());
		if(*c == '[' || *c == ']') {
			v = *c;
			w = 184 - v;
			if(v < w ? *z == 0 : *z != 0)
				while(p) {
					c = c + (v < w ? 1 : -1);
					p = p + (*c == v ? 1 : *c == w ? -1 : 0);
				}
		}
		c++;
	}

	free(b);
	return 0;
}
