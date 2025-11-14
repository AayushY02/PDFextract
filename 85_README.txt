
How to use (quick start)

1) Download the two files:
   - extractor.py
   - rules_chubu.yaml

2) Put your input text as UTF-8, e.g. "input.txt".

3) Run:
   python extractor.py --rules rules_chubu.yaml --input input.txt

What comes out:
- Prints file name/length up front.
- Prints whether certain markers are present.
- Emits the extracted fields line-by-line, e.g.:
    name_of: 本官
    工事名: 〇〇道路改良工事（その２）
    同種工事（企業）: 「同種工事（企業）」......
    同種工事（技術者）: 「同種工事（技術者）」......
    より同種性の高い: 「より同種性の高い」...... or 該当なし.

Customize:
- Open rules_chubu.yaml and tweak phrases, add or remove ops.
- Common ops: find_after, take_before, copy/restore buffer, strip/compact whitespace, emit key/values, if_var branching.

Notes:
- Ops are safe: if a pattern isn't found, the op just no-ops (keeps going).
- For more complex needs, duplicate this YAML for other regions (e.g., rules_kanto.yaml) and adjust markers.



85_script


has_eval_phrase : 
   search in : all
   search text : 入札の評価に関する基準及び得点配分
   if found : set(true)
   if not found : set(false)

name_of :
   search in first : 20
   search text : 入札公告（建設工事）
   if found : set(本官)
   if not found : 
      search in : all
      search text : 分任支出負担行為担当官
      if found :
         take right
            search in : taken
            search text : 中部地方整備局
            if found:
               take right:
                  search in : taken
                  search text : 所長
                  if found : 
                     remove whitespaces
                     add in right(所)
                     store(var)
                     set(var)

工事名:
   search in : all
   search text : 工事名
   if found : 
      take right:
         search in : taken
         search text : (2)
         if found : 
            take left : 
               search in : taken
               search text : （電子入札対象案件）
               if found : 
                  take left :
                     remove whitespaces
                     store(var2)
                     set(var2)


「同種工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text :  [【企業】,【技術者】]
      if found : 
         search in : all
         search text : 発注者から企業に対して通知された評定点が
         if found : 
            take right : 
               search in : taken
               search text : 【企業】
               if found : 
                  take right : 
                     search in : taken
                     search text : 同種工事：
                     if found : 
                        take right : 
                           search in : taken
                           search text : 【技術者】
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : 同種工事：
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : (5)
                                       if found : 
                                          take left : 
                                             search in : taken
                                             search text : (6)
                                             if found : 
                                                take left : 
                                                   remove whitespaces
                                                   store(var4)
                                                   set(var4)
      if not found : 
         set(特殊工事のため要確認)
   if false:
      search in: all
      search text: 元請けとして、以下に示す同種工事
      if found : 
         take right : 
            search in : taken
            search text : 【企業】
            if found : 
               take right : 
                  search in : taken
                  seach text : 同種工事：
                  if found : 
                     take right : 
                        search in : taken
                        seach text : 【技術者】
                        if found : 
                           take right : 
                              search in : taken
                              search text : 同種工事：
                              if found : 
                                 take right: 
                                    search in : taken
                                    search text : (5)
                                    if found : 
                                       take left : 
                                          remove whitespaces
                                          store(var3)
                                          set(var3)

                                       
同種工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text :  [【企業】,【技術者】]
      if found : 
         search in : all
         search text : 発注者から企業に対して通知された評定点が
         if found : 
            take right : 
               search in : taken
               search text : 【企業】
               if found : 
                  take right : 
                     search in : taken
                     search text : 同種工事：
                     if found : 
                        take left : 
                           search in : taken
                           search text : 【技術者】
                           if found : 
                              take left : 
                                 remove whitespaces
                                 store(var5)
                                 set(var5)
      if not found : 
         seach in : all
         search text : 発注者から企業に対して通知された評定点が
         if found : 
            take right : 
               search in : taken
               search text : 同種工事：
               if found : 
                  take right : 
                     search in : taken
                     search text : (6)
                     if found : 
                        take left : 
                           remove whitespaces
                           store(var6)
                           set(var6)
   if false:
      search in: all
      search text: 元請けとして、以下に示す同種工事
      if found : 
         take right : 
            search in : taken
            search text : 【企業】
            if found : 
               take right : 
                  search in : taken
                  seach text : 同種工事：
                  if found : 
                     take right : 
                        search in : taken
                        seach text : 【技術者】
                        if found : 
                           take left : 
                              remove whitespaces
                              store(var7)
                              set(var7)

                     
「より同種性の高い」:
   search in : all
   search text : [※１： , を「より同種性が高い」と評価]
   if found : 
      search in : all 
      search text : ※１：
      if found : 
         take right : 
            search in : taken
            search text : 同種工事のうち、
            if found : 
               take right : 
                  search in : taken
                  search text : を「より同種性が高い」と評価
                  if found : 
                     take left : 
                        remove whitespaces
                        store(var8)
                        set(var8)
   if not found : 
      set(該当なし)















i developed my own script design and want to use this : 

85_script


has_eval_phrase : 
   search in : all
   search text : 入札の評価に関する基準及び得点配分
   if found : set(true)
   if not found : set(false)

