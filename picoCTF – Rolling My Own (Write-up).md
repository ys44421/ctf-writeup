# picoCTF - Rolling My Own 

---

- **Challenge:** Rolling My Own  
- **Category:** Reverse Engineering 
- **Difficulty:** Hard
- **Challenge description:** A small service generates executable code from MD5 outputs derived from the user password and embedded salts. If the produced code calls the flag printing function with the expected argument, the service prints the flag.

---

## Tools & environment
- Ghidra for static analysis  
- `objdump`, `readelf` for quick evidence extraction  
- Python 3 for automation  
- `nc` for testing the remote service  
- Isolated Kali VM for safe execution

---

# High-level summary (what the binary does)
- Reads user password with `fgets`.  
- Builds `local_58` as 4 × (4-byte password chunk + 8-byte salt).  
- Computes MD5 for each 12-byte chunk.  
- Extracts 4 bytes from each MD5 at offsets `[8,2,7,1]` → forms a 16-byte blob.  
- Maps an executable page, writes that 16-byte blob, and executes it.  
- The flag prints only if the called function receives `rdi == 0x7b3dc26f1`.

```
/* FUN_00100b6a — reads password, concatenates 4×(4-byte chunk + 8-byte salt), computes hashes, extracts bytes and executes the resulting 16-byte blob. */

undefined8 FUN_00100b6a(void)

{
    size_t sVar1;
    void *__ptr;
    undefined8 *puVar2;
    long in_FS_OFFSET;
    int local_100;
    int local_fc;
    int local_e8 [4];
    undefined8 local_d8;
    undefined8 local_d0;
    undefined8 local_c8;
    undefined8 local_c0;
    undefined8 local_b8;
    undefined8 local_b0;
    undefined local_a8;
    char acStack153 [65];
    char local_58 [72];
    long local_10;
    
    local_10 = *(long *)(in_FS_OFFSET + 0x28);
    setbuf(stdout,(char *)0x0);
    local_c8 = 0x57456a4d614c7047;
    local_c0 = 0x6b6d6e6e6a4f5670;
    local_b8 = 0x367064656c694752;
    local_b0 = 0x736c787a6563764d;
    local_a8 = 0;
    local_e8[0] = 8;
    local_e8[1] = 2;
    local_e8[2] = 7;
    local_e8[3] = 1;
    memset(acStack153 + 1,0,0x40);
    memset(local_58,0,0x40);
    printf("Password: ");
    fgets(acStack153 + 1,0x40,stdin);
    sVar1 = strlen(acStack153 + 1);
    acStack153[sVar1] = '\0';
    local_100 = 0;
    while (local_100 < 4) {
        strncat(local_58,acStack153 + (long)(local_100 << 2) + 1,4);
        strncat(local_58,(char *)((long)&local_c8 + (long)(local_100 << 3)),8);
        local_100 = local_100 + 1;
    }
    __ptr = malloc(0x40);
    sVar1 = strlen(local_58);
    FUN_00100e3e(__ptr,local_58,sVar1 & 0xffffffff);
    local_100 = 0;
    while (local_100 < 4) {
        local_fc = 0;
        while (local_fc < 4) {
        *(undefined *)((long)&local_d8 + (long)(local_fc * 4 + local_100)) =
            *(undefined *)((long)__ptr + (long)(local_e8[local_fc] + local_fc * 0x10 + local_100));
        local_fc = local_fc + 1;
        }
        local_100 = local_100 + 1;
    }
    puVar2 = (undefined8 *)mmap((void *)0x0,0x10,7,0x22,-1,0);
    *puVar2 = local_d8;
    puVar2[1] = local_d0;
    (*(code *)puVar2)(FUN_0010102b);
    free(__ptr);
    if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                        /* WARNING: Subroutine does not return */
        __stack_chk_fail();
    }
    return 0;
}
```

```
/* FUN_00100e3e — splits the input into 12-byte blocks and computes MD5 for each block (stores MD5 outputs). */

void FUN_00100e3e(long param_1,void *param_2,int param_3)

{
    int iVar1;
    uint uVar2;
    int iVar3;
    long in_FS_OFFSET;
    void *local_a8;
    int local_98;
    int local_94;
    int local_90;
    MD5_CTX local_88;
    uchar local_28 [24];
    long local_10;
    
    local_10 = *(long *)(in_FS_OFFSET + 0x28);
    if (param_3 % 0xc == 0) {
        iVar1 = param_3 / 0xc;
    }
    else {
        iVar1 = param_3 / 0xc + 1;
    }
    local_98 = 0;
    local_a8 = param_2;
    while (local_98 < iVar1) {
        local_90 = 0xc;
        if ((local_98 == iVar1 + -1) && (param_3 % 0xc != 0)) {
        local_90 = iVar1 % 0xc;
        }
        MD5_Init(&local_88);
        MD5_Update(&local_88,local_a8,(long)local_90);
        local_a8 = (void *)((long)local_a8 + (long)local_90);
        MD5_Final(local_28,&local_88);
        local_94 = 0;
        while (local_94 < 0x10) {
        iVar3 = local_98 * 0x10 + local_94;
        uVar2 = (uint)(iVar3 >> 0x1f) >> 0x1a;
        *(uchar *)((int)((iVar3 + uVar2 & 0x3f) - uVar2) + param_1) = local_28[local_94];
        local_94 = local_94 + 1;
        }
        local_98 = local_98 + 1;
    }
    if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                        /* WARNING: Subroutine does not return */
        __stack_chk_fail();
    }
    return;
}
```

