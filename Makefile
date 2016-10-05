all: beagle_broker

%: src/%.cxx
	g++ $^ -o $@ -O3 -Wall -Wextra -lzmq -std=c++0x