name_of :
   search in first : 20
   search text : 入札公告（建設工事）
   if found : set(本官)
   if not found : 
      search in : all
      search text : 分任支出負担行為担当官
      if found :
         take right
            search in : taken
            search text : 中部地方整備局
            if found:
               take right:
                  search in : taken
                  search text : 所長
                  if found : 
                     remove whitespaces
                     add in right(所)
                     store(var)
                     set(var)

工事名:
   search in : all
   search text : 工事名
   if found : 
      take right:
         search in : taken
         search text : (2)
         if found : 
            take left : 
               search in : taken
               search text : （電子入札対象案件）
               if found : 
                  take left :
                     remove whitespaces
                     store(var2)
                     set(var2)


「同種工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text :  [【企業】,【技術者】]
      if found : 
         search in : all
         search text : 発注者から企業に対して通知された評定点が
         if found : 
            take right : 
               search in : taken
               search text : 【企業】
               if found : 
                  take right : 
                     search in : taken
                     search text : 同種工事：
                     if found : 
                        take right : 
                           search in : taken
                           search text : 【技術者】
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : 同種工事：
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : (5)
                                       if found : 
                                          take left : 
                                             search in : taken
                                             search text : (6)
                                             if found : 
                                                take left : 
                                                   remove whitespaces
                                                   store(var4)
                                                   set(var4)
      if not found : 
         set(特殊工事のため要確認)
   if false:
      search in: all
      search text: 元請けとして、以下に示す同種工事
      if found : 
         take right : 
            search in : taken
            search text : 【企業】
            if found : 
               take right : 
                  search in : taken
                  seach text : 同種工事：
                  if found : 
                     take right : 
                        search in : taken
                        seach text : 【技術者】
                        if found : 
                           take right : 
                              search in : taken
                              search text : 同種工事：
                              if found : 
                                 take right: 
                                    search in : taken
                                    search text : (5)
                                    if found : 
                                       take left : 
                                          remove whitespaces
                                          store(var3)
                                          set(var3)

                                       
同種工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text :  [【企業】,【技術者】]
      if found : 
         search in : all
         search text : 発注者から企業に対して通知された評定点が
         if found : 
            take right : 
               search in : taken
               search text : 【企業】
               if found : 
                  take right : 
                     search in : taken
                     search text : 同種工事：
                     if found : 
                        take left : 
                           search in : taken
                           search text : 【技術者】
                           if found : 
                              take left : 
                                 remove whitespaces
                                 store(var5)
                                 set(var5)
      if not found : 
         seach in : all
         search text : 発注者から企業に対して通知された評定点が
         if found : 
            take right : 
               search in : taken
               search text : 同種工事：
               if found : 
                  take right : 
                     search in : taken
                     search text : (6)
                     if found : 
                        take left : 
                           remove whitespaces
                           store(var6)
                           set(var6)
   if false:
      search in: all
      search text: 元請けとして、以下に示す同種工事
      if found : 
         take right : 
            search in : taken
            search text : 【企業】
            if found : 
               take right : 
                  search in : taken
                  seach text : 同種工事：
                  if found : 
                     take right : 
                        search in : taken
                        seach text : 【技術者】
                        if found : 
                           take left : 
                              remove whitespaces
                              store(var7)
                              set(var7)

                     
「より同種性の高い」:
   search in : all
   search text : [※１： , を「より同種性が高い」と評価]
   if found : 
      search in : all 
      search text : ※１：
      if found : 
         take right : 
            search in : taken
            search text : 同種工事のうち、
            if found : 
               take right : 
                  search in : taken
                  search text : を「より同種性が高い」と評価
                  if found : 
                     take left : 
                        remove whitespaces
                        store(var8)
                        set(var8)
   if not found : 
      set(該当なし)





here is the definition : 

indentations play a major role in this, but you can suggest me different formats if necessary

if there is no indent, ie the first column has_eval_phrase : - this act as a variable whose value we are calculating and whose value we will be printing at the end.

everything inside this (with indents) is how we calculate the value for this variable.

search in and search text - these are used to define the range in which we want to do a text search

search in : all -  means searching the entire text
search in : taken - means we search in taken text from previous step.

search text : xx - means that we will be searching the text xx in the defined range

if found and if not found:
these are used with search in and search text, when we want to define what to do if the text was found (if found) , or not found (if not found). the indets text inside this defines the process to do if found and if not found.

then there is  search text : [xx , yy]
this means we want to search both the things xx and yy and this gives true if both xx and yy are found. there if both are found in the text we move to if found section else if not found section.

take left, take right :

after searching a text , if it is found we can do partition by taking the part after that particular searched word (take right) or part before that searched word (take left). then the further process inside these will be done on the text we took ( either left or right )

remove whitespaces : 

remove all the whitespaces from left and right of the text we have taken . currently using text

add in right(xx) , add in left(xx) : 

add the xx text to the right / left of the taken / remaining text

store(var) :

store the remaining / taken text in a variable , var is the name of that variable

set(xx) :

this store the xx value in the original variable we are calculating. this does it directly from any part of the calcuation to its uppermost main variable (one which will be printed in the end). 



i want you to help me develop a python file which could understand this kind of script and run it accordingly in the way defined in the script.

