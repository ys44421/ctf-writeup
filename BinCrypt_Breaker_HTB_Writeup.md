# BinCrypt Breaker - HTB Write-up
---
**Category**: Reverse Engineering  
**Difficulty**: Medium   
**Files**: `checker`, `file.bin`  
**Goal**: Find the hidden flag

---
## Step 1: Understanding the Challenge

When I downloaded the challenge files, I had two files:
- `checker` - A program that checks if you have the correct flag
- `file.bin` - An encrypted file containing the real challenge
<img width="645" height="98" alt="image" src="https://github.com/user-attachments/assets/25a225fa-7671-4daa-9cb8-a7925f444dd3" />

- My goal was to find the flag hidden in these files.

---

## Step 2: Initial File Analysis
First, I needed to understand what type of files I was working with:

<img width="1901" height="187" alt="image" src="https://github.com/user-attachments/assets/9cbfec0f-31b7-4f21-bd30-0fe29caf4109" />

- Checker is a Linux executable program

- file.bin is a data file (encrypted content)

---

## Step 3: Testing the Program
<img width="1903" height="286" alt="image" src="https://github.com/user-attachments/assets/e3e9c049-2ffa-4699-a38e-7f97ac9e6f68" />

I executed the checker to observe its behavior:

```bash
./checker file.bin
# -> prompts: Enter the flag (without HTB{})
# -> input: test
# -> output: Wrong flag
```
---

## Step 4: Finding the Encryption Method

**Why I used objdump:** 
- I needed to see the program's code to understand how it works.

**What I looked for:**
- Searched for the "decrypt" function because it handles the file
- Looked for encryption operations like XOR

**What I found:**
- The instruction `xor al, 0xab` in the assembly code
- This means each byte gets XORed with the value `0xab`

**How I knew this was the key:**
- XOR is a common simple encryption
- `0xab` is the value used in the operation

<img width="1070" height="213" alt="image" src="https://github.com/user-attachments/assets/779d03fc-0d80-41e8-8692-383c21795150" />

---
## Step 5: Decrypting the Hidden File

- Since I knew the encryption method (XOR with 0xab), I could decrypt file.bin:
```bash
# Read the encrypted file
with open('file.bin', 'rb') as f:
    encrypted_data = f.read()

# XOR each byte with 0xab to decrypt
decrypted = bytes([b ^ 0xab for b in encrypted_data])

# Save the decrypted content
with open('decrypted_elf', 'wb') as f:
    f.write(decrypted)
```
- Result: I got a new file called decrypted_elf

<img width="687" height="170" alt="image" src="https://github.com/user-attachments/assets/6fe16f13-a365-44c7-bf6f-75728eff6ed1" />

---

## Step 6: Analyzing the Decrypted File

- I examined what was inside the decrypted file: file decrypted_elf
- It was another executable program! So file.bin was hiding a second program.
<img width="1908" height="117" alt="image" src="https://github.com/user-attachments/assets/76e59bf8-811a-41b4-bc51-7d358b2d248f" />

- I made it executable and looked for hidden text:
```bash
chmod +x decrypted_elf
objdump -s -j .rodata decrypted_elf
```
<img width="745" height="317" alt="image" src="https://github.com/user-attachments/assets/b6073ad5-509a-4c14-a9cf-e32e307fe7a5" />

- Important Finding: I found this encrypted string:
```bash
RV{r15]_vcP3o]L_tazmfSTaa3s0
```
- This looked like the encrypted flag!

---

## Step 7: Understanding the Flag Transformation

- The string RV{r15]_vcP3o]L_tazmfSTaa3s0 wasn't the real flag. It needed to be transformed. Through analysis, I discovered the transformation process.
- The algorithm had these steps:
1. Split the string into two equal halves (14 characters each)
2. Apply XOR operations to specific positions in each half
3. Rearrange characters using a specific pattern
4. Swap certain character positions in the final step

---

## Step 8: Writing the Decryption Code

Through careful analysis of the binary and testing various approaches, I determined that the encrypted flag undergoes a multi-step transformation process.

**Key Insights:**
- The transformation involves both cryptographic operations and positional changes
- Different parts of the string are processed with different keys
- Character positions are systematically rearranged
- The process is reversible when you understand the pattern

**Strategy Used:**
- I implemented the reverse of each transformation step
- Verified intermediate results at each stage
- Used Python to automate the decryption process
- Tested with partial strings to validate the approach

The solution required understanding both the cryptographic elements and the positional transformations applied to the flag string.

---

## Step 9: Obtaining the Flag

After implementing and running the decryption algorithm, the program successfully revealed the flag:
<img width="682" height="138" alt="image" src="https://github.com/user-attachments/assets/8f45fab9-1f4b-4598-b16e-5970367129d6" />

---

## Tools Used
- file - File type identification and analysis
- objdump - Binary disassembly and string extraction
- chmod - File permission management
- Python - Custom decryption script implementation

---

## What I Learned

- **Hidden Layers**: Simple encryption can hide bigger challenges inside.
- **File Sections**: Important information often stays in read-only parts of programs.
- **Mixed Methods**: Challenges can use both coding changes and secret writing.
- **Always Check**: Test your answer with the original program to make sure it works.
- **Step by Step**: Break big problems into small pieces to solve them more easily.









