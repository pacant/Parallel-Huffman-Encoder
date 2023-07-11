using namespace std;
inline char bits_to_char(const string &bitString)
{
    int byte = 0;
    for (char bit : bitString)
    {
        byte = byte * 2 + (bit - '0'); // basically a shift + int value of the bit
    }
    return char(byte);
}

inline void add_padding(string &output_buffer)
{
    int num_padding_bits = 8 - output_buffer.size() % 8;
    if (num_padding_bits == 8)
        num_padding_bits = 0;

    // Convert the num_padding_bits to a binary string representation
    string header = "";
    for (int i = 0; i < 8; i++)
    {
        header = char('0' + num_padding_bits % 2) + header;
        num_padding_bits /= 2;
    }

    // Add padding bits
    output_buffer.append(num_padding_bits, '0');
    output_buffer += header;
}
