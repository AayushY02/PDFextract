has_eval_phrase :
   search in : all
   search text : "総合評価に関する評価項目"
   if found :
      set(true)
   if not found :
      set(false)

name_bu : 
   search in : all
   search text : "中国地方整備局"
   if found : 
      set("中国地方整備局")

name_of :
   search in : all
   search text : "支出負担行為担当官中国地方整備局長"
   if found :
      set("本官")
   if not found : 
      search in : all
      search text : "分任支出負担行為担当官"
      if found :
         take right:
            search in : taken
            search text : "中国地方整備局"
            if found:
               take right:
                  search in : taken
                  search text : "所長"
                  if found : 
                     take left:
                        remove whitespaces
                        add in right(所)
                        store(var_nameof)
                        set(var_nameof)

「工事名」:
   search in : all
   search text : "工事名"
   if found : 
      take right:
         search in : taken
         search text : "(2)"
         if found : 
            take left : 
               search in : taken
               search text : ("れいわねん" , "れいわど")
               if found : 
                  take left : 
                     replace("(電子入札対象案件)" , "")
                     replace("(電子契約対象案件)" , "")
                     remove whitespaces
                     store(var_kouji)
                     set(var_kouji)
               if not found : 
                  replace("(電子入札対象案件)" , "")
                  replace("(電子契約対象案件)" , "")
                  remove whitespaces
                  store(var_kouji)
                  set(var_kouji)

reg_A : 
   search in : all
   search text : ("4.競争参加資格" , "4. 競争参加資格")
   if found : 
      take right : 
         search in : taken
         search text : ("5. 技術的能力の審査及び総合評価に関する事項", "5.技術的能力の審査及び総合評価に関する事項")
         if found : 
            take left : 
               store(region_A)
         
reg_B : 
   search in : all
   search text : ("5.技術的能力の審査及び総合評価に関する事項", "5. 技術的能力の審査及び総合評価に関する事項")
   if found : 
      take right : 
         store(region_B)

「同種工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      search in : region_A
      search text : ("同種工事とは、下記の" , "同種工事とは、")
      if found : 
         take right :  
            search in : taken
            search text : "なお、同種工事の施工実績は"
            if found : 
               take left : 
                  search in : taken
                  search text : ("(ウ)" , "(イ)")
                  if found : 
                     remove whitespaces
                     replace("下記の" ,"")
                     replace("･" ,"")
                     store(var3)
                     set(var3)  
                  if not found : 
                     remove whitespaces
                     replace("下記の" ,"")
                     replace("･" ,"")
                     replace("の施工実績を有することとする。" ,"")
                     replace("の施工実績を有すること。" ,"")
                     replace("(ア)の要件を満たす工事とする。" ,"")
                     replace("要件を満たす工事とする。" ,"")
                     replace("(ア)" ,"")
                     replace("(ア)" ,"")
                     store(var3)
                     set(var3)  
   if false :
      search in : region_A
      search text : ("同種工事とは、下記の" , "同種工事とは、")
      if found : 
         take right :  
            search in : taken
            search text : "なお、同種工事の施工実績は"
            if found : 
               take left : 
                  search in : taken
                  search text : ("(ウ)" , "(イ)")
                  if found : 
                     remove whitespaces
                     replace("下記の" ,"")
                     replace("･" ,"")
                     store(var3)
                     set(var3)  
                  if not found : 
                     remove whitespaces
                     replace("下記の" ,"")
                     replace("･" ,"")
                     replace("の施工実績を有することとする。" ,"")
                     replace("の施工実績を有すること。" ,"")
                     replace("(ア)の要件を満たす工事とする。" ,"")
                     replace("要件を満たす工事とする。" ,"")
                     replace("(ア)" ,"")
                     replace("(ア)" ,"")
                     store(var3)
                     set(var3)  

