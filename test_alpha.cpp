#include <iostream>
using namespace std;

class ClassA {
	int x;
};

int main() {
	bool y = true;
	int x = 5;
	return 0;
}

class ClassB {
	void member(int x);
};


void foo(int x) {
	for(int i = 0; i < x; ++i) {
		cout << i << endl;
	}
}

class ClassC {
	void member(int x) {
		cout << x << endl;
	}
};
