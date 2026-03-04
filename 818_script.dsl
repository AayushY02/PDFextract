has_eval_phrase :
   search in : all
   search text : "総合評価に関する事項"
   if found :
      set(true)
   if not found :
      set(false)

name_bu : 
   search in : all
   search text : "北海道開発局留萌開発建設部"
   if found : 
      set("北海道開発局")

name_of :
   search in first : 20
   search text : "支出負担行為担当官北海道開発局留萌開発建設部長"
   if found :
      set("本官")  
   if not found : 
      search in : all
      search text : "2 契約担当官等"
      if found : 
         take right : 
            search in : taken
            search text : "支出負担行為担当官"
            if found :
               take right :
                  search in : taken
                  search text : "北海道開発局"
                  if found:
                     take right:
                        search in : taken
                        search text : "長"
                        if found : 
                           take left:
                              remove whitespaces
                              store(var_nameof)
                              set(var_nameof)
      if not found : 
         search in : all
         search text : "契約担当官等"
         if found : 
            take right : 
               search in : taken
               search text : "支出負担行為担当官"
               if found : 
                  take right : 
                     search in : taken
                     search text : "北海道開発局"
                     if found : 
                        take right : 
                           search in : taken
                           search text : "長"
                           if found : 
                              take left : 
                                 remove whitespaces
                                 store(var_nameof)
                                 set(var_nameof)

「工事名」:
   search in : all
   search text : ("工事名" , "工 事 名")
   if found : 
      take right :
         search in : taken
         search text : ("(2) 工事場所" , "(2)工事場所" , "(2)")
         if found : 
            take left : 
               replace("（電子入札対象案件）" , "")
               replace("（電子契約対象案件）" , "")
               remove whitespaces
               store(var_kouji)
               set(var_kouji)

reg_A : 
   search in : all
   search text : "競争参加資格 4"
   if found : 
      take right : 
         search in : taken
         search text : "総合評価落札方式に関する事項"
         if found : 
            take left : 
               store(region_A)
         
reg_B : 
   search in : all
   search text : "総合評価落札方式に関する事項"
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
      search text : ("平成20年度以降から公告開始日時点において、次の" , "平成21年度以降から公告開始日時点において、次の")
      if found : 
         take right : 
               search in : taken
               search text : "を元請"
               if found : 
                  take left :
                     store(tempdd)
               search in : taken
               search text : "又は「より同種工事」の実績とする。"
               if found : 
                  take right : 
                     search in : taken
                     search text : ("施工計画(「当該工事での留意事項等" , "当該工事での留意事項等(以下「施工計画」という" , "次のア、イ及びウに掲げる基準を満")
                     if found : 
                           take left : 
                              add in left(tempdd)
                              remove whitespaces
                              replace("の施工実績を有すること。" , "")
                              replace("の施工実績。" , "")
                              store(doushi_kouji_1)
                              set(doushi_kouji_1)  

「同種性が認められる（企業）」temp:
   check : name_of
   has value : 本官
   if true : 
      set("本官")    
   if false:
      search in : region_A
      search text : "次のア又はイの要件を満たす工事を元請"
      if found : 
         take right : 
            search in : taken
            search text : "国内工事の実績と同様に「同種工事」又は「より同種工事」の実績とする。"
            if found : 
               take right :
                  search in : taken
                  search text : "ア【同種性が認められる工事】" 
                  if found : 
                     take right :
                        search in : taken
                        search text : "イ【より同種性の高い工事】"
                        if found : 
                           take left :
                              store(dd)
                           take right : 
                              search in : taken
                              search text : "注1)"
                              if found : 
                                 search in : taken
                                 search text : "施工計画(「当該工事での留意事項等"
                                 if found : 
                                    take left : 
                                       search in : taken
                                       search text : "施工実績を有すること。 "
                                       if found : 
                                          take right : 
                                             add in left(dd)
                                             remove whitespaces
                                             store(xx)
                                             set(xx)
                              if not found : 
                                 set(dd)
                        
