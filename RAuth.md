# RAuth | HackTheBox (Reversing Challenge) - writeup

- **CTF name:** HackTheBox  
- **Challenge name:** RAuth  
- **Category:** Reversing / Crypto  
- **Difficulty:** Easy
- **Goal:** Locate an embedded key/ciphertext in the binary and decrypt it to get the password.

---
## TL;DR
Used static analysis (radare2) to discover the program uses the Salsa20 stream cipher with an embedded key+nonce and ciphertext. Decrypting the ciphertext with the discovered key/nonce yields the password `TheCrucialRustEngineering@2021;)`, which authenticates against the remote service and returns the flag. 

---
## Environment
- OS: Kali Linux 
- Tools: `radare2 (r2)`, `gdb`/`rust-gdb`, `checksec`, `strings`, `python3`
- Recommended: run in an isolated VM (HTB rules).

---
## 1. First look - what to look for
- When reversing a small challenge program, look for suspicious data first - long ASCII hex strings, long blobs, or references to crypto functions. These are often embedded keys/ciphertexts
- Identify the file type and metadata.
<img width="700" height="400" alt="image" src="https://github.com/user-attachments/assets/29ab9589-a7f7-4fb2-b20c-4eb19bf8ab70" />

---
## 2. Login Prompt Test
- This confirms the binary reads user input and has a password check. Triggering the wrong-password path helps decide where to set breakpoints or search the binary
- for embedded keys/ciphertext
<img width="400" height="150" alt="image" src="https://github.com/user-attachments/assets/61714834-4112-4286-a335-db6df00ceaa0" />

  ---
## 3. Use radare2 to locate where that data lives
- Inspecting main with r2 reveals a static blob that the code loads and passes to the Salsa20 routines. The disassembly shows a 32-byte hex string (the Salsa20 key), a movabs immediate that decodes to the nonce, and the following bytes are the ciphertext -decrypting ciphertext with that key+nonce yields the login password.
<img width="1880" height="382" alt="image" src="https://github.com/user-attachments/assets/bb176699-312a-4abe-b59a-293dcc216082" />

---
## 4. How the key & nonce were found
- I located the static blob in .rodata using radare2 and confirmed it at runtime with the debugger. The izz~ef39f4f2 output gave the mapped address (0x5555c0239ca0) containing the ASCII hex string ef39f4f20e76e33bd25f4db338e81b10 followed by escaped bytes (the ciphertext)
- key (ASCII hex): ef39f4f20e76e33bd25f4db338e81b10 -> convert with bytes.fromhex(...)

- ciphertext (hex):
05 05 5F B1 A3 29 A8 D5 58 D9 F5 56 A6 CB 31 F3 24 43 2A 31 C9 9D EC 72 E3 3E B6 6F 62 AD 1B F9
  <img width="1487" height="373" alt="image" src="https://github.com/user-attachments/assets/f353910d-4d1f-4e66-89c0-657db979fe42" />

  ---
## 5. Extract the nonce from the movabs immediate in the disassembly
- nonce_hex = "d4c270a3"

  <img width="1408" height="187" alt="image" src="https://github.com/user-attachments/assets/9d193d0d-39aa-434e-9edd-30eb9c491abe" />

---
## 6. Write & Run Decryptor
- This Python script converts the ASCII-encoded key/nonce found in the binary into raw bytes, initializes a Salsa20 stream cipher with those values, and decrypts the embedded ciphertext to recover the login password.

<img width="1167" height="741" alt="image" src="https://github.com/user-attachments/assets/a5e057d0-f4c4-49fb-86e6-244bee838a66" />
<img width="732" height="348" alt="image" src="https://github.com/user-attachments/assets/70997e27-7120-47d8-9d4a-4d0c03d5b491" />





  
  
