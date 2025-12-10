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

「より同種性の高い（企業）」: 
   search in : all
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
   search in : all
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
   search in : all
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
                     remove whitespaces
                     store(co_similarity)
                     set(co_similarity)

   

「より同種性の高い（技術者）」: 
   search in : all
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
   search in : all
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
   search in : all
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
                     remove whitespaces
                     store(eng_similarity)
                     set(eng_similarity)


 