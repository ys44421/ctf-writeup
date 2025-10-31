# SEPC - Hack The Box

---
- **Challenge name:** SEPC 
- **Category:** Kernel / Module reversing  
- **Difficulty:** Medium  
- **Files included:** `bzImage`, `initramfs.cpio.gz`, `run.sh`  

---
## TL;DR
Extract the supplied root filesystem, examine the user-mode binary to learn how it talks to the kernel, inspect the kernel module for the verification routine, extract the module’s read-only data, and reproduce the module’s transformation offline to verify you can derive the secret.

---
## 1. Files & initial triage

**What to do :**
- Confirm which files were provided and their types. This tells you whether the challenge requires booting a VM or static analysis.

**Commands to run (safe):**
```bash
ls -l
file bzImage initramfs.cpio.gz run.sh
sed -n '1,200p' run.sh
```

<img width="1891" height="727" alt="image" src="https://github.com/user-attachments/assets/f85e8003-9cbc-446b-9b89-6b361b03c1cf" />

- shows the three files (kernel, initramfs, and script) and confirms the script runs a QEMU virtual machine using them.

---

## 2. Extract the root filesystem 

- Extracting the initramfs gives you all embedded user binaries and kernel modules without booting. This is safer and often faster for reversing.
```bash
  mkdir -p /tmp/rev_sepc_init
cd /tmp/rev_sepc_init
gunzip -c /path/to/initramfs.cpio.gz | cpio -idmv
```

<img width="1012" height="492" alt="image" src="https://github.com/user-attachments/assets/50f88d2d-1803-4d44-b315-edc71557becf" />

- Extracted initramfs to a working folder. The extraction reveals a user binary and a kernel object to analyse offline.

---

## 3. Quick reconnaissance on the user binary

- The user-mode program often reveals how it communicates with the kernel (device name, open/write/read behaviour). That narrows the search in the kernel module.
```bash
ls -l checker
file checker
strings checker | head -n 40
# Optionally: strace ./checker (only inside a safe environment if you choose to run it)
```
<img width="1108" height="658" alt="image" src="https://github.com/user-attachments/assets/7802315a-4c5a-499f-b89f-be3124fdfd3f" />

- User binary interacts with a kernel device and writes input per character - indicates the verification happens in the kernel module.

---

## 4. Inspect the kernel module (static analysis pointers)

- The verification logic is likely implemented in the module. Look for functions that read user data and perform comparisons against constants.
```bash
ls -l checker.ko
file checker.ko
strings checker.ko | head -n 40
```

<img width="1673" height="753" alt="image" src="https://github.com/user-attachments/assets/97770263-dbad-486f-9d17-17c8dd695ed7" />

-  The module contains a routine that reads user input and compares it to a computed value built from static data. The disassembly confirms that the verification happens inside the module.

---

## 5. Extract the module’s read-only data

- Static constants used in verification live in the module’s data sections. Extracting these bytes lets you reproduce the module’s computation.

<img width="1077" height="480" alt="image" src="https://github.com/user-attachments/assets/6bacdbc0-8db6-4e53-9e89-19a254ba1c15" />

- objcopy extracted the module’s .rodata into a file named rodata. ls -lh shows the extracted file size, and the hexdump proves the file contains binary data (a block of constants) used by the module.

---

## 6. Reproducing the module’s logic 

- After extracting `.rodata` and inspecting the module, I found that the module builds the expected value by combining two static byte blocks with a simple byte-wise operation (XOR) and then comparing the result to user input.  


- To confirm this safely, I implemented a small offline script that reads the extracted `rodata`, applies the same byte-wise operation to the two blocks, and prints the derived string. Reproducing the operation offline avoids touching the running kernel while verifying the logic.

- The script produced a human-readable string that matches the module’s expected value, confirming the verification is based on static data and a reversible byte-wise transform (XOR). Decoding can therefore be done offline.

- **Flag found**
<img width="542" height="197" alt="image" src="https://github.com/user-attachments/assets/2f14a834-3ae7-4c96-abfe-e51347add059" />



