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
   search text : "支出負担行為担当官北陸地方整備局長"
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

「工事名」:
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

reg_A : 
   search in : all
   search text : ("4.競争参加資格" , "4. 競争参加資格")
   if found : 
      take right : 
         search in : taken
         search text : ("5.総合評価に関する事項", "5. 総合評価に関する事項")
         if found : 
            take left : 
               store(region_A)
         
reg_B : 
   search in : all
   search text : ("5.総合評価に関する事項", "5. 総合評価に関する事項")
   if found : 
      take right : 
         store(region_B)

「同種工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      
   if false:
      search in : region_A
      search text : ("下記1)の要件を満たす工事の施工実績", "下記1)の要件を満たす作業(工事)")
      if found : 
         take right : 
            search in : taken
            search text : "評定点が65点未満のものを除く。\n1) "
            if found : 
               take right :
                  search in : taken
                  search text : "(7) 建設共同企業体の実績をもって単体"
                  if found : 
                     take left : 
                        search in : taken
                        search text : "※一般財団法人日"
                        if found : 
                           take left : 
                              remove whitespaces
                              replace("であること。" , "")
                              replace("の施工実績を有すること。" , "")
                              replace("。" , "")
                              store(doushi_kouji_1)
                              set(doushi_kouji_1)
                        if not found : 
                           take left : 
                              remove whitespaces
                              replace("であること。" , "")
                              replace("の施工実績" , "")
                              replace("。" , "")
                              store(doushi_kouji_1)
                              set(doushi_kouji_1)
            if not found : 
               search in : taken
               search text : "満のものを除く。\n1) "
               if found : 
                  take right :
                     search in : taken
                     search text : "(7) 建設共同企業体の実績をもって単体"
                     if found : 
                        take left : 
                           search in : taken
                           search text : "※一般財団法人日"
                           if found : 
                              take left : 
                                 remove whitespaces
                                 replace("であること。" , "")
                                 replace("の施工実績" , "")
                                 replace("。" , "")
                                 store(doushi_kouji_1)
                                 set(doushi_kouji_1)
                           if not found : 
                              take left : 
                                 remove whitespaces
                                 replace("であること。" , "")
                                 replace("の施工実績" , "")
                                 replace("。" , "")
                                 store(doushi_kouji_1)
                                 set(doushi_kouji_1)

                     
「同種工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
     
   if false:
      search in : region_A
      search text : ("次に掲げる基準を満たす主任技術者、又は監理技術者を本工事に配置できること。" , "次に掲げる基準を満たす主任技術者又は監理技術者を本工事に配置できること。", "次に掲げる基準を満たす主任技術者、又は監理技術者を本作業に配置できること。" , "次に掲げる基準を満たす現場代理人を本作業に配置できること。")
      if found : 
         take right : 
            search in : taken
            search text : "下記(ア)の要件を満たす工事の施工経験"
            if found : 
               take right : 
                  search in : taken
                  search text : "評定点が65点未満のものを除く。"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "((3)) 監理技術者にあっては"
                        if found : 
                           take left : 
                              remove whitespaces
                              store(doushi_kouji_2)
                              set(doushi_kouji_2)
            if not found : 
               search in : taken
               search text : ("上記(6)に掲げる要件を満たす工事の施工経験", "上記(6)に掲げる要件を満たす工事", "上記(6)に掲げる要件を満たす作業(工事)")
               if found : 
                  set(「同種工事（企業）」)

「より同種性の高い（企業）」: 
   search in : region_B
   search text : ("企業の施工能 力 | ", "企業の施工能力 | ")
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
                     search in : taken
                     search text : ("の場合", "の場 合", "場合", "場 合", ":")
                     if found : 
                        take left : 
                           remove whitespaces
                           replace(" " , "")
                           replace("敷設の施工実績を有する" , "")
                           replace("実績を有する" , "")
                           store(co_very_high_similarity)
                           set(co_very_high_similarity)

「同種性が高い（企業）」: 
   search in : region_B
   search text : ("企業の施工能 力 | ", "企業の施工能力 | ")
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
                     search in : taken
                     search text : ("の場合", "の場 合", "場合", "場 合", ":")
                     if found : 
                        take left : 
                           remove whitespaces
                           store(co_high_similarity)
                           set(co_high_similarity)

「同種性が認められる（企業）」: 
   search in : region_B
   search text : ("企業の施工能 力 | ", "企業の施工能力 | ")
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
                     search in : taken
                     search text : ("の場合", "の場 合", "場合", "場 合", ":")
                     if found : 
                        take left : 
                           remove whitespaces
                           store(co_similarity)
                           set(co_similarity)                  

「より同種性の高い（技術者）」: 
   search in : region_B
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
                                       search in : taken
                                       search text : ("の場合", "の場 合", "場合", "場 合", ":")
                                       if found : 
                                          take left : 
                                             remove whitespaces
                                             store(eng_very_high_similarity)
                                             set(eng_very_high_similarity)

「同種性の高い（技術者）」:
   search in : region_B
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
                                       search in : taken
                                       search text : ("の場合", "の場 合", "場合", "場 合", ":")
                                       if found : 
                                          take left : 
                                             remove whitespaces
                                             store(eng_high_similarity)
                                             set(eng_high_similarity)

「同種性が認められる（技術者）」:
   search in : region_B
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
                                       search in : taken
                                       search text : ("の場合", "の場 合", "場合", "場 合", ":")
                                       if found : 
                                          take left : 
                                             remove whitespaces
                                             store(eng_similarity)
                                             set(eng_similarity)
