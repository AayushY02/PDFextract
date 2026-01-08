has_eval_phrase :
   search in : all
   search text : "評価方法及び資料(総合評価に関する資料)の確認等"
   if found :
      set(true)
   if not found :
      set(false)

name_bu : 
   search in : all
   search text : "関東地方整備局"
   if found : 
      set("関東地方整備局")

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
                  search text : "関東地方整備局"
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
      take right :
         search in : taken
         search text : "(2)工事場所"
         if found : 
            take left : 
               search in : taken
               search text : ("(電子入札対象案件)", "(以下「((1))工事」という)")
               if found : 
                  take left :
                     remove whitespaces
                     replace("((1))", "")
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
         search text : ("5. 入札手続における担当部局" , "5.入札手続における担当部局")
         if found : 
            take left : 
               store(region_A)
         
reg_B : 
   search in : all
   search text : ("7.総合評価の項目", "7. 総合評価の項目")
   if found : 
      take right : 
         store(region_B)

「同種工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      
   if false:
      search in : region_A
      search text : "完成･引渡しが完了した下記(ア)の要件を満たす同種工事の施工実績を有すること。"
      if found : 
         take right : 
            search in : taken
            search text : "(ただし、異工種建設工事共同企業体については適用しない。))"
            if found : 
               take right :
                  search in : taken
                  search text : "ただし、申請できる同種工事の施工実績"
                  if found : 
                     take left : 
                        remove whitespaces
                        store(doushi_kouji_1)
                        set(doushi_kouji_1)
      if not found : 
         search in : taken
         search text : "完成･引渡しが完了した下記(ア)又は(イ)"
         if found :
            search in : taken
            search text : "完成･引渡しが完了した"
            if found : 
               take right : 
                  search in : taken
                  search text : "ただし、申請できる同種工事の施工実績"
                  if found : 
                     take left : 
                        replace("(共同企業体の構成員としての実績は、出資比率が20%以上の場合のものに限る。(ただし、異工種建設工事共同企業体については適用しない。))" , "")
                        remove whitespaces
                        store(doushi_kouji_1)
                        set(doushi_kouji_1)



「同種工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
     
   if false:
      search in : region_A
      search text : ("引渡しが完了した上記(5)(ア)に掲げる工事の経験を有する" , "引渡しが完了した上記(5)(ア)")
      if found : 
         set(「同種工事（企業）」)


「より同種性の高い（企業）」: 
   search in : region_B
   search text : "((1))企業の技術力"
   if found : 
      take right : 
         search in : taken
         search text : "〔企業の施工能力〕"
         if found : 
            take right : 
               search in : taken
               search text : "| より高い同種性が認められる。"
               if found : 
                  take right :
                     search in : taken
                     search text : " | "
                     if found : 
                        take left : 
                           remove whitespaces
                           store(co_very_high_similarity)
                           set(co_very_high_similarity)

「同種性が高い（企業）」: 
   search in : region_B
   search text : "((1))企業の技術力"
   if found : 
      take right : 
         search in : taken
         search text : "〔企業の施工能力〕"
         if found : 
            take right : 
               search in : taken
               search text : "| 高い同種性が認められる。"
               if found : 
                  take right :
                     search in : taken
                     search text : " | "
                     if found : 
                        take left : 
                           remove whitespaces
                           store(co_high_similarity)
                           set(co_high_similarity)

「同種性が認められる（企業）」: 
   search in : region_B
   search text : "((1))企業の技術力"
   if found : 
      take right : 
         search in : taken
         search text : "〔企業の施工能力〕"
         if found : 
            take right : 
               search in : taken
               search text : "| 同種性が認められる。"
               if found : 
                  take right :
                     search in : taken
                     search text : " | "
                     if found : 
                        take left : 
                           search in : taken
                           search text : "上記以外の同種工事の実績"
                           if found : 
                              set(「同種工事（企業）」)
                           if not found :
                              remove whitespaces
                              store(co_similarity)
                              set(co_similarity)

   

「より同種性の高い（技術者）」: 
   search in : region_B
   search text : "((2))配置予定技術者の技術力"
   if found :  
      search in : region_B
      search text : "〔配置予定技術者の能力〕"
      if found : 
         take right : 
            search in : taken
            search text : "| より高い同種性が認められる。"
            if found : 
               take right :
                  search in : taken
                  search text : " | "
                  if found : 
                     take left : 
                        remove whitespaces
                        store(eng_very_high_similarity)
                        set(eng_very_high_similarity)

「同種性の高い（技術者）」:
   search in : region_B
   search text : "((2))配置予定技術者の技術力"
   if found : 
      search in : region_B
      search text : "〔配置予定技術者の能力〕"
      if found : 
         take right : 
            search in : taken
            search text : "| 高い同種性が認められる。"
            if found : 
               take right :
                  search in : taken
                  search text : " | "
                  if found : 
                     take left : 
                        remove whitespaces
                        store(eng_high_similarity)
                        set(eng_high_similarity)

「同種性が認められる（技術者）」:
   search in : region_B
   search text : "((2))配置予定技術者の技術力"
   if found :  
      search in : taken
      search text : "〔配置予定技術者の能力〕"
      if found : 
         take right : 
            search in : taken
            search text : "| 同種性が認められる。"
            if found : 
               take right :
                  search in : taken
                  search text : " | "
                  if found : 
                     take left : 
                        search in : taken
                        search text : "上記以外の同種工事の経験"
                        if found : 
                           set(「同種工事（技術者）」)
                        if not found : 
                           remove whitespaces
                           store(eng_similarity)
                           set(eng_similarity)


 