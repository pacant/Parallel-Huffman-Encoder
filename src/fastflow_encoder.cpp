#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <string>
#include <ff/ff.hpp>
#include <ff/parallel_for.hpp>
#include <ff/map.hpp>
#include <functional>
#include "utimer.hpp"
#include "huffman_encoder.hpp"
#include "utils.hpp"

using namespace ff;
using namespace std;

string encode_file_ff(const string &input_buffer, int num_threads, const vector<string> &encoding_table)
{
    ParallelFor pf(num_threads);
    vector<string> encoded_chunks(num_threads); // vector of encoded chunks of the input file

    auto Map = [&](const long start, const long stop, const int thid)
    {
        if (start == stop)
            return;

        string temp_buffer;

        for (long i = start; i < stop; i++)
            temp_buffer += encoding_table[input_buffer[i]];

        encoded_chunks[thid] = std::move(temp_buffer);
    };

    {
        utimer parallel("Fastflow encoding");
        pf.parallel_for_idx(
            0, input_buffer.size(), 1, 0, Map,
            num_threads);
    }

    string res;
    int size = 0;
    for (string &s : encoded_chunks)
    {
        size += s.size();
    }
    res.reserve(size);
    {
        utimer parallel("Fastflow first concatenation");
        for (string &s : encoded_chunks)
        {
            res += s;
        }
        add_padding(res);
    }

    return res;
}
vector<int> count_frequencies_ff(const string &input_buffer, int num_threads)
{
    {
        vector<int> res(256, 0);

        vector<int> lmap[num_threads];

        // ParallelForPipeReduce?
        ParallelFor pf(num_threads, true);

        auto Map = [&](const long start, const long stop, const int thid)
        {
            if (start == stop)
                return;

            lmap[thid] = vector<int>(256, 0);

            for (long i = start; i < stop; ++i)
            {
                lmap[thid][input_buffer[i]]++;
            }
        };

        pf.parallel_for_idx(0, input_buffer.length(), 1, 0, Map, num_threads);

        for (int i = 0; i < num_threads; i++)
        {
            for (int j = 0; j < 256; j++)
            {
                res[j] += lmap[i][j];
            }
        }
        return res;
    }
}
string ascii_file_ff(const string &output_buffer, int num_threads)
{

    vector<string> output_bytes(num_threads);

    int chunksize = output_buffer.size() / num_threads;

    // Make sure that the chunksize is a multiple of 8 (output_buffer is a multiple of 8 for sure) the last thread will take care of the remaining b

    chunksize -= chunksize % 8;

    chunksize = max(chunksize, 8);

    ParallelFor pf(num_threads);

    auto Map = [&](const long start, const long stop, const int thid)
    {
        if (start == stop)
            return;

        string temp_buffer;
        for (int i = start; i < stop; i += 8)
        {
            temp_buffer += bits_to_char(output_buffer.substr(i, 8)); // Convert the 8 bits to a byte
        }

        output_bytes[thid] = std::move(temp_buffer);
    };

    {
        utimer ff("Fastflow ASCII translation");

        pf.parallel_for_idx(
            0, output_buffer.size(), 1, chunksize, Map, num_threads);
    }
    string res;
    int size = 0;
    for (string &s : output_bytes)
    {
        size += s.size();
    }
    res.reserve(size);
    {
        utimer parallel("Fastflow final concatenation");
        for (string &s : output_bytes)
        {
            res += s;
        }
    }

    return res;
}