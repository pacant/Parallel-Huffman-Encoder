#ifndef UTIMER_HPP
#define UTIMER_HPP

#include <iostream>
#include <iomanip>
#include <chrono>

class utimer
{
    std::chrono::system_clock::time_point start;
    std::chrono::system_clock::time_point stop;
    std::string message;

private:
    long *us_elapsed;

public:
    utimer(const std::string m);

    utimer(const std::string m, long *us);

    ~utimer();
};

#endif
