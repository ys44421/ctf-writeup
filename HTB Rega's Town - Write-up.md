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
strings rega_town | head -50
```
- This reveals the program's messages and hints at validation mechanisms.

---

### 3. **Pattern Discovery**

Using binary analysis tools, I found that the program checks the input in multiple stages:

First, it verifies the basic flag structure:
- The input must be exactly 33 characters long
- It must start with "HTB{" and end with "}"
- Contains specific character patterns separated by underscores

Then it checks detailed patterns for each section:
- Each part between the underscores has specific rules
- Some parts must start with certain letters
- Some must contain numbers in specific positions
- Character types are strictly enforced (uppercase, lowercase, or digits)

Finally, mathematical validation:
- The program calculates the product of ASCII values for each section
- Compares these products against pre-set target numbers
- All sections must pass both pattern and math checks


<img width="1892" height="202" alt="image" src="https://github.com/user-attachments/assets/fa705455-a7a5-4e2d-a3ed-7c51320ec862" />

---

### 4. **Constraint Analysis**

### **Validation Mechanism Discovery**
Command:
```bash
objdump -t rega_town | grep -i "check\|valid"
```
What We Found:
- Validation Function: check_input - Main validation routine
- Mathematical Function: multiply_characters - Handles ASCII calculations
- Multiple Checkpoints: Series of validation steps

### **How Constraints Are Enforced**

Sequential Validation Flow:
- Length Check - Immediate rejection if not 33 characters
- Format Check - Verifies HTB{} structure
- Pattern Validation - Regex matching for each segment
- Mathematical Verification - ASCII product calculations
- Final Approval - All checks must pass


Key Insight: The constraints work together to create a robust validation system where guessing becomes computationally infeasible without understanding both rule types.

---

### 5. **Automated Solving Approach**

I developed a script that:
- Generates potential character combinations
- Validates against discovered patterns
- Checks mathematical constraints
- Filters valid segments

---

### Solution Strategy

The key was combining:
- Static analysis to identify validation logic
- Constraint solving to find valid combinations
- Pattern recognition to select meaningful results

---

### Tools & Techniques

- Binary analysis utilities for pattern extraction
- Custom scripting for constraint solving
- Systematic validation of potential solutions

---

### Flag
- HTB{...}

---

- Note: This write-up provides the methodology without revealing the complete solution path, maintaining the challenge's educational value while demonstrating the analytical approach.
