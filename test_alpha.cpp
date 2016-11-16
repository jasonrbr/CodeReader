#include <iostream>
using namespace std;

class ClassA {
	int x;
	class ClassD {
		void member(int x);
	};
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
	void member(int x);
};

void ClassB::member(int x) {
	return x * 2;
}

void ClassA::ClassD::member(int x) {
	return "hello world";
}

void ClassC::member(int x) {
	return "bob";
}

int classA::classD::foo() {
	cout << "in foo\n";
}
