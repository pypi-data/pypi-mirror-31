``mk60`` is a console application assisting in creation of Elektronika D3-28
tapes from data files. This application reads given data file and encodes it in
the WAVE (WAV) audio format according to the modulation scheme used by D3-28.
That audio file may be replayed further with conventional software and recorded
to a compact cassette compatible with D3-28's tape transport.

Currently only one input data format is supported: text file with decimal-coded
hexadecimal codes of D3-28's memory segment. Each line shall contain one data
byte, or be empty, or start with comment ``#`` symbol. The last byte in the
file must be the D3-28's ``END`` instruction -- i.e., the code ``0512``.

Best regards, Alexander A. Strelets <streletsaa@gmail.com>
