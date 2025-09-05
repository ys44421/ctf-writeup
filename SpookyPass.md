#SpookyPass | HackTheBox (Reversing Challenge)

**Category**: Reversing | **Difficulty**: Very Easy  
**ZIP Password**: `hackthebox` | **Released**: 295 Days Ago

---
## overview  

SpookyPass is a very easy reversing challenge from HackTheBox. The challenge provides a zipped binary file protected with a password. The goal is to analyze the binary, identify the required password, and retrieve the hidden flag.

---

##  Steps & Thought Process

### 1. Download the challenge file
From the HackTheBox challenge page, I downloaded `SpookyPass.zip`.  
The page also provided the **ZIP password**:  

---
### 2. Unzip the challenge
I extracted the file with: unzip SpookyPass.zip
This created a folder rev_spookypass containing the binary file pass.

---
### 3. Inspect the binary with strings
strings rev_spookypass/pass | less
Inside the output, I noticed several library function names (e.g., `puts`, `strcmp`, `printf`) and text strings used by the program.  
Among them, I found a **hardcoded password string**:
This clearly looked like the required input for the program.

---
### 4. Run the binary and test the password
When prompted, I entered the extracted password: s3cr3t_p455_f0r_gh05t5_4nd_gh0ul5
The program then revealed the flag: HTB{un0bfu5c4t3d_5tr1ng5}

---
##  Conclusion
This challenge demonstrated how even simple tools like `strings` can solve beginner-level reversing tasks.  
By carefully examining the binary output, I was able to identify the hardcoded password, use it to run the program, and finally retrieve the flag. 

---
### Key takeaways:
- Always start with basic static analysis (`file`, `strings`) before moving to advanced tools.
- Many beginner reversing challenges hide secrets directly as plain text.
- Clear documentation of each step ensures reproducibility and better learning.

