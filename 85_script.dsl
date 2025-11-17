has_eval_phrase :
   search in : all
   search text : "入札の評価に関する基準及び得点配分"
   if found :
      set(true)
   if not found :
      set(false)

name_of :
   search in first : 20
   search text : "支出負担行為担当官 中部地方整備局長"
   if found :
      set("本官")
   if not found : 
      search in : all
      search text : "分任支出負担行為担当官"
      if found :
         take right :
            search in : taken
            search text : "中部地方整備局"
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

工事名:
   search in : all
   search text : "工事名"
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


「同種工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : ["【企業】", "【技術者】"]
      if found : 
         search in : all
         search text : "発注者から企業に対して通知された評定点が"
         if found : 
            take right : 
               search in : taken
               search text : "【企業】"
               if found : 
                  take right : 
                     search in : taken
                     search text : "同種工事："
                     if found : 
                        take right : 
                           search in : taken
                           search text : "【技術者】"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "同種工事："
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : "(5)"
                                       if found : 
                                          take left : 
                                             search in : taken
                                             search text : "(6)"
                                             if found : 
                                                take left : 
                                                   remove whitespaces
                                                   store(var_ts_gijutsu_true)
                                                   set(var_ts_gijutsu_true)
      if not found : 
         set("特殊工事のため要確認")
   if false:
      search in: all
      search text: "同種工事:"
      if found : 
         take right : 
            search in : taken
            search text : "また"
            if found : 
               take left :
                  store(new) 
                  set(new)

同種工事（企業）:
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : ["【企業】", "【技術者】"]
      if found : 
         search in : all
         search text : "発注者から企業に対して通知された評定点が"
         if found : 
            take right : 
               search in : taken
               search text : "【企業】"
               if found : 
                  take right : 
                     search in : taken
                     search text : "同種工事："
                     if found : 
                        take right : 
                           search in : taken
                           search text : "【技術者】"
                           if found : 
                              take left : 
                                 remove whitespaces
                                 store(var_ts_kigyo_true)
                                 set(var_ts_kigyo_true)
      if not found : 
         search in : all
         search text : "発注者から企業に対して通知された評定点が"
         if found : 
            take right : 
               search in : taken
               search text : "同種工事："
               if found : 
                  take right : 
                     search in : taken
                     search text : "(6)"
                     if found : 
                        take left : 
                           remove whitespaces
                           store(var_ts_kigyo_true2)
                           set(var_ts_kigyo_true2)
   if false:
      search in: all
      search text: "元請けとして、以下に示す同種工事"
      if found : 
         take right : 
            search in : taken
            search text : "【企業】"
            if found : 
               take right : 
                  search in : taken
                  search text : "同種工事："
                  if found : 
                     take left : 
                        remove whitespaces
                        store(var_ts_kigyo_false)
                        set(var_ts_kigyo_false)

「より同種性の高い」:
   search in : all
   search text : ["※１：" , "を「より同種性が高い」と評価"]
   if found : 
      search in : all 
      search text : "※１："
      if found : 
         take right : 
            search in : taken
            search text : "同種工事のうち、"
            if found : 
               take right : 
                  search in : taken
                  search text : "を「より同種性が高い」と評価"
                  if found : 
                     take left : 
                        remove whitespaces
                        store(var_high)
                        set(var_high)
   if not found : 
      set("該当なし")
