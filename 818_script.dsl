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

「同種性が認められる（企業）」:
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
                              remove whitespaces
                              replace("の施工実績を有すること。" , "")
                              store(doushi_kouji_1)
                              set(doushi_kouji_1)
                                

「より同種性が高い（企業）」:
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
      


「同種性が認められる（技術者）」:
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
               set(「同種性が認められる工事（企業）」)
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
                              take left : 
                                 remove whitespaces
                                 replace("の施工実績を有すること。" , "")
                                 replace("を有すること。" , "")
                                 store(doushi_kouji_1)
                                 set(doushi_kouji_1)
                  
        



「より同種性が高い（技術者）」: 
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
               set(「より同種性の高い工事（企業）」)
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
    

