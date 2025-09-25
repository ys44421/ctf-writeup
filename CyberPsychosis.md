# CyberPsychosis - writeup

- **CTF name:** HackTheBox 
- **Challenge name:** CyberPsychosis
- **Challenge description:** A malicious Linux kernel module (`diamorphine.ko`) rootkit was provided. The module hides files/processes and contains a secret signal-based way to escalate to root. The task is to analyze the module, disarm it, and find the hidden flag.
- **Challenge category:** Reverse engineering / Kernel rootkit
- **Challenge difficulty:** Easy

---

## Summary
This challenge contained a malicious Linux kernel module called `diamorphine.ko`.  
The module acted like a rootkit: it hid files/processes and provided a secret way to get root permissions.

I analyzed the module statically, found the control functions (`hacked_getdents`, `hacked_kill`), confirmed how it worked at runtime, used the secret signal to gain root, removed the module, and finally read the flag.


---

## Files provided
- `diamorphine.ko` - the kernel module binary provided by the challenge.
<img width="432" height="56" alt="image" src="https://github.com/user-attachments/assets/d2dc56cf-dda4-45c0-a5be-9a2035bbe660" />

---

## Tools used
- `strings`, `file` - for quick static info.
- `rabin2`, `radare2 (r2)` - to view symbols and disassemble.
- `ncat` / remote shell — to connect to the challenge host.
- `lsmod`, `cat /sys/module/*` - to inspect loaded kernel modules.
- `rmmod` - to remove the module.
- `find`, `cat` - to locate and read the flag.

---

## Static analysis (what I did)
1. `file diamorphine.ko` - confirmed it is a kernel object (`.ko`).
2. `strings -n 4 diamorphine.ko` - searched for human-readable strings. I saw names like `diamorphine`, `psychosi`, `hacked_getdents`, `hacked_kill`.  
   These names indicate *hooking* of kernel behavior: `getdents` is typically used for directory listing (rootkits hide files here), and `kill` suggests a command interface using signals.
   <img width="972" height="627" alt="image" src="https://github.com/user-attachments/assets/679786fc-0e3f-4348-8f1c-22bf8e3dd1c2" />

4. `rabin2 -qs diamorphine.ko` and `r2 -A diamorphine.ko` - listed functions and disassembled. I opened `sym.hacked_kill` in `r2` and inspected the code.

**Why `hacked_kill`?**  

- **Name is suspicious.** The function name `hacked_kill` contains `kill` - that hints it hooks or modifies the kernel `kill` behaviour.  
- **Signal checks in disassembly.** In the disassembly we see comparisons like:
  - `cmp eax, 0x2e`  -> `0x2e` = **46**
  - `cmp eax, 0x40`  -> `0x40` = **64**
  That means the function reacts to specific signal numbers instead of normal behaviour.

- **Classic privilege pattern.** The function calls `prepare_creds()` and `commit_creds()` when the 0x40 case is reached.  
  - `prepare_creds()` / `commit_creds()` is the standard kernel pattern to replace the current process credentials - i.e. give the process **root** privileges.

- **What the signal values do (observed & tested):**
  - `kill -46 ` - toggles visibility (unhide/hide files/processes).
  - `kill -64 ` - triggers privilege escalation (become `root`).
  - We use `-46` and `-64` because the code explicitly checks for `0x2e` and `0x40`. `-63` is not used by this module.
 
<img width="1632" height="575" alt="image" src="https://github.com/user-attachments/assets/30f511cb-ddb9-484e-8b9d-283344f6bdd0" />

---

## Dynamic testing (runtime)
1. Connect to the challenge shell: `ncat <host> <port>` (or use the provided access method).
2. Check current user: `id` (shows `uid=1000`).
3. Send the magic signal to the shell: `kill -64 $$` (this sends signal 64 to your current shell process).
4. Check `id` again: now `uid=0` (root) - privilege escalation succeeded.

**Note:** The actual magic signal number may vary by challenge. I read the disassembly and saw the signal checks (for example `cmp eax, 0x40`), which is how I picked `-64`.

<img width="642" height="360" alt="image" src="https://github.com/user-attachments/assets/53b00a11-561c-436a-9369-3af880e257ee" />

---
## Control the rootkit (make it visible & get root)
- This rootkit uses special Unix signals as a control channel. Important commands I ran:
- Reveal hidden files/processes:
  ```
  kill -46 0
  ```
  *Explanation:* Many rootkits use a signal to toggle visibility (some use `-63`), but this particular module was compiled to use signal **46**, so you must send the exact signal it expects.
- Elevate current shell to root:
  ```
  kill -64 $$
  ```
  *Explanation:* The module checks the signal number in the kernel function and, for the configured value, it calls `prepare_creds`/`commit_creds` to give the calling process root privileges.
- Check that the module is loaded:
  ```
  lsmod | grep diamorphine
  ```
- Remove the kernel module (cleanup):
  ```
  rmmod diamorphine
  ```
## Finally - find the flag:

- Search for text files (possible flag)
  ```
  find / -type f -name "*.txt" 2>/dev/null
- Read the flag file:
  ```
   cat /opt/psychosis/flag.txt
- Result: flag found in /opt/psychosis/flag.txt
  <img width="812" height="363" alt="image" src="https://github.com/user-attachments/assets/cafdc3cb-068f-48d3-838f-7a17ae898453" />


