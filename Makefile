all: beagle-broker version

%: src/%.cxx 
	g++ -o $@ $^ -Wall -Wextra -std=c++0x -O3 -lzmq