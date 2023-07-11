#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <unordered_map>
#include <queue>
#include <thread>
#include <bitset>
#include <numeric>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <algorithm>
#include <barrier>
#include "utimer.hpp"
#include "huffman_encoder.hpp"
#include "utils.hpp"

using namespace std;

// Node for the Huffman tree
struct HuffmanNode
{
    char data;
    int frequency;
    HuffmanNode *left;
    HuffmanNode *right;

    HuffmanNode(char data, int frequency) : data(data), frequency(frequency), left(nullptr), right(nullptr) {} // leaf
    HuffmanNode(int frequency) : data('\0'), frequency(frequency), left(nullptr), right(nullptr) {}            // internal node

    ~HuffmanNode()
    {
        delete left;
        delete right;
    }
};

// auxiliary function for the priority queue, to order the nodes by frequency (from lowest to highest)
struct CompareFrequency
{
    bool operator()(HuffmanNode *a, HuffmanNode *b) const
    {
        return a->frequency > b->frequency;
    }
};

// Read the input file and count character frequencies with a sort of mapReduce
vector<int> count_frequencies(string input, int nw)
{
    vector<int> lmap[nw];

    mutex m[nw];
    vector<pair<char, int>> reds[nw]; // reducer queues

    mutex r;
    vector<int> res(256, 0);

    barrier bar(nw);

    auto body = [&](int i)
    {
        // range of action for that mapper
        int chunk_size = input.size() / nw;

        int from = i * chunk_size;
        int to = (i == nw - 1) ? input.size() : (i + 1) * chunk_size;

        lmap[i] = vector<int>(256, 0);
        // mapper
        for (int j = from; j < to; j++)
        {
            lmap[i][input[j]]++;
        }

        // sending to the reducer
        for (int j = 0; j < 256; j++)
        {
            if (lmap[i][j] == 0)
                continue;

            int h = (hash<char>{}(char(j))) % nw;              // hash function for redirecting a pair to a reducer
            unique_lock ul(m[h]);                              // locking the queue for that reducer for avoiding concurrency problems
            reds[h].push_back(make_pair(char(j), lmap[i][j])); // add the pair to the queue
        }

        // BARRIER
        bar.arrive_and_wait();

        // reducer
        vector<int> lred(256, 0);

        // local reduce
        for (auto e : reds[i])
        {
            lred[e.first] += e.second;
        }

        // global reduce
        for (int j = 0; j < 256; j++)
        {
            if (lred[j] == 0)
                continue;
            unique_lock rl(r);
            res[j] += lred[j];
        }
        return;
    };

    thread tids[nw];
    for (int i = 0; i < nw; i++)
    {
        tids[i] = thread(body, i);
    }
    for (int i = 0; i < nw; i++)
    {
        tids[i].join();
    }

    return res;
}

// Build the Huffman tree returning the root
HuffmanNode *build_tree(vector<int> char_frequencies)
{
    // Create a priority queue from lowest to highest frequency, this is an auxiliary data structure for extracting the two nodes with the lowest frequency
    priority_queue<HuffmanNode *, vector<HuffmanNode *>, CompareFrequency> pq;

    // Add each character and its frequency to the queue as a Huffman node

    for (int i = 0; i < 256; i++)
    {
        if (char_frequencies[i] == 0)
            continue;
        pq.push(new HuffmanNode(char(i), char_frequencies[i]));
    }
    // Build the tree, combining the two nodes with the lowest frequency until there is only one node left (the root)
    while (pq.size() > 1)
    {
        HuffmanNode *left = pq.top();
        pq.pop();
        HuffmanNode *right = pq.top();
        pq.pop();
        HuffmanNode *parent = new HuffmanNode(left->frequency + right->frequency);
        parent->left = left;
        parent->right = right;
        pq.push(parent);
    }

    return pq.top();
}

