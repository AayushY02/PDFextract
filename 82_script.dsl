has_eval_phrase :
   search in : all
   search text : "総合評価に関する事項"
   if found :
      set(true)
   if not found :
      set(false)

name_bu : 
   search in : all
   search text : "東北地方整備局"
   if found : 
      set("東北地方整備局")

name_of :
   search in : all
   search text : "支出負担行為担当官東北地方整備局長"
   if found :
      set("本官")
   if not found : 
      search in : all
      search text : "2.契約担当官等"
      if found : 
         take right : 
            search in : taken
            search text : "分任支出負担行為担当官"
            if found :
               take right :
                  search in : taken
                  search text : "東北地方整備局"
                  if found:
                     take right:
                        search in : taken
                        search text : ("所長" , "所⻑")
                        if found : 
                           take left:
                              remove whitespaces
                              add in right(所)
                              store(var_nameof)
                              set(var_nameof)
      if not found : 
         search in : all
         search text : "契約担当官等"
         if found : 
            take right : 
               search in : taken
               search text : "分任支出負担行為担当官"
               if found : 
                  take right : 
                     search in : taken
                     search text : "東北地方整備局"
                     if found : 
                        take right : 
                           search in : taken
                           search text : "所長"
                           if found : 
                              take left : 
                                 remove whitespaces
                                 add in right(所)
                                 store(var_nameof)
                                 set(var_nameof)

「工事名」:
   search in : all
   search text : "工事名"
   if found : 
      take right :
         search in : taken
         search text : "(2) 工事場所"
         if found : 
            take left : 
               search in : taken
               search text : "(電子入札対象案件)"
               if found : 
                  take left :
                     search in : taken
                     search text : "(電子入札対象案件及び電子契約対象案件)"
                     if found : 
                        take left : 
                           remove whitespaces
                           store(var_kouji)
                           set(var_kouji)
                     if not found : 
                        remove whitespaces
                        store(var_kouji)
                        set(var_kouji)
               if not found : 
                  search in : taken
                  search text : "(電子入札対象案件及び電子契約対象案件)"
                  if found : 
                     take left : 
                        remove whitespaces
                        store(var_kouji)
                        set(var_kouji)
                  if not found : 
                     remove whitespaces
                     store(var_kouji)
                     set(var_kouji)

reg_A : 
   search in : all
   search text : "4.競争参加資格"
   if found : 
      take right : 
         search in : taken
         search text : "5.総合評価に関する事項"
         if found : 
            take left : 
               store(region_A)
         
reg_B : 
   search in : all
   search text : "5.総合評価に関する事項"
   if found : 
      take right : 
         store(region_B)

「同種工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      search in : region_A
      search text : ("引渡しが完了した、下記①の要件を満たす工事の施工実績を有すること" , "引渡しが完了した、下記の(ア)又は(イ)又は(ウ)のいずれかの要件及び(エ)の要件を満たす工事の施工実績を有すること")
      if found :
         take right:
            search in : taken
            search text : "①の実績を有すること。"
            if found : 
               take right :
                  search in : taken
                  search text : "適切なものとは、"
                  if found : 
                     take left:
                        remove whitespaces
                        store(var1)
                        set(var1)
            if not found : 
               search in : taken
               search text : "の実績であること。)。"
               if found : 
                  take right :
                     search in : taken
                     search text : "適切なものとは、"
                     if found : 
                        take left:
                           remove whitespaces
                           store(var1)
                           set(var1)
   if false:
      search in : region_A
      search text : "施工を行った分担工事の実績であること。)。"
      if found : 
         take right : 
            search in : taken
            search text : "② 当該施工実績"
            if found : 
               take left :
                  search in : taken
                  search text : "②"
                  if found : 
                     remove whitespaces
                     replace(" " , "")
                     replace(end, "の施工実績" , "")
                     store(doushi_kouji_1)
                     set(doushi_kouji_1)
                  if not found : 
                     remove whitespaces
                     replace("①" , "")
                     replace(" " , "")
                     replace(end, "の施工実績" , "")
                     store(doushi_kouji_1)
                     set(doushi_kouji_1)

「同種工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      search in : region_A
      search text : ("元請けとして完成･引渡しが完了した、下記(ア)の要件を満たす")
      if found :
         take right:
            search in : taken
            search text : "構成員が施工を行った分担工事のものであること。"
            if found : 
               take right :
                  search in : taken
                  search text : ("適切なものとは、" , "なお、施工経験として提出した")
                  if found : 
                     take left:
                        search in : taken
                        search text : "に代えることができる。"
                        if found : 
                           take right : 
                              remove whitespaces
                              store(var1)
                              set(var1)
                        if not found : 
                           remove whitespaces
                           store(var2)
                           set(var2)             
   if false:
      search in : region_A
      search text : ("(5) 次に掲げる基準を満たす主任技術者、監理技術者又は特例監理技術者を本工事に配置できること" , "(5) 次に掲げる基準を満たす主任技術者、監理技術者を本工事に配置できること。")
      if found : 
         take right : 
            search in : taken
            search text : ("完成･引渡しが完了した、下記(ア)及び(イ)の要件を満たす工事" , "完成･引渡しが完了した、下記(ア)及び(イ)の要件を満")
            if found : 
               take right : 
                  search in : taken
                  search text : "に代えることができる。"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "(イ) 当該施工経験"
                        if found : 
                           take left : 
                              remove whitespaces
                              replace("(ア)" , "")
                              replace(" " , "")
                              replace(end, "の施工経験" , "")
                              store(doushi_kouji_gijutsusha)
                              set(doushi_kouji_gijutsusha)

