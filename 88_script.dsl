has_eval_phrase :
   search in : all
   search text : 総合評価に関する評価項目
   if found :
      set(true)
   if not found :
      set(false)

name_bu : 
   search in : all
   search text : 四国地方整備局
   if found : 
      set(四国地方整備局)

name_of :
   search in : all
   search text : 支出負担行為担当官四国地方整備局長
   if found :
      set(本官)
   if not found : 
      search in : all
      search text : 分任支出負担行為担当官
      if found :
         take right
            search in : taken
            search text : 四国地方整備局
            if found:
               take right:
                  search in : taken
                  search text : 所長
                  if found : 
                     take left:
                        remove whitespaces
                        add in right(所)
                        store(var_nameof)
                        set(var_nameof)

工事名:
   search in : all
   search text : 工事名
   if found : 
      take right:
         search in : taken
         search text : (2)
         if found : 
            take left : 
               search in : taken
               search text : （電子入札及び電子契約対象案件）
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
      search text : 同種工事２の経験を有する者
      if found : 
         search in : all
         search text : 発注者から企業に対して通知された評定点が
         if found : 
            search in : all
            search text : 同種工事２とは
            if found : 
               take right : 
                  search in : taken
                  search text : なお、当該経験は
                  if found :
                     take left : 
                        replace ("を有すること。", "")
                        store(var1)
                        set(var1)
   if false:
      search in: all
      search text: 同種工事（上記（４）に掲げる工事）の経験を有する者であること
      if found : 
         set(「同種工事（技術者）」)

同種工事（企業）:
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : [【企業】, 【技術者】]
      if found : 
         search in : all
         search text : 発注者から企業に対して通知された評定点が
         if found : 
            take right : 
               search in : taken
               search text : 【企業】
               if found : 
                  take right : 
                     search in : taken
                     search text : 同種工事：
                     if found : 
                        take left : 
                           search in : taken
                           search text : 【技術者】
                           if found : 
                              take left : 
                                 remove whitespaces
                                 store(var_ts_kigyo_true)
                                 set(var_ts_kigyo_true)
      if not found : 
         search in : all
         search text : 発注者から企業に対して通知された評定点が
         if found : 
            take right : 
               search in : taken
               search text : 同種工事：
               if found : 
                  take right : 
                     search in : taken
                     search text : (6)
                     if found : 
                        take left : 
                           remove whitespaces
                           store(var_ts_kigyo_true2)
                           set(var_ts_kigyo_true2)
   if false:
      search in: all
      search text: 元請けとして、以下に示す同種工事
      if found : 
         take right : 
            search in : taken
            search text : 【企業】
            if found : 
               take right : 
                  search in : taken
                  search text : 同種工事：
                  if found : 
                     take left : 
                        remove whitespaces
                        store(var_ts_kigyo_false)
                        set(var_ts_kigyo_false)

「より同種性の高い」:
   search in : all
   search text : [※１： , を「より同種性が高い」と評価]
   if found : 
      search in : all 
      search text : ※１：
      if found : 
         take right : 
            search in : taken
            search text : 同種工事のうち、
            if found : 
               take right : 
                  search in : taken
                  search text : を「より同種性が高い」と評価
                  if found : 
                     take left : 
                        remove whitespaces
                        store(var_high)
                        set(var_high)
   if not found : 
      set(該当なし)
