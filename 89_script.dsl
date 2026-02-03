file_1:
   search in : all
   search text : "=== FIRST FILE START:"
   if found : 
      take right : 
         search in : taken
         search text : "=== SECOND FILE START:"
         if found : 
            take left : 
               search in : taken
               search text : ".txt ==="
               if found : 
                  take right :
                     store(file1)

file_2:
   search in : all
   search text : "=== SECOND FILE START:"
   if found : 
      take right : 
         search in : taken
         search text : "=== END OF DOCUMENT ==="
         if found : 
            take left : 
               search in : taken
               search text : ".txt ==="
               if found : 
                  take right :
                     store(file2)



has_eval_phrase :
   search in : all
   search text : "総合評価に関する事項"
   if found :
      set(true)
   if not found :
      set(false)

name_bu : 
   search in : file1
   search text : "九州地方整備局"
   if found : 
      set("九州地方整備局")

name_of :
   search in : file1
   search text : "what_to_use"
   if found :
      set("本官")  
   if not found : 
      search in : file1
      search text : "支出負担行為担当官"
      if found :
         take right :
            search in : taken
            search text : "九州地方整備局"
            if found:
               take right:
                  search in : taken
                  search text : "長"
                  if found : 
                     take left :
                        remove whitespaces
                        add in right(所)
                        store(var_nameof)
                        set(var_nameof)

「工事名」:
   search in : file1
   search text : "工 事 名"
   if found : 
      take right :
         search in : taken
         search text : ("(2) 工事場所" , "(2)工事場所" , "(3)工事場所")
         if found : 
            take left : 
               search in : taken
               search text : ("(電子入札及び電子契約対象案件)" , "2)" , "【B】")
               if found : 
                  take left :
                     remove whitespaces
                     replace("【A】" , "")
                     replace("1)" , "")
                     store(var_kouji)
                     set(var_kouji)
               if not found : 
                  remove whitespaces
                  replace("【A】" , "")
                  replace("1)" , "")
                  store(var_kouji)
                  set(var_kouji)

reg_A : 
   search in : file1
   search text : "2 競争参加資格"
   if found : 
      take right : 
         search in : taken
         search text : "3 総合評価に関する事項等"
         if found : 
            take left : 
               store(region_A)
         
reg_B : 
   search in : file1
   search text : "3 総合評価に関する事項等"
   if found : 
      take right : 
         store(region_B)

「同種工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")    
   if false:
      search in : region_A
      search text : "元請けとして次に掲げるア)の要件を満たす同種工事の施工実績を有すること。"
      if found : 
         take right : 
            search in : taken
            search text : "分担工事の経験であること。)"
            if found : 
               take right :
                  search in : taken
                  search text : "ただし、経常建設共同企業体"
                  if found : 
                     take left : 
                        remove whitespaces
                        replace("の施工実績を有すること。" , "")
                        replace("を有すること。" , "")
                        replace("ア)" , "")
                        store(doushi_kouji_1)
                        set(doushi_kouji_1)    
      if not found : 
         search in : region_A
         search text : "元請けとして次に掲げるア)~ウ)"
         if found : 
            take right : 
               search in : taken
               search text : "分担工事の経験であること。)"
               if found : 
                  take right :
                     search in : taken
                     search text : "ただし、経常建設共同企業体"
                     if found : 
                        take left : 
                           search in : taken
                           search text : "ただし、"
                           if found : 
                              take right : 
                                 remove whitespaces
                                 store(doushi_kouji_1)
                                 set(doushi_kouji_1)    
                           if not found : 
                              remove whitespaces
                              store(doushi_kouji_1)
                              set(doushi_kouji_1) 

「同種工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")    
   if false:
      search in : region_A
      search text : "次に掲げる基準を満たす主任技術者又は監理技術者を当該工事に配置できること。"
      if found : 
         take right : 
            search in : taken
            search text : ("上記(4)に掲げる同種工事の経験を有する者であること。" , "上記(5)に掲げる同種工事の経験を有する者であること。" , "上記(4)に掲げる同種工事の経験を有")
            if found : 
               set(「同種工事（企業）」)