「より同種性が高い（企業）」: 
   check : name_of
   has value : 本官
   if true : 
      search in : region_B
      search text : "II.加算点"
      if found : 
         take right : 
            search in : taken
            search text : "下記1)①及び2)①の「より同種性が高い工事」"
            if found : 
               take right : 
                  search in : taken
                  search text : "より同種性が高い工事"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "企業の施工能力 |"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "|"
                              if found : 
                                 take left : 
                                    remove whitespaces
                                    store(var23)
                                    set(var23)
   if false :
      search in : region_B
      search text : "② 加算点"
      if found : 
         take right : 
            search in : taken
            search text : "| より同種性が高い工事"
            if found : 
               take right :
                  search in : taken
                  search text : "企業の施工能力 |"
                  if found : 
                     take right :
                        search in : taken
                        search text : " | "
                        if found : 
                           take left :  
                              remove whitespaces
                              replace(" | ", "")
                              replace(" " , "")
                              replace("工事の施工実績" , "")
                              replace("における造園" , "")
                              replace(end, "の施工実績" , "")
                              store(co_very_high_similarity)
                              set(co_very_high_similarity)

「同種性が認められる（企業）」: 
   check : name_of
   has value : 本官
   if true : 
      search in : region_B
      search text : "II.加算点"
      if found : 
         take right : 
            search in : taken
            search text : "下記1)①及び2)①の「より同種性が高い工事」及び「同種性が認められる工事」"
            if found : 
               take right : 
                  search in : taken
                  search text : "同種性が認められる工事"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "企業の施工能力 |"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "|"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "|"
                                    if found : 
                                       take left :
                                          remove whitespaces
                                          store(var23)
                                          set(var23)
   if false : 
      search in : region_B
      search text : "② 加算点"
      if found : 
         take right : 
            search in : taken
            search text : "| 同種性が認められる工事"
            if found : 
               take right :
                  search in : taken
                  search text : "企業の施工能力 |"
                  if found : 
                     take right :
                        search in : taken
                        search text : " | "
                        if found : 
                           take right :
                              search in : taken
                              search text : "配置予定技術者の能力 |"
                              if found : 
                                 take left : 
                                    remove whitespaces
                                    replace(" " , "")
                                    replace(end, "の施工実績" , "")
                                    store(co_similarity)
                                    set(co_similarity)

「より同種性が高い（技術者）」: 
   check : name_of
   has value : 本官
   if true : 
      search in : region_B
      search text : "II.加算点"
      if found : 
         take right : 
            search in : taken
            search text : "下記1)①及び2)①の「より同種性が高い工事」"
            if found : 
               take right : 
                  search in : taken
                  search text : "より同種性が高い工事"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "配置予定技術者の能力 |"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "|"
                              if found : 
                                 take left : 
                                    remove whitespaces
                                    store(var23)
                                    set(var23)
   if false :
      search in : region_B
      search text : "② 加算点"
      if found : 
         take right : 
            search in : taken
            search text : "| より同種性が高い工事"
            if found : 
               take right :
                  search in : taken
                  search text : "配置予定技術者の能力 |"
                  if found : 
                     take right :
                        search in : taken
                        search text : " |"
                        if found : 
                           take left :  
                              remove whitespaces
                              store(temp1)
                              check : temp1
                              has value : ""
                              if true : 
                                 set(「より同種性の高い（企業）」)
                              if false : 
                                 set(temp1)

「同種性が認められる（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      search in : region_B
      search text : "II.加算点"
      if found : 
         take right : 
            search in : taken
            search text : "下記1)①及び2)①の「より同種性が高い工事」"
            if found : 
               take right : 
                  search in : taken
                  search text : "より同種性が高い工事"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "配置予定技術者の能力 |"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "|"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "|"
                                    if found : 
                                       take left :
                                          remove whitespaces
                                          store(var23)
                                          set(var23)
   if false :
      search in : region_B
      ## this is a comment
      search text : "② 加算点"
      if found : 
         take right : 
            search in : taken
            search text : "| 同種性が認められる工事"
            if found : 
               take right :
                  search in : taken
                  search text : "配置予定技術者の能力 |"
                  if found : 
                     take right :
                        search in : taken
                        search text : " |"
                        if found : 
                           take right :
                              search in : taken
                              search text : "[[TABLE_END]]"  
                              if found : 
                                 take left : 
                                    remove whitespaces
                                    store(temp2)
                                    check : temp2
                                    has value : ""
                                    if true : 
                                       set(「同種性が認められる（企業）」)
                                    if false : 
                                       set(temp2)