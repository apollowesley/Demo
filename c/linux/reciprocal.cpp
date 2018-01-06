#include <cassert>
#include "reciprocal.hpp"
double reciprocal(int i)
{ // i 不能为 0
    assert(i != 0);
    return 1.0 / i;
    
}