「同種性が認められる工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")
   if false:
      search in : file2
      search text : "(5) 総合評価の評価項目"
      if found : 
         take right : 
            search in : taken
            search text : "[配置予定技術者の能"
            if found : 
               take right :
                  search in : taken
                  search text : "① 元請けとして、平成21年度以降に完成した工事で"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "同種性が認められる工事"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "より同種性の高い工事"
                              if found : 
                                 take left : 
                                    remove whitespaces
                                    replace("を有すること。" , "")
                                    replace("の施工実績。" , "")
                                    store(doushi_kouji_1)
                                    set(doushi_kouji_1)

「より同種性の高い工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")
   if false:
      search in : file2
      search text : "(5) 総合評価の評価項目"
      if found : 
         take right : 
            search in : taken
            search text : "[配置予定技術者の能"
            if found : 
               take right :
                  search in : taken
                  search text : "① 元請けとして、平成21年度以降に完成した工事で"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "| より同種性の高い工事 |" 
                        if found : 
                           take right : 
                              search in : taken
                              search text : "| 同種性が認められる工事 |"
                              if found : 
                                 take left : 
                                    remove whitespaces
                                    replace("|" , "")
                                    replace("を有すること。" , "")
                                    replace("の施工実績。" , "")
                                    store(doushi_kouji_1)
                                    set(doushi_kouji_1)
                              if not found : 
                                 search in : taken
                                 search text : "② 当該実績"
                                 if found : 
                                    take left : 
                                       remove whitespaces
                                       replace("を有すること。" , "")
                                       replace("|" , "")
                                       replace("の施工実績。" , "")
                                       store(doushi_kouji_1)
                                       set(doushi_kouji_1)
                        if not found : 
                           search in : taken
                           search text : "より同種性の高い工事"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "| 同種性が認められる工事 |"
                                 if found : 
                                    take left : 
                                       remove whitespaces
                                       replace("|" , "")
                                       replace("を有すること。" , "")
                                       replace("の施工実績。" , "")
                                       store(doushi_kouji_1)
                                       set(doushi_kouji_1)
                                 if not found : 
                                    search in : taken
                                    search text : "② 当該実績"
                                    if found : 
                                       take left : 
                                          remove whitespaces
                                          replace("を有すること。" , "")
                                          replace("|" , "")
                                          replace("の施工実績。" , "")
                                          store(doushi_kouji_1)
                                          set(doushi_kouji_1)



「同種性が認められる工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")
   if false:
      search in : file2
      search text : "(5) 総合評価の評価項目"
      if found : 
         take right : 
            search in : taken
            search text : "[企業の能力等]"
            if found : 
               take right :
                  search in : taken
                  search text : "① 参加資格要件の同種工事"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "同種性が認められる工事"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "より同種性の高い工事"
                              if found : 
                                 take left : 
                                    remove whitespaces
                                    replace("を有すること。" , "")
                                    replace("の施工実績。" , "")
                                    store(doushi_kouji_1)
                                    set(doushi_kouji_1)
                              if not found : 
                                 search in : taken
                                 search text : "② 評価は"

「より同種性の高い工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")
   if false:
      search in : file2
      search text : "(5) 総合評価の評価項目"
      if found : 
         take right : 
            search in : taken
            search text : "[企業の能力等]"
            if found : 
               take right :
                  search in : taken
                  search text : "① 参加資格要件の同種工事"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "より同種性の高い工事"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "同種性の高い工事"
                              if found : 
                                 take left : 
                                    remove whitespaces
                                    replace("を有すること。" , "")
                                    replace("の施工実績。" , "")
                                    store(doushi_kouji_1)
                                    set(doushi_kouji_1)

「同種性の高い工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")
   if false:
      search in : file2
      search text : "(5) 総合評価の評価項目"
      if found : 
         take right : 
            search in : taken
            search text : "[企業の能力等]"
            if found : 
               take right :
                  search in : taken
                  search text : "① 参加資格要件の同種工事"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "より同種性の高い工事"
                        if found : 
                           take right : 
                              search in : taken
                              search text : " 同種性の高い工事"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "② 評価は"
                                    if found : 
                                       take left :
                                          remove whitespaces
                                          replace("を有すること。" , "")
                                          replace("の施工実績。" , "")
                                          store(doushi_kouji_1)
                                          set(doushi_kouji_1)



    

