# CyberPsychosis — writeup

## Summary
This challenge contained a malicious Linux kernel module called `diamorphine.ko`.  
The module acted like a rootkit: it hid files/processes and provided a secret way to get root permissions.

I analyzed the module statically, found the control functions (`hacked_getdents`, `hacked_kill`), confirmed how it worked at runtime, used the secret signal to gain root, removed the module, and finally read the flag.

> **Note:** I avoid posting the raw flag publicly here. If you want to keep it private, store it elsewhere.

---

## Files provided
- `diamorphine.ko` — the kernel module binary provided by the challenge.

---

## Tools used
- `strings`, `file` — for quick static info.
- `rabin2`, `radare2 (r2)` or `Cutter` — to view symbols and disassemble.
- `ncat` / remote shell — to connect to the challenge host.
- `lsmod`, `cat /sys/module/*` — to inspect loaded kernel modules.
- `rmmod` — to remove the module.
- `find`, `cat` — to locate and read the flag.

---

## Static analysis (what I did)
1. `file diamorphine.ko` — confirmed it is a kernel object (`.ko`).
2. `strings -n 4 diamorphine.ko` — searched for human-readable strings. I saw names like `diamorphine`, `psychosi`, `hacked_getdents`, `hacked_kill`.  
   These names indicate *hooking* of kernel behavior: `getdents` is typically used for directory listing (rootkits hide files here), and `kill` suggests a command interface using signals.
3. `rabin2 -qs diamorphine.ko` and `r2 -A diamorphine.ko` — listed functions and disassembled. I opened `sym.hacked_kill` in `r2` and inspected the code.

**Why `hacked_kill`?**  
- The function name included `kill`.
- The disassembly showed `cmp eax, 0x40` (compare signal number), and calls to `prepare_creds` and `commit_creds` — the classic pattern to replace current process credentials with `root` credentials.
- That pattern explains privilege escalation when a specific signal number is sent.

---

## Dynamic testing (runtime)
1. Connect to the challenge shell: `ncat <host> <port>` (or use the provided access method).
2. Check current user: `id` (shows `uid=1000`).
3. Send the magic signal to the shell: `kill -64 $$` (this sends signal 64 to your current shell process).
4. Check `id` again: now `uid=0` (root) — privilege escalation succeeded.

**Note:** the actual magic signal number may vary by challenge. I read the disassembly and saw the signal checks (for example `cmp eax, 0x40`), which is how I picked `-64`.

---

## Confirming the rootkit
- `lsmod | grep diamorphine` — showed the module loaded.
- `ls -l /sys/module/diamorphine` and `cat /sys/module/diamorphine/*` — gave extra info and kernel log errors (common when probing malicious modules).

---

## Removing the rootkit
- I removed the module: `rmmod diamorphine`.
- Confirmed module was gone: `lsmod | grep diamorphine` returned nothing.

---

## Reading the flag
- With root and after cleanup I searched for typical flag files:
  ```bash
  find / -type f -name "*.txt" 2>/dev/null
  cat /opt/psychosis/flag.txt
