main.c:
	cython --embed main.pyx -2

main: main.c
	gcc -Os -I /usr/include/python2.7 -o main main.c -lpython2.7 -lpthread -lm -lutil -ldl
