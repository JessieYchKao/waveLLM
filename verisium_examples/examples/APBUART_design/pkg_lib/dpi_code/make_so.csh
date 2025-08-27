rm -fr ./libtest_v1.so
#/grid/avs/install/xcelium/AGILE/latest/tools/cdsgcc/gcc/bin/gcc -g -shared -D DPI_COMPATIBILITY_VERSION_1800v2005 -fsigned-char -o libtest_v1.so -fPIC test_v1.c -I `xmroot`/tools/include
`xmroot`/tools/cdsgcc/gcc/bin/gcc -g -shared -D DPI_COMPATIBILITY_VERSION_1800v2005 -fsigned-char -o libtest_v1.so -fPIC ./files/test_v1.c -I `xmroot`/tools/include
