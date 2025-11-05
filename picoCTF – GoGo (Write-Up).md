# picoCTF 2025 - GoGo

---

- **Challenge**: enter_password
- **Difficulty:** Hard - Reverse Engineering
- **Description**: A 32-bit Go binary that requests a password and then an “unhashed key”. The binary verifies a 32-byte password using a bytewise XOR against an internal key and compares the result to expected bytes. The service is also available remotely at mercury.picoctf.net:48728.
- **Tools:** Ghidra, GDB, Python, netcat  
---

## 1. Recon

<img width="1892" height="227" alt="image" src="https://github.com/user-attachments/assets/c6ddcded-f5ed-4711-b59c-d7211e736c3b" />

- Binary identified as Go ELF (32-bit) with debug info.

---

## 2. Static analysis (Ghidra)

- Inspect main and locate the password check function (main.checkPassword).

- Identify the loop that runs 0x20 (32) iterations performing (input[i] ^ key[i]) == expected[i].

<img width="1906" height="762" alt="image" src="https://github.com/user-attachments/assets/dc3d01ad-ff8c-4d38-bd0a-836228bb04ed" />

<img width="453" height="316" alt="image" src="https://github.com/user-attachments/assets/a462ca05-39e1-4016-ade2-59d1fe0c9c1e" />

<img width="727" height="272" alt="image" src="https://github.com/user-attachments/assets/7752c014-9faf-4050-88a3-6aa177903afd" />

- Decompiled main.checkPassword showing XOR loop and key/expected data references.

---

## 3. Dynamic analysis (GDB)

- Set a breakpoint inside the verification loop (address found in disassembly, 0x080d4b28).
- 0x080d4b28 was chosen because it sits inside the verification loop where the code performs the XOR and CMP.
Breaking there halts execution when the input, key, and expected bytes are all on the stack, allowing direct memory dumps to recover the password.
- Run the program with a 32-byte test input and dump memory:

```
gdb -q ./enter_password
b *0x080d4b28
run
# after breakpoint:
x/32xb $ecx         # input bytes
x/32xb $esp+0x4     # key bytes (XOR operand)
x/32xb $esp+0x24    # expected bytes (compare target)
```

<img width="1135" height="485" alt="image" src="https://github.com/user-attachments/assets/c4b7f3c2-8911-449f-b10a-dfc3b575f114" />

- Memory dumps: input, key, and expected bytes.

---

## 4. Reconstructing the password

- For each index i (0..31) compute:
```
password[i] = expected[i] ^ key[i]
```
- Use a short Python script to XOR the two byte arrays and print the resulting password.

---

## 5. Unhashed key extraction

- After submitting the reconstructed password the service prompts: “What is the unhashed key?”

<img width="777" height="188" alt="image" src="https://github.com/user-attachments/assets/a85dacd1-ce18-4fea-99c8-a863bc0a143e" />

- To obtain it: stop the program at the XOR instruction, dump the key bytes from the stack, and convert those bytes to ASCII to form the unhashed MD5 string.

```
# break inside loop, run with the 32-byte password
gdb -q ./enter_password
b *0x080d4b28
run
# after breakpoint:
x/32xb $esp+0x4         # dump key bytes
# convert to ASCII-hex string
```

---

## 7. Remote verification

- Connect to the service and submit the reconstructed password and unhashed key:
```
nc mercury.picoctf.net 48728
# Enter password: [reconstructed_password]
# What is the unhashed key? [unhashed_key]
```
- After submitting the reconstructed password and the unhashed key the remote service returns the flag

<img width="785" height="258" alt="image" src="https://github.com/user-attachments/assets/05f3443f-6607-4029-bcb8-8a5b6fc23cc0" />

---

**End of write-up**


