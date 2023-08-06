
\>\>\> from XOR_CheckSum import xor_checksum_string

\>\>\> xor_checksum_string('CCICA,0,00')

123

\>\>\> hex(xor_checksum_string('CCICA,0,00'))

'0x7b'

\>\>\> hex(xor_checksum_string('CCICA,0,00', encoding="utf-8"))

'0x7b'

\>\>\> hex(xor_checksum_string('CCICA,0,00', encoding="utf-16"))

'0x7a'