「同種工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      search in : region_A
      search text : "元請けとして完成･引き渡しが完了した、下記の同種工事の"
      if found : 
         take right : 
            search in : taken
            search text : "同種工事とは、下記の(ア)の要件を満たす工事とする。"
            if found : 
               take right : 
                  search in : taken
                  search text : "ただし、配置予定技術者"
                  if found : 
                     take left : 
                        remove whitespaces
                        store(temp1)
                        set(temp1)
   if false : 
      search in : all
      search text : ("次の1)~5)に掲げる基準を満たす主任技術者又は監理技術者を当該工事に専任で配置できること" , "次の1)~4)に掲げる基準を満たす主任技術者又は監理技術者を当該工事に専任で配置" , "次の①~④に掲げる基準を満たす主任技術者又は監理技術者を当該工事に専任で配置")
      if found : 
         take right : 
            search in : taken
            search text :  ("完成･引き渡しが完了した、上記(5)の同種工事" , "完成･引渡しが完了した、上記(5)に掲げる同種工事" , "完成･引き渡しが完了した、上記(5)に掲げる同種工事")
            if found : 
               set(「同種工事（企業）」)
            if not found : 
               search in : taken
               search text : "完成･引き渡しが完了した、下記の"
               if found :
                  take right : 
                     search in : taken
                     search text : ("同種工事とは、下記の" , "同種工事とは、")
                     if found : 
                        take right : 
                           search in : taken
                           search text : "ただし、配置予定技術者"
                           if found :
                              take left :
                                 remove whitespaces
                                 store(var4)
                                 set(var4)
      if not found : 
         search in : all
         search text : "基準を満たす主任技術者又は監理技術者を当該工事に"
         if found : 
            take right : 
               search in : taken
               search text : ("に掲げる同種工事の経験を有する者であること。" , "の同種工事の施工実績を有していること。")
               if found : 
                  set(「同種工事（企業）」)


「より同種性が高い（企業）」:  
   check : name_of
   has value : 本官
   if true : 
      search in : region_B
      search text : ("2) 企業の能力等(加算点)" , "2)企業の能力等(加算点)")
      if found : 
         take right :
            search in : taken
            search text : ("①同種工事" , "① 同種工事の")
            if found : 
               take right:
                  search in : taken
                  search text : "| 加 算 点"
                  if found : 
                     take right : 
                        search in : taken
                        search text : ("| 5.0点" , "| 4.0点")
                        if found : 
                           take left :
                              search in : taken
                              search text : "こ れに該当する工事を同種工事として申請する場合 は"
                              if found :
                                 take left : 
                                    remove whitespaces
                                    replace("|", "")
                                    store(var10)
                                    set(var10)
                              if not found :
                                 remove whitespaces
                                 replace("|", "")
                                 store(var10)
                                 set(var10)
      if not found : 
         set("記載なし")
   if false : 
      search in : region_B
      search text : ("2) 企業の能力等(加算点)" , "2)企業の能力等(加算点)")
      if found : 
         take right :
            search in : taken
            search text : ("①同種工事" , "① 同種工事の")
            if found : 
               take right:
                  search in : taken
                  search text : "| 加 算 点"
                  if found : 
                     take right : 
                        search in : taken
                        search text : ("| 5.0点" , "| 4.0点")
                        if found : 
                           take left :
                              search in : taken
                              search text : "こ れに該当する工事を同種工事として申請する場合 は"
                              if found :
                                 take left : 
                                    remove whitespaces
                                    replace("|", "")
                                    store(var10)
                                    set(var10)
                              if not found :
                                 remove whitespaces
                                 replace("|", "")
                                 store(var10)
                                 set(var10)
      if not found : 
         set("記載なし")

                                    

「同種性（企業）」:  
   check : name_of
   has value : 本官
   if true : 
      search in : region_B
      search text : ("2) 企業の能力等(加算点)" , "2)企業の能力等(加算点)")
      if found : 
         take right :
            search in : taken
            search text : ("①同種工事" , "① 同種工事の")
            if found : 
               take right:
                  search in : taken
                  search text : "| 加 算 点"
                  if found : 
                     take right : 
                        search in : taken
                        search text : ("| 5.0点" , "| 4.0点")
                        if found : 
                           take right :
                              search in : taken
                              search text : "| 0.0点"
                              if found : 
                                 take left :
                                    search in : taken
                                    search text : "上記以外"
                                    if found : 
                                       set(「同種工事（企業）」)
                                    if not found : 
                                       remove whitespaces
                                       replace("|", "")
                                       store(var11)
                                       set(var11)
      if not found : 
         set("記載なし")
   if false : 
      search in : region_B
      search text : ("2) 企業の能力等(加算点)" , "2)企業の能力等(加算点)")
      if found : 
         take right :
            search in : taken
            search text : ("①同種工事" , "① 同種工事の")
            if found : 
               take right:
                  search in : taken
                  search text : "| 加 算 点"
                  if found : 
                     take right : 
                        search in : taken
                        search text : ("| 5.0点" , "| 4.0点")
                        if found : 
                           take right :
                              search in : taken
                              search text : "| 0.0点"
                              if found : 
                                 take left :
                                    search in : taken
                                    search text : "上記以外"
                                    if found : 
                                       set(「同種工事（企業）」)
                                    if not found : 
                                       remove whitespaces
                                       replace("|", "")
                                       store(var11)
                                       set(var11)
      if not found : 
         set("記載なし")



