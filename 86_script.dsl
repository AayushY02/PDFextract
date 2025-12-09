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
                  search text : "近畿地方整備局"
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
      

「同種工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      
     
   if false:
 