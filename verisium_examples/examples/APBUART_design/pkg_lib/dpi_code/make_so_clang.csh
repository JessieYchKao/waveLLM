rm ./libtest_v1.so
#/grid/common/test/llvm-v3.8.0rh65_ny/bin/clang -g -shared -D DPI_COMPATIBILITY_VERSION_1800v2005 -fsigned-char -o libtest_v1.so -fPIC test_v1.c -I `xmroot`/tools/include
# Need to point to CLANG installation below
/grid/common/test/llvm-v3.8.0rh65_ny/bin/clang -g -shared -D DPI_COMPATIBILITY_VERSION_1800v2005 -fsigned-char -o libtest_v1.so -fPIC test_v1.c -I `xmroot`/tools/include

