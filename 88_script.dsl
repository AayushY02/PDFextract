has_eval_phrase :
   search in : all
   search text : "総合評価に関する評価項目"
   if found :
      set(true)
   if not found :
      set(false)

name_bu : 
   search in : all
   search text : "四国地方整備局"
   if found : 
      set("四国地方整備局")

name_of :
   search in : all
   search text : "支出負担行為担当官四国地方整備局長"
   if found :
      set("本官")
   if not found : 
      search in : all
      search text : "分任支出負担行為担当官"
      if found :
         take right : 
            search in : taken
            search text : "四国地方整備局"
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
      take right:
         search in : taken
         search text : "(2)"
         if found : 
            take left : 
               search in : taken
               search text : "(電子入札及び電子契約対象案件)"
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
   search in : all
   search text : "下記の条件を満足する同種工事を施工した実績を有すること"
   if found : 
      take right :
         store(text0)
         search in : taken
         search text : "実績に限る。\n･同種工事とは、"
         if found : 
            take right : 
               search in : taken
               search text : "なお、当該実績が"
               if found : 
                  take left : 
                     replace("を有すること。","")
                     store(var3)
                     set(var3)
         if not found : 
            search in : taken
            search text : "実績に限る。\n同種工事とは、"
            if found : 
               take right : 
                  search in : taken
                  search text : "なお、当該実績が"
                  if found : 
                     take left : 
                        replace("を有すること。","")
                        store(var4)
                        set(var4)
            if not found : 
               search in : taken
               search text : "実績に限る。\n･"
               if found : 
                  take right : 
                     search in : taken
                     search text : "なお、当該実績が"
                     if found : 
                        take left : 
                           replace("を有すること。","")
                           store(var5)
                           set(var5)
               if not found :
                  search in : taken
                  search text : "･同種工事として"
                  if found :  
                     take right : 
                     search in : taken
                     search text : "なお、当該実績が"
                     if found : 
                        take left : 
                           replace("を有すること。","")
                           store(exception2)
                           set(exception2)
               if not found : 
                  search in : taken
                  search text : "実績に限る。 同種工事とは、"
                  if found : 
                     take right : 
                     search in : taken
                     search text : "なお、当該実績が"
                     if found : 
                        take left : 
                           replace("を有すること。","")
                           store(exception2)
                           set(exception2)
   if not found : 
      search in : all
      search text : "下記の条件を満足する同種工事1を施工した実績を有すること"
      if found : 
         take right : 
            store(text0)
            search in : taken
            search text :  "同種工事1とは、"
            if found : 
               take right : 
                  search in : taken
                  search text : "なお、当該実績は"
                  if found : 
                     take left : 
                        replace("を有すること。","")
                        store(var6)
                        set(var6)
        


「同種工事（技術者）」:
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "同種工事2の経験を有する者"
      if found : 
         search in : text0
         search text : "同種工事2とは"
         if found : 
            take right :  
               search in : taken
               search text : "なお、当該経験は"
               if found :
                  take left : 
                     replace("を有すること。", "")
                     store(var1)
                     set(var1)
   if false:
      search in: all
      search text: "同種工事(上記(4)に掲げる工事)の経験を有する者であること"
      if found : 
         set(「同種工事（企業）」)
      if not found :
         search in : text0
         search text : "元請けの技術者として"
         if found : 
            take right : 
               search in : taken
               search text : ("(共同企業体の構成員としての経験は", " 共同企業体の構成員としての経験は")
               if found : 
                  take left : 
                     replace("を有すること。", " ")
                     store(var2)
                     set(var2)


「より同種性の高い（技術者）」: 
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "同種工事2の経験を有する者"
      if found : 
         search in : all
         search text : "1)技術者評価"
         if found : 
            take right : 
               search in : taken
               search text : "「より同種性の高い工事」とは、同種工事2のうち「"
               if found : 
                  take right : 
                     search in : taken
                     search text : "」とする。"
                     if found : 
                        take left : 
                           store(var5)
                           set(var5)
   if false : 
      search in : all
      search text : ("「より同種性の高い工事」:" , "「同種性が認められる工事」")
      if found : 
         search in : all
         search text : ("1)技術者評価" , "2)技術者評価")
         if found : 
            take right:
               search in : taken
               search text : ("」における「より同種性の高い工事」とは、" , "」 における「より同種性の高い工事」とは" , "における「より同種性の高い工事」とは、")
               if found : 
                  take right : 
                     search in : taken
                     search text : "を有することとする。"
                     if found : 
                        take left : 
                           store(var3)
                           set(var3)
                     if not found : 
                        search in : taken
                        search text : "とする。"
                        if found : 
                           take left:
                              store(var4)
                              set(var4)