「同種性が認められる（技術者）」temp:
   check : name_of
   has value : 本官
   if true : 
      set("本官")    
   if false:
      search in : region_A
      search text : "基準を満たす主任技術者又は監理技術者を当該工事に専任で"
      if found : 
         take right : 
            search in : taken
            search text : "上記(4)に掲げる工事の経験を有する"
            if found : 
               set(「同種性が認められる（企業）」temp)
            if not found : 
               search in : taken
               search text : "(ア)【同種性が認められる工事】" 
               if found : 
                  take right :
                     search in : taken
                     search text : "(イ)【より同種性の高い工事】"
                     if found : 
                        take left :
                           store(dd1)
                        take right : 
                           search in : taken
                           search text : "注1)"
                           if found : 
                              search in : taken
                              search text : "施工計画(「当該工事での留意事項等"
                              if found : 
                                 take left : 
                                    search in : taken
                                    search text : "施工実績を有すること。 "
                                    if found : 
                                       take right : 
                                          add in left(dd1)
                                          remove whitespaces
                                          store(xx)
                                          set(xx)
                           if not found : 
                              set(dd1)                                  
                                

「より同種性が高い（企業）」temp:
   check : name_of
   has value : 本官
   if true : 
      set("本官")    
   if false:
      search in : region_A
      search text : "次のア又はイの要件を満たす工事を元請"
      if found : 
         take right : 
            search in : taken
            search text : "国内工事の実績と同様に「同種工事」又は「より同種工事」の実績とする。"
            if found : 
               take right :
                  search in : taken
                  search text : "ア【同種性が認められる工事】" 
                  if found : 
                     take right :
                        search in : taken
                        search text : "イ【より同種性の高い工事】"
                        if found : 
                           take right :
                              search in : taken
                              search text : ( "当該工事での留意事項等" , "注1)冬期通行止め区間の" , "次のア、イ及びウに掲げる" )
                              if found : 
                                 take left : 
                                    remove whitespaces
                                    replace("の施工実績を有すること。" , "")
                                    replace("を有すること。" , "")
                                    store(doushi_kouji_1)
                                    set(doushi_kouji_1)
      


「同種工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")    
   if false:
      search in : region_A
      search text : "基準を満たす主任技術者又は監理技術者を当該工事に専任で"
      if found : 
         take right : 
            search in : taken
            search text : "上記(4)に掲げる工事の経験を有する"
            if found : 
               set(「同種工事（企業）」)
            if not found : 
               search in : taken
               search text : "平成20年度以降から公告開始日時点において、次の"
               if found : 
                  take right : 
                     search in : taken
                     search text : "の経験を有する者であること"
                     if found : 
                        take left :
                           store(tempdd)
                     search in : taken
                     search text : "点未満のものを除く。"
                     if found : 
                        take right : 
                           search in : taken
                           search text : "ウ 監理技術者にあっては"
                           if found : 
                                 take left : 
                                    add in left(tempdd)
                                    remove whitespaces
                                    replace("の施工実績を有すること。" , "")
                                    replace("の施工実績。" , "")
                                    store(doushi_kouji_1)
                                    set(doushi_kouji_1)  
                           
        



「より同種性が高い（技術者）」temp: 
   check : name_of
   has value : 本官
   if true : 
      set("本官")    
   if false:
      search in : region_A
      search text : "基準を満たす主任技術者又は監理技術者を当該工事に専任で"
      if found : 
         take right : 
            search in : taken
            search text : "上記(4)に掲げる工事の経験を有する"
            if found : 
               set(「より同種性が高い（企業）」temp)
            if not found : 
               search in : taken
               search text : "次の(ア)又は(イ)に掲げる工事の経験を有する者であること"
               if found : 
                  take right :
                     search in : taken
                     search text : "(ア)【同種性が認められる工事】"
                     if found : 
                        take right :
                           search in : taken
                           search text : "(イ)【より同種性の高い工事】"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "ウ 監理技術者に"
                                 if found : 
                                    take left :
                                       remove whitespaces
                                       replace("の施工実績を有すること。" , "")
                                       replace("を有すること。" , "")
                                       store(doushi_kouji_1)
                                       set(doushi_kouji_1)
    

