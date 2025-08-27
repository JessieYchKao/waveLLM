run
stop -create -randomize -always
deposit -constraint_mode default_delay 0
constraint "delay > 2"
run -rand_solve