「同種性が認められる（技術者）」:
   check : name_of
   has value : 本官
   if true :
      search in : all
      search text : "同種工事2の経験を有する者"
      if found : 
         search in : all
         search text : ("1)技術者評価" , "2)技術者評価")
         if found : 
            take right : 
               search in : taken
               search text : "「同種性が認められる工事」とは、"
               if found : 
                  take right : 
                     search in : taken
                     search text : "記載している同種工事2を示す。"
                     if found : 
                        set(「同種工事（技術者）」)
   if false : 
      search in : all
      search text : ("「より同種性の高い工事」：" , "「同種性が認められる工事」")
      if found : 
         search in : all
         search text : ("1)技術者評価" , "2)技術者評価")
         if found : 
            take right :
               search in : taken
               search text : "「同種性が認められる工事」とは、"
               if found : 
                  take right : 
                     search in : taken
                     search text : "記載している同種工事を示す。"
                     if found : 
                        set(「同種工事（技術者）」)

「より同種性の高い（企業）」:
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "同種工事2の経験を有する者"
      if found : 
         search in : all
         search text : ("1)技術者評価" , "2)技術者評価")
         if found : 
            take right : 
               search in : taken
               search text : "．企業の施工実績"
               if found : 
                  take right : 
                     search in : taken
                     search text : "「より同種性の高い工事」とは、同種工事1のうち「"
                     if found :
                        take right : 
                           search in : taken
                           search text : "」とする。"
                           if found : 
                              take left : 
                                 store(var8)
                                 set(var8)       
   if false : 
      search in : all
      search text : ("「より同種性の高い工事」：", "「同種性が認められる工事」")
      if found : 
         search in : all
         search text : ("1)技術者評価" , "2)技術者評価")
         if found : 
            take right : 
               search in : taken
               search text : ".企業の施工実績"
               if found : 
                  take right : 
                     search in : taken
                     search text : "示す。「より同種性の高い工事」とは、"
                     if found : 
                        take right : 
                           search in : taken
                           search text : "を有することとする。"
                           if found : 
                              take left : 
                                 store(var7)
                                 set(var7)
                           if not found : 
                              search in : taken
                              search text : "とする。"
                              if found : 
                                 take left : 
                                    store(var8)
                                    set(var8)
                     if not found : 
                        search in : taken
                        search text : "示す「より同種性の高い"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "とする「同種性が認められる工事」"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : ("。 とは、", "。")
                                    if found : 
                                       take left :
                                          store(exception1)
                                          set(exception1) 
                        if not found : 
                           search in : taken
                           search text : "示す。「より同種性の高"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "い工事」とは、"
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : "を有することとする。"
                                       if found : 
                                          take left : 
                                             store(exception4)
                                             set(exception4)
                                       if not found : 
                                          search in : taken
                                          search text : "とする。"
                                          if found : 
                                             take left : 
                                                store(exception4)
                                                set(exception4)


「同種性が認められる（企業）」: 
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "同種工事2の経験を有する者"
      if found : 
         search in : all
         search text : ("1)技術者評価" , "2)技術者評価")
         if found : 
            take right : 
               search in : taken
               search text : ".企業の施工実績"
               if found : 
                  take right : 
                     search in : taken
                     search text : "「同種性が認められる工事」\nとは、"
                     if found :
                        take right : 
                           search in : taken
                           search text : "記載している同種工事1を示す。"
                           if found : 
                              set(「同種工事（企業）」)     
   if false : 
      search in : all
      search text : ("「より同種性の高い工事」：", "「同種性が認められる工事」")
      if found : 
         search in : all
         search text : ("1)技術者評価" , "2)技術者評価")
         if found : 
            take right : 
               search in : taken
               search text : ".企業の施工実績"
               if found : 
                  take right : 
                     search in : taken
                     search text :  "「同種性が認められる工事」\nとは、"
                     if found : 
                        take right : 
                           search in : taken
                           search text : "記載している同種工事を示す。"
                           if found :    
                              set(「同種工事（企業）」)
                     if not found : 
                        search in : taken
                        search text : "「より同種性の高い工事」とは、"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "記載している同種工事を示す。"
                              if found : 
                                 set(「同種工事（企業）」)
                        if not found : 
                           search in : taken
                           search text : ["工事」とは、" , "「同種性が認められる工事」"]
                           if found : 
                              search in : taken
                              search text : "「同種性が認められる工事」"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "記載している同種工事を示す。"
                                    if found :  
                                       set(「同種工事（企業）」)