「同種性が認められる（企業）」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")
   if false : 
      search in : region_B
      search text : "配 置 予 定 技 術 者"
      if found : 
         take right : 
            search in : taken
            search text : "同種性が認められる工事"
            if found : 
               take right : 
                  search in : taken
                  search text : "同種性が認められる工事の実績あり"
                  if found : 
                     set(「同種性が認められる（企業）」temp)

「同種性が認められる（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")
   if false : 
      search in : region_B
      search text : "配 置 予 定 技 術 者"
      if found : 
         take right : 
            search in : taken
            search text : "CPDへの取組"
            if found : 
               take left : 
                  search in : taken
                  search text : "同種性が認められる工事の実績あり"
                  if found : 
                     set(「同種性が認められる（技術者）」temp)
                  if not found : 
                     search in : taken
                     search text : "同種性が認められる工事において、"
                     if found : 
                           take right : 
                              search in : taken
                              search text : " | "
                              if found : 
                                 take left : 
                                       add in left("：")
                                       add in left(「同種性が認められる（技術者）」temp)
                                       replace("施工実績" , "")
                                       replace("のを有すること。" , "")
                                       store(newenwewe)
                                       set(newenwewe)

「より同種性が高い（企業）」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")
   if false : 
      search in : region_B
      search text : "配 置 予 定 技 術 者"
      if found : 
         take right : 
            search in : taken
            search text : "より同種性の高い工事"
            if found :
               take right : 
                  search in : taken
                  search text : "より同種性の高い工事実績あり"
                  if found : 
                     set(「より同種性が高い（企業）」temp)

「より同種性が高い（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")
   if false : 
      search in : region_B
      search text : "配 置 予 定 技 術 者"
      if found : 
         take right : 
            search in : taken
            search text : "CPDへの取組"
            if found : 
               take left : 
                  search in : taken
                  search text : "より同種性の高い工事実績あり"
                  if found : 
                     set(「より同種性が高い（技術者）」temp)
                  if not found : 
                     search in : taken
                     search text : "より同種性の高い工事において、"
                     if found : 
                           take right : 
                              search in : taken
                              search text : " | "
                              if found : 
                                 take left : 
                                       replace("施工実績" , "")
                                       add in left("：")
                                       add in left(「より同種性が高い（技術者）」temp)
                                       store(newenwewe)
                                       set(newenwewe)


「同種性が高い（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      set("本官")
   if false : 
      search in : region_B
      search text : "配 置 予 定 技 術 者"
      if found : 
         take right :
            search in : taken
            search text : "CPDへの取組"
            if found : 
                  take left :  
                     search in : taken
                     search text : "より同種性の高い工事において、"
                     if found : 
                        take right : 
                              search in : taken
                              search text : " | "
                              if found : 
                                 take right :
                                    search in : taken
                                    search text : "より同種性の高い工事において、"
                                    if found : 
                                          take right : 
                                             search in : taken
                                             search text : " | "
                                             if found : 
                                                take left : 
                                                      search in : taken
                                                      search text : "同種性が認められる工事に おいて、"
                                                      if found : 
                                                         search in first : 0
                                                         search text : ""
                                                         if found :
                                                            take left :
                                                                  add in right(「より同種性が高い（技術者）」)
                                                                  add in right(" ")
                                                                  add in right(「同種性が認められる（技術者）」)
                                                                  replace("施工実績" , "")
                                                                  store(Xx)
                                                                  set(Xx)