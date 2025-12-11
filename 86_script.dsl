has_eval_phrase :
   search in : all
   search text : "総合評価に関する事項"
   if found :
      set(true)
   if not found :
      set(false)

name_bu : 
   search in : all
   search text : "近畿地方整備局"
   if found : 
      set("近畿地方整備局")

name_of :
   search in first : 20
   search text : "支出負担行為担当官近畿地方整備局長"
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
                  search text : "近畿地方整備局"
                  if found:
                     take right:
                        search in : taken
                        search text : ("所長", "所⻑")
                        if found : 
                           take left:
                              remove whitespaces
                              add in right(所)
                              store(var_nameof)
                              set(var_nameof)

「工事名・作業名」:
   search in : all
   search text : "工事名"
   if found : 
      take right :
         search in : taken
         search text : "3.2"
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
   

「同種性が高い（企業）」:
   search in : all
   search text : "5.1.1.1 同種性の高い施工実績"
   if found : 
      take right : 
         search in : taken
         search text : (" | | | | " , " | ")
         if found : 
            take right : 
               search in : taken
               search text : " | "
               if found : 
                  take left : 
                     remove whitespaces
                     store(co_high_similarity)
                     set(co_high_similarity)

      

「同種性の高い（技術者）」:
   search in : all
   search text : ("5.1.2.2 同種性の高い施工経験 評価項目" , "5.1.2.2 同種性の高い施工経験")
   if found : 
      take right : 
         search in : taken
         search text : (" | | | | " , " | ")
         if found : 
            take right : 
               search in : taken
               search text : " | "
               if found : 
                  take left : 
                     remove whitespaces
                     store(eng_high_similarity)
                     set(eng_high_similarity)