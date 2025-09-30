# RAuth | HackTheBox (Reversing Challenge) - writeup

- **CTF name:** HackTheBox  
- **Challenge name:** RAuth  
- **Category:** Reversing / Crypto  
- **Difficulty:** Easy
- **Goal:** Locate an embedded key/ciphertext in the binary and decrypt it to get the password.

---
## 1. First look - what to look for
- When reversing a small challenge program, look for suspicious data first - long ASCII hex strings, long blobs, or references to crypto functions. These are often embedded keys/ciphertexts
- Identify the file type and metadata.
<img width="700" height="400" alt="image" src="https://github.com/user-attachments/assets/29ab9589-a7f7-4fb2-b20c-4eb19bf8ab70" />

---
## 2. Login Prompt Test
- This confirms the binary reads user input and has a password check. Triggering the wrong-password path helps decide where to set breakpoints or search the binary for embedded keys/ciphertext
  <img width="400" height="150" alt="image" src="https://github.com/user-attachments/assets/61714834-4112-4286-a335-db6df00ceaa0" />

  ---
## 3. Use radare2 to locate where that data lives
- Why: strings show candidate data, but we need the address and who uses it.
  
  
