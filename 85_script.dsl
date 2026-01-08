has_eval_phrase :
   search in : all
   search text : "入札の評価に関する基準及び得点配分"
   if found :
      set(true)
   if not found :
      set(false)

name_bu : 
   search in : all
   search text : "中部地方整備局"
   if found : 
      set("中部地方整備局")

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

「工事名」:
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

reg_A : 
   search in : all
   search text : ("4.競争参加資格" , "4. 競争参加資格")
   if found : 
      take right : 
         search in : taken
         search text : ("5. 設計業務等の受託者等", "5.設計業務等の受託者等")
         if found : 
            take left : 
               store(region_A)
         
reg_B : 
   search in : all
   search text : ("9. 総合評価落札方式に関する事項", "9.総合評価落札方式に関する事項")
   if found : 
      take right : 
         store(region_B)

「同種工事（企業）」:
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
                                                   store(var_ts_kigyo_true)
                                                   set(var_ts_kigyo_true)
      if not found : 
         set("特殊工事のため要確認")
   if false:
      search in: region_A
      search text: "同種工事:"
      if found : 
         take right : 
            search in : taken
            search text : "また"
            if found : 
               take left :
                  remove whitespaces
                  replace("の施工実績", "")
                  store(new)
                  set(new)

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
                              take left : 
                                 remove whitespaces
                                 store(var_ts_gijutsu_true)
                                 set(var_ts_gijutsu_true)
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
                           store(var_ts_gijutsu_true2)
                           set(var_ts_gijutsu_true2)
   if false:
      search in: region_A
      search text: "次に掲げる基準を満たす配置予定技術者(監理技術者又は主任技術者)を当該工事に専任で配置できる"
      if found : 
         take right : 
            search in : taken
            search text : "同種工事:"
            if found : 
               take right : 
                  search in : taken
                  search text : "配置予定技術者と直接的かつ恒常的な雇用関係"
                  if found : 
                     take left : 
                        remove whitespaces
                        replace("の施工実績", "")
                        store(var_ts_gijutsu_false)
                        set(var_ts_gijutsu_false)

「より同種性の高い」:
   search in : region_A
   search text : "同種工事:"
   if found : 
      take right : 
         search in : taken
         search text : ["また、" , "を「より同種性が高い」と評価"]
         if found : 
            search in : taken 
            search text : "また、"
            if found : 
               take right : 
                  search in : taken
                  search text : "を「より同種性が高い」と評価"
                  if found : 
                     take left : 
                        remove whitespaces
                        replace("の施工実績", "")
                        store(var_high)
                        set(var_high)           
         if not found : 
            search in : taken
            search text : ["また、" , "を「よ"]
            if found : 
               search in : taken 
               search text : "また、"
               if found : 
                  take right : 
                     search in : taken
                     search text : "を「よ"
                     if found : 
                        take left : 
                           remove whitespaces
                           replace("の施工実績", "")
                           store(var_high)
                           set(var_high)    


「より同種性の高い（企業）」:
   check : name_of
   has value : 本官
   if true : 
   if false :
      search in : region_B
      search text : "工事の総合評価に関する加算点は以下のとおり付与する。"
      if found : 
         take right :
            search in : taken
            search text : "企業の 能力等 |"
            if found : 
               take right :
                  search in : taken
                  search text : "より同種"
                  if not found : 
                     set("該当無し")

「より同種性の高い（技術者）」:
   check : name_of
   has value : 本官
   if true : 
   if false :
      search in : region_B
      search text : "工事の総合評価に関する加算点は以下のとおり付与する。"
      if found : 
         take right :
            search in : taken
            search text : "技術者 の能力 |"
            if found : 
               take right :
                  search in : taken
                  search text : "より同種"
                  if not found : 
                     set("該当無し")
