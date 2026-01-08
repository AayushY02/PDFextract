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
               search text : "(電子入札対象案件)"
               if found : 
                  take left :
                     search in : taken
                     search text : "れいわねん"
                     if found : 
                        take left : 
                           remove whitespaces
                           store(var_kouji)
                           set(var_kouji)
                     if not found : 
                        take left : 
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

「同種工事(企業)」:
   search in : region_A
   search text : ("同種工事とは、下記の" , "同種工事とは、")
   if found : 
      take right :  
         search in : taken
         search text : "なお、同種工事の施工実績は"
         if found : 
            take left : 
               remove whitespaces
               replace("下記の" ,"")
               store(var3)
               set(var3)  


「同種工事(技術者)」:
   search in : all
   search text : ("次の1)~5)に掲げる基準を満たす主任技術者又は監理技術者を当該工事に専任で配置できること" , "次の1)~4)に掲げる基準を満たす主任技術者又は監理技術者を当該工事に専任で配置" , "次の((1))~((4))に掲げる基準を満たす主任技術者又は監理技術者を当該工事に専任で配置")
   if found : 
      take right : 
         search in : taken
         search text :  ("完成･引き渡しが完了した、上記(5)の同種工事" , "完成･引渡しが完了した、上記(5)に掲げる同種工事" , "完成･引き渡しが完了した、上記(5)に掲げる同種工事")
         if found : 
            set(「同種工事(企業)」)
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
               set(「同種工事(企業)」)


「より高い同種性(企業)doushusei_co_0」:  
   check : name_of
   has value : 本官
   if true : 
   if false : 
      search in : region_B
      search text : ("2) 企業の能力等(加算点)" , "2)企業の能力等(加算点)")
      if found : 
         take right :
            search in : taken
            search text : ("((1))同種工事" , "((1)) 同種工事の")
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
                              remove whitespaces
                              replace("|", "")
                              store(var10)
                              set(var10)

「同種性(企業)doushusei_co_2」:  
   check : name_of
   has value : 本官
   if true : 
   if false : 
      search in : region_B
      search text : ("2) 企業の能力等(加算点)" , "2)企業の能力等(加算点)")
      if found : 
         take right :
            search in : taken
            search text : ("((1))同種工事" , "((1)) 同種工事の")
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
                                       set(「同種工事(企業)」)
                                    if not found : 
                                       remove whitespaces
                                       replace("|", "")
                                       store(var11)
                                       set(var11)



「より高い同種性(技術者) doushusei_en_0」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")
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
                  search text : ("((1))同種工事" , "((1)) 同種工事の")
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
                                    remove whitespaces
                                    replace("|", "")
                                    store(x)
                                    set(x)


                        

「高い同種性(技術者) doushusei_en_1」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")
   if false : 
      search in : region_B
      search text : "技術者の能力等(加算点)"
      if found : 
         take right :
            search in : taken
            search text : ("((1))同種工事" , "((1)) 同種工事の")
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
                                       



「同種性(技術者) doushusei_en_2」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")
   if false : 
      search in : region_B
      search text : "技術者の能力等(加算点)"
      if found : 
         take right :
            search in : taken
            search text : ("((1))同種工事" , "((1)) 同種工事の")
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
                                             set(「同種工事(技術者)」)
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

「配点(企業)」: 
   check : name_of
   has value : 本官
   if true : 
   if false : 
      search in : all
      search text : ("より高い同種性が認められる工事:" , "高い同種性が認められる工事:")
      if found : 
         search in : all
         search text : "企業の能力等(加算点)で提出した企業において"
         if found : 
            take right:
               search in : taken
               search text : "企業の能力等(加算点)"
               if found : 
                  take right : 
                     search in : taken
                     search text : "で評価し、それぞれ"
                     if found : 
                        take right :  
                           search in : taken
                           search text : "の加算点を"
                           if found : 
                              take left : 
                                 remove whitespaces 
                                 store(score_co)
                                 set(score_co)
      if not found : 
         search in : all
         search text : "企業の能力等("
         if found : 
            take right : 
               search in : taken
               search text : "、それぞれ"
               if found : 
                  take right : 
                     search in : taken
                     search text : "の加算点を与える。"
                     if found : 
                        take left : 
                           remove whitespaces
                           store(score_co)
                           set(score_co)


「配点(技術者)」: 
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "技術者の能力等("
      if found :  
         take right : 
            search in : taken
            search text : "で評価し、"
            if found :  
               take right : 
                  search in : taken
                  search text : "の加算点を与える。"
                  if found : 
                     take left : 
                        replace("それぞれ","")
                        remove whitespaces
                        store(score_en)
                        set(score_en)

   if false : 
      search in : all
      search text : ("より高い同種性が認められる工事:" , "高い同種性が認められる工事:")
      if found : 
         search in : all
         search text : "企業の能力等(加算点)で提出した企業において"
         if found : 
            take right:
               search in : taken
               search text : "企業の能力等(加算点)"
               if found : 
                  take right : 
                     search in : taken
                     search text : "より高い同種性が認められる工事:"
                     if found : 
                        take right :
                           search in : taken
                           search text : "同種性が認められる工事:"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "技術者の能力等(加算点)"
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : "で評価し、それぞれ"
                                       if found : 
                                          take right : 
                                             search in : taken
                                             search text : "の加算点を"
                                             if found : 
                                                take left : 
                                                   remove whitespaces
                                                   store(score_en)
                                                   set(score_en)
                           if not found : 
                              search in : taken
                              search text : "技術者の能力等(加算点)"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "で評価し、それぞれ"
                                    if found : 
                                       take right : 
                                          search in : taken
                                          search text : "の加算点を"
                                          if found : 
                                             take left : 
                                                remove whitespaces
                                                store(score_en)
                                                set(score_en)
                     if not found :    
                        search in : taken
                        search text : "同種性が認められる工事:"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "技術者の能力等(加算点)"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "で評価し、それぞれ"
                                    if found : 
                                       take right : 
                                          search in : taken
                                          search text : "の加算点を"
                                          if found : 
                                             take left : 
                                                remove whitespaces
                                                store(score_en)
                                                set(score_en)
                        if not found : 
                           search in : taken
                           search text : "技術者の能力等(加算点)"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "で評価し、それぞれ"
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : "の加算点を"
                                       if found : 
                                          take left : 
                                             remove whitespaces
                                             store(score_en)
                                             set(score_en)
      if not found : 
         search in : all
         search text : "企業の能力等("
         if found : 
            take right : 
               search in : taken
               search text : "技術者の能力等("
               if found : 
                  take right : 
                     search in : taken
                     search text : "で評価し、"
                     if found : 
                        take right :  
                           search in : taken
                           search text : "の加算点を与える。"
                           if found : 
                              take left : 
                                 replace("それぞれ","")
                                 remove whitespaces
                                 store(score_en)
                                 set(score_en)
                        