「より同種性が高い（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      search in : region_B
      search text : ("2) 企業の能力等(加算点)" , "2)企業の能力等(加算点)")
      if found : 
         take right :
            search in : taken
            search text : "技術者の能力等(加算点)"
            if found : 
               take right :
                  search in : taken
                  search text : ("①同種工事" , "① 同種工事の")
                  if found : 
                     take right:
                        search in : taken
                        search text : "| 加 算 点"
                        if found : 
                           take right : 
                              search in : taken
                              search text : ("| 6.0点" , "| 5.0点" , "| 4.0点")
                              if found : 
                                 take left :
                                    search in : taken
                                    search text : "これに該当する 工事を同種工事として申請する場合は"
                                    if found : 
                                       take left : 
                                          whitespaces
                                          replace("|", "")
                                          store(x)
                                          set(x)
                                    if not found :
                                       remove whitespaces
                                       replace("|", "")
                                       store(x)
                                       set(x)
   if false : 
      search in : region_B
      search text : ("2) 企業の能力等(加算点)" , "2)企業の能力等(加算点)")
      if found : 
         take right :
            search in : taken
            search text : "技術者の能力等(加算点)"
            if found : 
               take right :
                  search in : taken
                  search text : ("①同種工事" , "① 同種工事の")
                  if found : 
                     take right:
                        search in : taken
                        search text : "| 加 算 点"
                        if found : 
                           take right : 
                              search in : taken
                              search text : ("| 6.0点" , "| 5.0点" , "| 4.0点")
                              if found : 
                                 take left :
                                    search in : taken
                                    search text : "これに該当する 工事を同種工事として申請する場合は"
                                    if found : 
                                       take left : 
                                          whitespaces
                                          replace("|", "")
                                          store(x)
                                          set(x)
                                    if not found :
                                       remove whitespaces
                                       replace("|", "")
                                       store(x)
                                       set(x)


                        

「同種性が高い（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      search in : region_B
      search text : "技術者の能力等(加算点)"
      if found : 
         take right :
            search in : taken
            search text : ("①同種工事" , "① 同種工事の")
            if found : 
               take right:
                  search in : taken
                  search text : "| 加 算 点"
                  if found : 
                     take right : 
                        search in : taken
                        search text : ("| 6.0点" , "| 5.0点" , "| 4.0点")
                        if found : 
                           take right :
                              search in : taken
                              search text : ("| 3.0点" , "| 2.0点")
                              if found : 
                                 take left :
                                    remove whitespaces
                                    replace("|", "")
                                    store(y)
                                    set(y)
            if not found : 
               search in : taken
               search text : "配置予定技術者の地域内での施工実績"
               if found :
                  take right : 
                     search in : taken
                     search text : "加算点を与える。"
                     if found : 
                        take left :
                           search in : taken
                           search text : "について"
                           if found : 
                              take left : 
                                 remove whitespaces
                                 store(temp1)
                     search in : taken
                     search text : ("加 算 点 |" , "加 算 点")
                     if found : 
                        take right :
                           search in : taken
                           search text : "| 3.0点"
                           if found : 
                              take left : 
                                 remove whitespaces
                                 replace("|", "")
                                 store(temp2)
                                 add in left("\n")
                                 add in left(temp1)
                                 store(temp3)
                                 set(temp3)
   if false : 
      search in : region_B
      search text : "技術者の能力等(加算点)"
      if found : 
         take right :
            search in : taken
            search text : ("①同種工事" , "① 同種工事の")
            if found : 
               take right:
                  search in : taken
                  search text : "| 加 算 点"
                  if found : 
                     take right : 
                        search in : taken
                        search text : ("| 6.0点" , "| 5.0点" , "| 4.0点")
                        if found : 
                           take right :
                              search in : taken
                              search text : ("| 3.0点" , "| 2.0点")
                              if found : 
                                 take left :
                                    remove whitespaces
                                    replace("|", "")
                                    store(y)
                                    set(y)
            if not found : 
               search in : taken
               search text : "配置予定技術者の地域内での施工実績"
               if found :
                  take right : 
                     search in : taken
                     search text : "加算点を与える。"
                     if found : 
                        take left :
                           search in : taken
                           search text : "について"
                           if found : 
                              take left : 
                                 remove whitespaces
                                 store(temp1)
                     search in : taken
                     search text : ("加 算 点 |" , "加 算 点")
                     if found : 
                        take right :
                           search in : taken
                           search text : "| 3.0点"
                           if found : 
                              take left : 
                                 remove whitespaces
                                 replace("|", "")
                                 store(temp2)
                                 add in left("\n")
                                 add in left(temp1)
                                 store(temp3)
                                 set(temp3)
                                       



