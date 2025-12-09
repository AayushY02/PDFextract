has_eval_phrase :
   search in : all
   search text : "総合評価に関する事項"
   if found :
      set(true)
   if not found :
      set(false)

name_bu : 
   search in : all
   search text : "北陸地方整備局"
   if found : 
      set("北陸地方整備局")

name_of :
   search in first : 20
   search text : "支出負担行為担当官関東地方整備局長"
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
                  search text : "北陸地方整備局"
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

「工事名・作業名」:
   search in : all
   search text : "工 事 名"
   if found : 
      take right :
         search in : taken
         search text : "(2)"
         if found : 
            take left : 
               search in : taken
               search text : "(電子入札対象案件)"
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
      search in : all
      search text : "作 業 名"
      if found : 
         take right :
            search in : taken
            search text : "(2)"
            if found : 
               take left : 
                  search in : taken
                  search text : "(電子入札対象案件)"
                  if found : 
                     take left :
                        remove whitespaces
                        store(var_kouji)
                        set(var_kouji)
                  if not found : 
                     remove whitespaces
                     store(var_kouji)
                     set(var_kouji)

「同種工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      
   if false:
      search in : all
      search text : ("同種工事の施 工実績 | ", "同種作業(工 事)の施工実績 | ", "同種作業(工事)の施工実績 | " , "同 種 作 業 ( 工 事)の施工実績 | " , "同種工事の施 工実績 | " , "同種工事の施 工実績 工事成績 | " )
      if found : 
         take right : 
            search in : taken
            search text : " | "
            if found : 
               take right :
                  search in : taken
                  search text : "| "
                  if found : 
                     take left : 
                        remove whitespaces
                        store(doushi_kouji_1)
                        set(doushi_kouji_1)

「より同種性の高い（企業）」: 
   search in : all
   search text : ("同種工事の施 工実績 | ", "同種作業(工 事)の施工実績 | ", "同種作業(工事)の施工実績 | " , "同 種 作 業 ( 工 事)の施工実績 | " , "同種工事の施 工実績 | " , "同種工事の施 工実績 工事成績 | " )
   if found : 
      take right : 
         search in : taken
         search text : "より同種性が高い施工実績(S)"
         if found : 
            take right :
               search in : taken
               search text : "同種性が高い施工実績(A)"
               if found : 
                  take left : 
                     remove whitespaces
                     store(co_very_high_similarity)
                     set(co_very_high_similarity)

「同種性が高い（企業）」: 
   search in : all
   search text : ("同種工事の施 工実績 | ", "同種作業(工 事)の施工実績 | ", "同種作業(工事)の施工実績 | " , "同 種 作 業 ( 工 事)の施工実績 | " , "同種工事の施 工実績 | " , ""同種工事の施 工実績 工事成績 |"" )
   if found : 
      take right : 
         search in : taken
         search text : "同種性が高い施工実績(A)"
         if found : 
            take right :
               search in : taken
               search text : "同種性が認められる施工実績(B)"
               if found : 
                  take left : 
                     remove whitespaces
                     store(co_high_similarity)
                     set(co_high_similarity)

「同種性が認められる（企業）」: 
   search in : all
   search text : ("同種工事の施 工実績 | ", "同種作業(工 事)の施工実績 | ", "同種作業(工事)の施工実績 | " , "同 種 作 業 ( 工 事)の施工実績 | " , "同種工事の施 工実績 | " , "同種工事の施 工実績 工事成績 | " )
   if found : 
      take right : 
         search in : taken
         search text : "同種性が認められる施工実績(B)"
         if found : 
            take right :
               search in : taken
               search text : "| "
               if found : 
                  take left : 
                     remove whitespaces
                     store(co_similarity)
                     set(co_similarity)
                        
「同種工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
   if false:
      search in : all
      search text : ("配置予定技術 者の施工能力" , "配置予定技術 者の施工能力" , "配置予定現場 代理人の施工 能力")
      if found : 
         take right : 
            search in : taken
            search text : (" | 同種工事の施" , " | 同種作業(工 事)の施工")
            if found : 
               take right : 
                  search in : taken
                  search text : " | "
                  if found : 
                     take right : 
                        search in : taken
                        search text : " | "
                        if found : 
                           take right :
                              search in : taken
                              search text : "| "
                              if found : 
                                 take left : 
                                    remove whitespaces
                                    store(doushi_kouji_2)
                                    set(doushi_kouji_2)

「より同種性の高い（技術者）」: 
   search in : all
   search text : ("配置予定技術 者の施工能力" , "配置予定技術 者の施工能力" , "配置予定現場 代理人の施工 能力")
   if found : 
      take right : 
         search in : taken
         search text : (" | 同種工事の施" , " | 同種作業(工 事)の施工")
         if found : 
            take right : 
               search in : taken
               search text : " | "
               if found : 
                  take right : 
                     search in : taken
                     search text : " | "
                     if found : 
                        take right :
                           search in : taken
                           search text : "より同種性が高い施工経験(S)"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "同種性が高い施工経験(A)"
                                 if found : 
                                    take left : 
                                       remove whitespaces
                                       store(eng_very_high_similarity)
                                       set(eng_very_high_similarity)

「同種性の高い（技術者）」:
   search in : all
   search text : ("配置予定技術 者の施工能力" , "配置予定技術 者の施工能力" , "配置予定現場 代理人の施工 能力")
   if found : 
      take right : 
         search in : taken
         search text : (" | 同種工事の施" , " | 同種作業(工 事)の施工")
         if found : 
            take right : 
               search in : taken
               search text : " | "
               if found : 
                  take right : 
                     search in : taken
                     search text : " | "
                     if found : 
                        take right :
                           search in : taken
                           search text : "同種性が高い施工経験(A)"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "同種性が認められる施工経験(B)"
                                 if found : 
                                    take left : 
                                       remove whitespaces
                                       store(eng_high_similarity)
                                       set(eng_high_similarity)

「同種性が認められる（技術者）」:
   search in : all
   search text : ("配置予定技術 者の施工能力" , "配置予定技術 者の施工能力" , "配置予定現場 代理人の施工 能力")
   if found : 
      take right : 
         search in : taken
         search text : (" | 同種工事の施" , " | 同種作業(工 事)の施工")
         if found : 
            take right : 
               search in : taken
               search text : " | "
               if found : 
                  take right : 
                     search in : taken
                     search text : " | "
                     if found : 
                        take right :
                           search in : taken
                           search text : "同種性が認められる施工経験(B)"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "| "
                                 if found : 
                                    take left : 
                                       remove whitespaces
                                       store(eng_similarity)
                                       set(eng_similarity)
