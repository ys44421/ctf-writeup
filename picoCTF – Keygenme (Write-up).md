# picoCTF - Keygenme

---

| Field | Details |
|:--|:--|
| **CTF Name** | picoCTF 2024 |
| **Challenge Name** | Keygenme |
| **Challenge Category** | Reverse Engineering - Hard |

---

**TL;DR**

The program builds a license key from a static prefix plus hex output derived from MD5.
Static analysis in Ghidra revealed the algorithm (MD5 + sprintf("%02x") loop). Dynamic analysis with GDB confirmed the runtime addresses and the per-character values in register $RAX. The reconstructed key was tested by piping it into the binary.

---

## 1. Recon (initial inspection)

- The binary is ELF x86_64 and not fully stripped.

<img width="1897" height="227" alt="image" src="https://github.com/user-attachments/assets/cdddc92f-a4ef-4f90-b4a6-266f2ceab8ce" />

---

## 2. Static Analysis (Ghidra)

I loaded the binary into Ghidra and inspected the main routines.

**Key observations**

From the decompiled function in Ghidra, the program builds its expected key as follows:

- It copies the static prefix "picoCTF{br1ng_y0ur_0wn_k3y_" into memory.
- Then it generates two MD5 hashes (one of the prefix and one of a smaller string).
- Each hash is converted to a hexadecimal string using %02x.
- Finally, the resulting characters are compared with the user input to validate the key.

This screenshot shows the part of the Ghidra decompiler where those MD5 calls and hex-conversion loops appear.

<img width="652" height="377" alt="image" src="https://github.com/user-attachments/assets/2c9cb3ed-f380-4932-b038-ee8bd5c3601d" />

---

## 3. Dynamic Analysis (GDB)

- To confirm the exact position where the flag is validated, I ran the program under GDB.
Using the memory map, I identified the base address 0x0000555555554000.
From Ghidra, I knew the check happened near offset 0x13C8, so I set a breakpoint at
0x0000555555554000 + 0x13C8 = 0x00005555555553C8.

<img width="1397" height="675" alt="image" src="https://github.com/user-attachments/assets/d1ecf851-e413-4b68-8c3d-920c8a9abf1a" />
<img width="1200" height="168" alt="image" src="https://github.com/user-attachments/assets/0b26016a-cf23-4dbd-9064-40b71de27e7b" />

- Then I stepped through instructions and monitored the RAX register to watch characters being processed.

<img width="1133" height="353" alt="image" src="https://github.com/user-attachments/assets/020e50fc-37d1-4a2b-8dc4-ff058507e021" />

- Shows the ASCII values of the final constructed string (partially hidden).

---

## 4. Validation
- After confirming the logic, I piped my reconstructed key into the binary:
```
printf 'picoCTF{br1ng_y0ur_0wn_k3y_XXXXXXXX}\n' | ./keygenme

```
- The output confirmed the message “That key is valid.”, which validated my understanding.

---

## 5. Reflection

- This challenge demonstrated how static and dynamic analysis complement each other.
Ghidra revealed the algorithm’s structure, while GDB confirmed its runtime behavior.
The key idea was learning to calculate the real memory address using the binary’s base + offset and setting breakpoints effectively.

---
**End of Write-Up**
