# HTB Rega's Town Write-up

---
## Challenge Information

- Name: Rega's Town
- Type: Reverse Engineering
- Difficulty: Medium
- Platform: Hack The Box

---

## Challenge Overview

- Rega's Town is a reverse engineering challenge where we need to find the correct flag by analyzing a binary that validates input using regex patterns and mathematical constraints.

---

## Key Steps to Solution

### 1. **Initial Binary Analysis**
- Start by examining the binary type and behavior
- The program requests a passphrase and validates input

<img width="1900" height="411" alt="image" src="https://github.com/user-attachments/assets/248702ca-cf1f-4470-ab1a-0f81540337b0" />

--- 

### 2. **String Extraction**

```bash
strings rega_town | grep -E "Welcome|Enter|Correct|Maybe" | head -5
```
- This reveals the program's messages and hints at validation mechanisms.

<img width="1902" height="397" alt="image" src="https://github.com/user-attachments/assets/3cddc93b-7899-4908-b618-2e09e13d25ab" />

---

### 3. Pattern & Technical Discovery

**Binary Analysis Commands:**
```bash
# Locate regex patterns using radare2
r2 rega_town
[0x00000000]> aaa
[0x00000000]> izz | grep -A10 "Welcome to our secret town"

# Find validation functions using objdump
objdump -t rega_town | grep -E "check|multiply"
```



Multi-Stage Validation Discovered:
- ^.{33}$ - Input must be exactly 33 characters long
- (?:^[H][T][B]).* - Must start with "HTB"
- Contains specific character patterns separated by underscores

Second Stage - Detailed Patterns:
- Each of the 7 segments has specific regex rules
- Character type enforcement (uppercase, lowercase, digits)
- Position-based constraints

Third Stage - Mathematical Validation:
- ASCII value multiplication for each segment
- Comparison with hardcoded numerical targets
- All segments must pass both pattern and math checks

<img width="1892" height="202" alt="image" src="https://github.com/user-attachments/assets/fa705455-a7a5-4e2d-a3ed-7c51320ec862" />

Key Insight: The dual-constraint system makes brute-force impractical, requiring understanding of both structural and mathematical rules.



### 5. Automated Solving Approach

**Script Logic:**
1. Generate combinations using discovered regex constraints
2. Calculate ASCII products for validation
3. Filter results to meaningful English words
4. Verify against original binary

---

### Solution Strategy

The key was combining:
- Static analysis to identify validation logic
- Constraint solving to find valid combinations
- Pattern recognition to select meaningful results

---

### Tools & Techniques

- Radare2 - Deep binary analysis and pattern extraction
- objdump/strings - Initial reconnaissance and function discovery
- Python - Automated constraint solving and validation
- Systematic Testing - Iterative verification approach

---

### Flag
- HTB{...}

---

- Note: This write-up provides the methodology without revealing the complete solution path, maintaining the challenge's educational value while demonstrating the analytical approach.