「同種性（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      search in : region_B
      search text : "技術者の能力等(加算点)"
      if found : 
         take right :
            search in : taken
            search text : ("①同種工事" , "① 同種工事の")
            if found : 
               take right:
                  search in : taken
                  search text : "| 加 算 点"
                  if found : 
                     take right : 
                        search in : taken
                        search text : ("| 6.0点" , "| 5.0点" , "| 4.0点")
                        if found : 
                           take right :
                              search in : taken
                              search text : ("| 3.0点" , "| 2.0点")
                              if found : 
                                 take right :
                                    search in : taken
                                    search text : "0.0点"
                                    if found : 
                                       take left :
                                          search in : taken
                                          search text : "上記以外"
                                          if found : 
                                             set(「同種工事（技術者）」)
                                          if not found :
                                             remove whitespaces
                                             replace("|", "")
                                             store(y)
                                             set(y)
            if not found : 
               search in : taken
               search text : "配置予定技術者の地域内での施工実績"
               if found :
                  take right : 
                     search in : taken
                     search text : "加算点を与える。"
                     if found : 
                        take left :
                           search in : taken
                           search text : "について"
                           if found : 
                              take left : 
                                 remove whitespaces
                                 store(temp4)
                     search in : taken
                     search text : ("加 算 点 |" , "加 算 点")
                     if found : 
                        take right :
                           search in : taken
                           search text : "| 3.0点"
                           if found : 
                              take right :
                                 search in : taken
                                 search text : "0.0点" 
                                 if found : 
                                    take left : 
                                       remove whitespaces
                                       replace("|", "")
                                       store(temp5)
                                       add in left("\n")
                                       add in left(temp4)
                                       store(temp6)
                                       set(temp6)
   if false : 
      search in : region_B
      search text : "技術者の能力等(加算点)"
      if found : 
         take right :
            search in : taken
            search text : ("①同種工事" , "① 同種工事の")
            if found : 
               take right:
                  search in : taken
                  search text : "| 加 算 点"
                  if found : 
                     take right : 
                        search in : taken
                        search text : ("| 6.0点" , "| 5.0点" , "| 4.0点")
                        if found : 
                           take right :
                              search in : taken
                              search text : ("| 3.0点" , "| 2.0点")
                              if found : 
                                 take right :
                                    search in : taken
                                    search text : "0.0点"
                                    if found : 
                                       take left :
                                          search in : taken
                                          search text : "上記以外"
                                          if found : 
                                             set(「同種工事（技術者）」)
                                          if not found :
                                             remove whitespaces
                                             replace("|", "")
                                             store(y)
                                             set(y)
            if not found : 
               search in : taken
               search text : "配置予定技術者の地域内での施工実績"
               if found :
                  take right : 
                     search in : taken
                     search text : "加算点を与える。"
                     if found : 
                        take left :
                           search in : taken
                           search text : "について"
                           if found : 
                              take left : 
                                 remove whitespaces
                                 store(temp4)
                     search in : taken
                     search text : ("加 算 点 |" , "加 算 点")
                     if found : 
                        take right :
                           search in : taken
                           search text : "| 3.0点"
                           if found : 
                              take right :
                                 search in : taken
                                 search text : "0.0点" 
                                 if found : 
                                    take left : 
                                       remove whitespaces
                                       replace("|", "")
                                       store(temp5)
                                       add in left("\n")
                                       add in left(temp4)
                                       store(temp6)
                                       set(temp6)