// Build the encoding table recursively. Starting from the root, go left and add a 0 to the code, go right and add a 1 to the code. When you reach a leaf, add the code to the encoding table.
void build_encoding_table(const HuffmanNode *node, const string &code, vector<string> &encoding_table)
{
    if (node->left == nullptr && node->right == nullptr) // leaf
    {
        encoding_table[node->data] = code;
        return;
    }
    build_encoding_table(node->left, code + "0", encoding_table);
    build_encoding_table(node->right, code + "1", encoding_table);
}

string ascii_file(const string &input_buffer, int num_threads)
{

    // one vector of char for each thread
    thread tids[num_threads];
    vector<string> output_bytes(num_threads);
    // Reserve space for each thread
    for (int i = 0; i < num_threads; i++)
    {
        output_bytes[i].reserve((input_buffer.size() / num_threads) / 8);
    }

    int chunksize = input_buffer.size() / num_threads;

    // Make sure that the chunksize is a multiple of 8 (input_buffer is a multiple of 8 for sure)

    while (chunksize < 8)
    {
        num_threads--;
        chunksize = input_buffer.size() / num_threads;
    }

    chunksize -= chunksize % 8;

    auto ascii_chunk = [&](int i)
    {
        string temp_buffer;

        int from = i * chunksize;
        int to = (i == num_threads - 1) ? input_buffer.size() : (i + 1) * chunksize;

        temp_buffer.reserve(chunksize / 8);
        char byte;
        for (int j = from; j < to; j += 8)
        {
            temp_buffer += bits_to_char(input_buffer.substr(j, 8)); // inline function!
        }

        output_bytes[i] = std::move(temp_buffer);

        return;
    };
    {
        utimer parallel("Native threads ASCII translation");

        // Fullfill the output buffer in parallel
        for (int i = 0; i < num_threads; i++)
        {
            tids[i] = thread(ascii_chunk, i);
        }

        // Wait for all threads to finish
        for (int i = 0; i < num_threads; i++)
        {
            tids[i].join();
        }
    }
    string res;
    int size = 0;
    for (string &s : output_bytes)
    {
        size += s.size();
    }
    res.reserve(size);
    {
        utimer parallel("Native threads final concatenation");
        for (string &s : output_bytes)
        {
            res += s;
        }
    }
    return res;
}

// Write the encoding table to the output file
void write_encoding_table(const vector<string> &encoding_table)
{
    ofstream output("txt/decoding_table.txt");
    if (!output.is_open())
    {
        cerr << "Failed to open output file: " << endl;
        exit(1);
    }

    // write each entry in the encoding table
    for (int i = 0; i < 256; i++)
    {
        if (encoding_table[i].size() != 0)
            output << char(i) << ": " << encoding_table[i] << "\n";
    }
}

// Encode the input file using the encoding table
string encode_file(const string &input_buffer, int num_threads, const vector<string> &encoding_table)
{

    vector<string> encoded_chunks(num_threads); // vector of encoded chunks of the input file
    // start the threads
    thread enc_threads[num_threads];

    auto encode_chunk = [&](int index)
    {
        // Encode the input chunk using the encoding table
        string output_buffer;

        int chunk_size = input_buffer.size() / num_threads;
        int start = index * chunk_size;
        int stop = (index == num_threads - 1) ? input_buffer.size() : (index + 1) * chunk_size;

        for (int i = start; i < stop; i++)
        {
            output_buffer += encoding_table[input_buffer[i]];
        }
        encoded_chunks[index] = std::move(output_buffer); // writing the encoded chunk to the vector

        return;
    };

    {
        utimer parallel("Native threads encoding");

        for (int i = 0; i < num_threads; i++)
        {
            enc_threads[i] = thread(encode_chunk, i);
        }

        // join and appending to the buffer the encoded chunks
        for (int i = 0; i < num_threads; i++)
        {
            enc_threads[i].join();
        }
    }

    string res;
    int size = 0;

    for (string &s : encoded_chunks)
    {
        size += s.size();
    }

    res.reserve(size); // reserve space for the final string, avoiding reallocations

    {
        utimer parallel("Native threads first concatenation");
        for (string &s : encoded_chunks)
        {
            res += s;
        }
        add_padding(res);
    }

    return res;
}