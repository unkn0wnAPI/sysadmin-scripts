#!/usr/bin/python3

#
## Script Name: Cisco Password-Encryption Decryptor
## Author:      unkn0wnAPI [https://github.com/unkn0wnAPI]
## Information: Recover lost passwords from old Cisco network devices
#

#
## Configuration
#
PASSWORDS: list[str] = []

#
## Global Variables
#
CISCO_KEYS: list[int] = [
    0x64, 0x73, 0x66, 0x64, 0x3B, 0x6B, 0x66, 0x6F,
    0x41, 0x2C, 0x2E, 0x69, 0x79, 0x65, 0x77, 0x72,
    0x6B, 0x6C, 0x64, 0x4A, 0x4B, 0x44, 0x48, 0x53,
    0x55, 0x42
]

#
## Functions
#
def type7_decryptor(passwd: list[str]) -> list[str]:
    global CISCO_KEYS

    decrypted_passwords: list[str] = []
    for password in passwd:
        seed = int(password[:2])
        enc_bytes = password[2:]
        decrypted_password = ''

        for i in range(0, len(enc_bytes), 2):
            byte = int(enc_bytes[i:i+2], 16)
            decrypted_password += chr(byte ^ CISCO_KEYS[(seed + i // 2) % len(CISCO_KEYS)])

        decrypted_passwords.append(decrypted_password)
    return decrypted_passwords

def main() -> None:
    global PASSWORDS

    print('===Cisco Password-Encryption (Type 7) Decryptor===')

    if len(PASSWORDS) == 0:
        print('[ERROR] No passwords provided for decryption')
        return 1
    
    print(f'[INFO] Found {len(PASSWORDS)} passwords to decrypt')
    decrypted_passwords: list[str] = type7_decryptor(PASSWORDS)
    print('[OUTPUT] Decrypted passwords (ENCRYPTED -> PLAIN TEXT):')

    for x in range(len(PASSWORDS)):
        print(f' - {PASSWORDS[x]} -> {decrypted_passwords[x]}')

if __name__ == '__main__':
    main()