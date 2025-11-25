has_eval_phrase :
   search in : all
   search text : "総合評価に関する評価項目"
   if found :
      set(true)
   if not found :
      set(false)

name_bu : 
   search in : all
   search text : "中国地方整備局"
   if found : 
      set("中国地方整備局")

name_of :
   search in : all
   search text : "支出負担行為担当官四国地方整備局長"
   if found :
      set("本官")
   if not found : 
      search in : all
      search text : "分任支出負担行為担当官"
      if found :
         take right
            search in : taken
            search text : "中国地方整備局"
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
               search text : "（電子入札対象案件）"
               if found : 
                  take left :
                     remove whitespaces
                     store(var_kouji)
                     set(var_kouji)


「同種工事（企業）」:
   search in : all
   search text : ["同種工事とは、", "なお、同種工事の施工実績は、"]
   if found : 
      search in : all
      search text : "同種工事とは、"
      if found : 
         take right :  
            search in : taken
            search text : "なお、同種工事の施工実績は、"
            if found : 
               take left : 
                  remove whitespaces
                  store(var3)
                  set(var3)  

「同種工事（技術者）」:
   search in : all
   search text : "現場での作業に配置する技術者は、"
   if found : 
      take right : 
         search in : taken
         search text :  "同種工事とは、"
         if found : 
            take right : 
               search in : taken
               search text : "ただし、"
               if found : 
                  take left : 
                     remove whitespaces
                     store(var4)
                     set(var4)
   if not found : 
      search in : all
      search text : "基準を満たす主任技術者又は監理技術者を当該工事に"
      if found : 
         take right : 
            search in : taken
            seach text : ("に掲げる同種工事の経験を有する者であること。" , "の同種工事の施工実績を有していること。")
            if found : 
               set(「同種工事（企業）」)


「より高い同種性（企業）doushusei_co_0」:  
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "同種工事２の経験を有する者"
      if found : 
         search in : all
         search text : "１）技術者評価"
         if found : 
            take right : 
               search in : taken
               search text : "「より同種性の高い工事」とは、同種工事２のうち「"
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
      search text : ("「より同種性の高い工事」：" , "「同種性が認められる工事」")
      if found : 
         search in : all
         search text : "１）技術者評価"
         if found : 
            take right:
               search in : taken
               search text : "」における「より同種性の高い工事」とは、"
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
      search text : "同種工事２の経験を有する者"
      if found : 
         search in : all
         search text : "１）技術者評価"
         if found : 
            take right : 
               search in : taken
               search text : "「同種性が認められる工事」とは、"
               if found : 
                  take right : 
                     search in : taken
                     search text : "記載している同種工事２を示す。"
                     if found : 
                        store(var7)
                        set(var7)

   if false : 
      search in : all
      search text : ("「より同種性の高い工事」：" , "「同種性が認められる工事」")
      if found : 
         search in : all
         search text : "１）技術者評価"
         if found : 
            take right :
               search in : taken
               search text : "「同種性が認められる工事」とは、"
               if found : 
                  take right : 
                     search in : taken
                     search text : 記載している同種工事を示す。
                     if found : 
                        store(var6)
                        set(var6)

「より同種性の高い（企業）」:
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "同種工事２の経験を有する者"
      if found : 
         search in : all
         search text : "１）技術者評価"
         if found : 
            take right : 
               search in : taken
               search text : "．企業の施工実績"
               if found : 
                  take right : 
                     search in : taken
                     search text : "「より同種性の高い工事」とは、同種工事１のうち「"
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
         search text : "１）技術者評価"
         if found : 
            take right : 
               search in : taken
               search text : "．企業の施工実績"
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


「同種性が認められる（企業）」: 
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "同種工事２の経験を有する者"
      if found : 
         search in : all
         search text : "１）技術者評価"
         if found : 
            take right : 
               search in : taken
               search text : "．企業の施工実績"
               if found : 
                  take right : 
                     search in : taken
                     search text : "「同種性が認められる工事」とは、"
                     if found :
                        take right : 
                           search in : taken
                           search text : "記載している同種工事１を示す。"
                           if found : 
                              set(「同種工事（企業）」)     
   if false : 
      search in : all
      search text : ("「より同種性の高い工事」：", "「同種性が認められる工事」")
      if found : 
         search in : all
         search text : "１）技術者評価"
         if found : 
            take right : 
               search in : taken
               search text : "．企業の施工実績"
               if found : 
                  take right : 
                     search in : taken
                     search text : "「同種性が認められる工事」とは、"
                     if found : 
                        take right : 
                           search in : taken
                           search text : "記載している同種工事を示す。"
                           if found :    
                              set(「同種工事（企業）」)