```
/* FUN_0010102b — flag-print function: prints flag only when called with param == 0x7b3dc26f1. */

void FUN_0010102b(long param_1)

{
    FILE *__stream;
    long in_FS_OFFSET;
    char local_98 [136];
    long local_10;
    
    local_10 = *(long *)(in_FS_OFFSET + 0x28);
    if (param_1 == 0x7b3dc26f1) {
        __stream = fopen("flag","r");
        if (__stream == (FILE *)0x0) {
        puts("Flag file not found. Contact an admin.");
                        /* WARNING: Subroutine does not return */
        exit(1);
        }
        fgets(local_98,0x80,__stream);
        puts(local_98);
    }
    else {
        puts("Hmmmmmm... not quite");
    }
    if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                        /* WARNING: Subroutine does not return */
        __stack_chk_fail();
    }
    return;
}
```

- NOTE: Full decompiler output included for reproducibility; see the short "High-level summary" above for the concise explanation. 

---

## What I found in the binary (evidence pointers)
- Four 64-bit immediates (salts) embedded in the code :  
  `0x57456a4d614c7047`, `0x6b6d6e6e6a4f5670`, `0x367064656c694752`, `0x736c787a6563764d`.  
- These immediates decode (little-endian) to ASCII salts used by the program ( `GpLaMjEW`, ...).  
- The program picks byte slices from each MD5 output using offsets `[8,2,7,1]`.

```
local_e8[0] = 8;
local_e8[1] = 2;
local_e8[2] = 7;
local_e8[3] = 1;       
```

---

## Approach (how I investigated — pointers)

1. Locate salts and `Password:` string in `.rodata`.
```
In FUN_00100b6a
local_c8 = 0x57456a4d614c7047;
local_c0 = 0x6b6d6e6e6a4f5670;
local_b8 = 0x367064656c694752;
local_b0 = 0x736c787a6563764d;
```
2. Confirm the concat -> MD5 -> extract -> exec pipeline (via decompiler).
```
In FUN_00100e3e:
MD5_Init(&local_88);
MD5_Update(&local_88,local_a8,(long)local_90);
local_a8 = (void *)((long)local_a8 + (long)local_90);
MD5_Final(local_28,&local_88);
```
3. Note offsets used to extract bytes from MD5 outputs.
```
 while (local_fc < 4) {
        *(undefined *)((long)&local_d8 + (long)(local_fc * 4 + local_100)) =
            *(undefined *)((long)__ptr + (long)(local_e8[local_fc] + local_fc * 0x10 + local_100));
        local_fc = local_fc + 1;
        }
        local_100 = local_100 + 1;
```

4. Reduce search complexity by recovering each 4-byte chunk independently (each MD5 depends only on `chunk + salt`).
> Each MD5 hashes a 12-byte block formed by a 4-byte password chunk + its 8-byte salt, so each 4-byte chunk can be recovered independently.
5. Automate chunk search: for each 4-char candidate, compute `MD5(candidate + salt)` and compare the relevant 4-byte slice.
 - If the slice matches the expected bytes, record the candidate and proceed to the next chunk.


---

## Automation (what I implemented)
- A Python script that:
- Iterates all 4-char candidates (configurable charset) per chunk.  
- For each candidate: `candidate_block = candidate + salt`, compute `MD5(candidate_block)`.  
- Compare the MD5 hex slice at the configured offset to target hex; if matched, record the chunk.  
- Assemble the full password from the known prefix and recovered chunks.

---
## Verification
- After assembling candidate password from recovered chunks, I tested the remote service and confirmed the execution path that prints the flag.  

```
nc mercury.picoctf.net 47110
Password: D1v1..........
picoCTF{.....}
```

---

## Useful commands

```
# Inspect rodata and strings
readelf -x .rodata remote
objdump -s -j .rodata remote

# Find imm64 constants in disassembly
objdump -d remote | egrep -n 'mov(abs)?\s+.*0x[0-9a-f]{12,16}'

# Search for MD5 usage
objdump -d remote | egrep -n 'MD5_Init|MD5_Update|MD5_Final'
```

---
**End of write-up**
                                  









