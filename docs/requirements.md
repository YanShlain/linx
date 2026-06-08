# File scanner

## Confidentiality Notice
Copyright © 2023, Linx Security Inc. All rights reserved. 

This document and the information contained herein is the sole property of Linx Security Inc. This document, including all data, diagrams, and intellectual property contained within, cannot be reproduced, distributed, or copied in any form without the express written permission of Linx Security Inc. 

This document is confidential and intended solely for the use of the individual or entity to whom it is addressed. 

---

## Task
Your task is to design and implement a file scanner. 

### Input
1. Full path to a file/folder in your local file system (string) 
2. Sensitive word (string) 

### Functional Requirements
1. The scanner should support the following file extensions (other files can be skipped): 
    * .txt 
    * .json 
    * .CSV 
    * .docx
    * .pdf 
2. If the file contains the sensitive word, print a proper message with the full file path. 
3. If the given path leads to a folder, the scanner should scan all the files and folders within that folder, recursively. 
4. The scanner should support very large files that cannot be read into memory at once. 
5. The scanner should scan vast and deep directory trees efficiently. 
6. The scanner supports case insensitive, exact word matching. 

#### Matching Example (Sensitive Word: "goat")
| File name | Text | Verdict | Comments |
| :--- | :--- | :--- | :--- |
| a.txt | Does a goat eat meat? | MATCH | Case insensitive match |
| b.txt | GOAT is an abbreviation... | MATCH | Case insensitive match |
| c.txt | Riddle: You go at red... | NO MATCH | go at != goat |
| d.txt | The main part of a goat's... | NO MATCH | goat's != goat |


---

## Assumptions
1. The sensitive word is relatively short, and can be stored as-is in memory. 
2. Single line can be stored as-is in memory. 
3. There's no need to find more than one match in a given file. 
4. If the path doesn't exist, print a proper error message and quit the program. 

## Expectations
1. After you evaluate all the requirements, you should define an MVP (Minimum Viable Product) according to the time you have and your effort estimation.
2. You should implement a fully working solution according to the MVP definition, in any high-level programming language. 
3. Your code should be clear and extensible. 
