# picoCTF – Hurry up! Wait!

---


| Field | Details |
|:--|:--|
| **CTF Name** | picoCTF 2024 |
| **Challenge Name** | Hurry up! Wait! |
| **Challenge Category** | Reverse Engineering - Hard |
| **Challenge Description** | A mysterious ELF binary named `svchost.exe` written in Ada. When executed, it delays output for a long time. The goal is to analyze the binary to uncover the hidden flag without waiting for all delays to finish. |

---

##  Challenge Overview
The provided ELF file looks like a standard Linux program, but its name is misleading.  
Static analysis shows the binary was compiled from **Ada source code**, which already hints at unusual structure and function names.  
Our objective: find the hidden flag efficiently.

**Initial clues:**
- Presence of Ada runtime functions like `ada__calendar__delays`.
- The program likely uses built-in Ada delays to slow output.

<img width="1908" height="117" alt="image" src="https://github.com/user-attachments/assets/56a2331d-4295-494e-a10c-b820e0dffab3" />

<img width="653" height="565" alt="image" src="https://github.com/user-attachments/assets/64d39937-4909-4254-ab0e-cfb897e0eda5" />

---

## Step 1 – Main Routine Analysis

The function `FUN_0010298a` acts as the program’s main routine.  
It first calls `ada__calendar__delays__delay_for()` (an Ada runtime delay) and then runs a long list of helper calls (`FUN_00xxxx`).  
Each helper prints a single character stored in `.rodata`.  
By following the call order, the hidden text can be reconstructed.

>  *Hint:* focus on how the call sequence in `FUN_0010298a` relates to data bytes in `.rodata`.

<img width="1907" height="895" alt="image" src="https://github.com/user-attachments/assets/f044ac34-5ee7-4890-8189-f3229305b2af" />

---

## Step 2 –Understanding the Mechanism

The main routine (`FUN_0010298a`) calls a series of small helper functions.  
Each helper function loads a specific address from the `.rodata` section and prints the character stored there using the Ada function `ada__text_io_put_4()`.

By analyzing these calls, it becomes clear that each function corresponds to one letter of the hidden message.  
When all helper functions run in order, they print the complete flag.

>  *Hint:* focus on the `LEA RAX, [DAT_...]` instructions - each one points to a different data address containing a single ASCII byte.

<img width="1447" height="816" alt="Screenshot 2025-11-03 004656" src="https://github.com/user-attachments/assets/dc2de40d-ce79-482e-8b22-1022396a1f6c" />
<img width="980" height="210" alt="Screenshot 2025-11-03 004753" src="https://github.com/user-attachments/assets/2b5ea241-b5c2-4c38-9f2b-e86bfb80cd7e" />

---
##  Step 3 - Automating the Extraction
Rather than reading every address manually, I automate the process using a short **Python script** inside Ghidra.  
The script:
1. Finds all calls from `main` to `FUN_00xxxx`.  
2. Moves to each function’s instruction at `entry + 0x9`.  
3. Extracts the data address referenced there.  
4. Reads the byte stored at that address.  
5. Prints all bytes together as one string.

This is the **fastest** approach to reveal the hidden flag.

<img width="243" height="52" alt="image" src="https://github.com/user-attachments/assets/deb3d356-c5ad-4d56-95d9-05cc62ad7903" />

---

## 💡 Step 4 - Result and Reflection
This challenge demonstrates how compiled Ada code can distribute static data across many sub-functions to obscure information.  
Understanding the repeating pattern and writing a simple automation script is far more efficient than manual decoding.

---

**End of Write-Up**
