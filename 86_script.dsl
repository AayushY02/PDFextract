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
   search in : all
   search text : "支出負担行為担当官 近畿地方整備局長"
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
   
reg_A : 
   search in : all
   search text : "=== SECOND FILE START:"
   if found : 
      take right : 
         search in : taken
         search text : "==="
         if found : 
            take right :
               search in : taken
               search text : "=== THIRD FILE START:"
               if found : 
                  take left : 
                     store(region_A)
         
reg_B : 
   search in : all
   search text : "=== THIRD FILE START:"
   if found : 
      take right : 
         search in : taken
         search text : "==="
         if found : 
            take right :
               search in : taken
               search text : "=== END OF DOCUMENT ==="
               if found : 
                  take left :  
                     store(region_B)

「同種工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      search in : region_A
      search text : "4.競争参加資格に関する事項"
      if found : 
         take right : 
            search in : taken
            search text : "4.1 企業に対する要件"
            if found : 
               take right : 
                  search in : taken
                  search text : "4.1.5 同種工事の実績"
                  if found : 
                     take right :
                        search in : taken
                        search text : ("引渡しが完了した下記1)の要件を満たす工事(発注機関は問わない。)の施工実績を有すること。" , "引渡しが完了した下記1)の要件を満たす工事の施工実績を有すること。")
                        if found : 
                           take right : 
                              search in : taken
                              search text : ("なお、発注機関は国" , "・経常 JV にあっては" , "･経常JVにあっては")
                              if found : 
                                 take left:
                                    search in : taken
                                    search text : "1)"
                                    if found : 
                                       take right : 
                                          remove whitespaces
                                          replace("の施工実績。" , "")
                                          replace("。" , "")
                                          store(doushikouji_kigyo)
                                          set(doushikouji_kigyo)
   if false : 
      search in : region_A
      search text : "4.競争参加資格に関する事項"
      if found : 
         take right : 
            search in : taken
            search text : "4.1 企業に対する要件"
            if found : 
               take right : 
                  search in : taken
                  search text : "4.1.5 同種工事の実績"
                  if found : 
                     take right :
                        search in : taken
                        search text : ("引渡しが完了した下記1)の要件を満たす工事(発注機関は問わない。)の施工実績を有すること。" , "引渡しが完了した下記1)の要件を満たす工事の施工実績を有すること。")
                        if found : 
                           take right : 
                              search in : taken
                              search text : ("なお、発注機関は国" , "・経常 JV にあっては" , "･経常JVにあっては")
                              if found : 
                                 take left:
                                    search in : taken
                                    search text : "1)"
                                    if found : 
                                       take right : 
                                          remove whitespaces
                                          replace("の施工実績。" , "")
                                          replace("。" , "")
                                          store(doushikouji_kigyo)
                                          set(doushikouji_kigyo)

「同種工事（技術者）」temp:
   search in : region_A
   search text : "4.競争参加資格に関する事項"
   if found : 
      take right : 
         search in : taken
         search text : "4.1 企業に対する要件"
         if found : 
            take right : 
               search in : taken
               search text : "4.1.5 同種工事の実績"
               if found : 
                  take right :
                     search in : taken
                     search text : ("引渡しが完了した下記1)の要件を満たす工事(発注機関は問わない。)の施工実績を有すること。" , "引渡しが完了した下記1)の要件を満たす工事の施工実績を有すること。")
                     if found : 
                        take right : 
                           search in : taken
                           search text : "の施工実績を有すること。"
                           if found : 
                              take right:
                                 search in : taken
                                 search text : ("なお、発注機関は国" , "･甲型共同企業体構成員" )
                                 if found : 
                                    take left : 
                                       search in : taken
                                       search text : "神戸市発注の工事に限る。"
                                       if found : 
                                          take right : 
                                             remove whitespaces
                                             replace("2)" , "")
                                             replace("。" , "")
                                             store(doushikouji_g_temp)
                                             set(doushikouji_g_temp)
                                       if not found : 
                                          remove whitespaces
                                          replace("2)" , "")
                                          replace("。" , "")
                                          store(doushikouji_g_temp)
                                          set(doushikouji_g_temp)

「同種工事（技術者）」: 
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "4.競争参加資格に関する事項"
      if found : 
         take right : 
            search in : taken
            search text : "4.2 配置予定技術者に対する"
            if found : 
               take right : 
                  search in : taken
                  search text : "4.2.2 配置予定技術者の工事経験"
                  if found : 
                     take right :
                        search in : taken
                        search text : "競争参加資格要件"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "平成21年度以降に元請として完成し、引渡しが完了した上記4.1.5 1)の要件を満たす工事の経験を有する者であること。"
                              if found : 
                                 set(「同種工事（企業）」)
                              if not found : 
                                 search in : taken
                                 search text :("本工事では同種工事の経験は問わない" , "本工事では、配置予定技術者の工事経験は問わない")
                                 if found : 
                                    set("（該当無し）")
                                 if not found : 
                                    search in : taken
                                    search text : "平成21年度以降に元請として完成し、引渡しが完了した上記4.1.5 2)の要件を満たす工事"
                                    if found : 
                                       set(「同種工事（技術者）」temp)
   if false : 
      search in : region_A
      search text : "4.競争参加資格に関する事項"
      if found : 
         take right : 
            search in : taken
            search text : "4.2 配置予定技術者に対する"
            if found : 
               take right : 
                  search in : taken
                  search text : "4.2.2 配置予定技術者の工事経験"
                  if found : 
                     take right :
                        search in : taken
                        search text : "競争参加資格要件"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "平成21年度以降に元請として完成し、引渡しが完了した上記4.1.5 1)の要件を満たす工事の経験を有する者であること。"
                              if found : 
                                 set(「同種工事（企業）」)
                              if not found : 
                                 search in : taken
                                 search text :("本工事では同種工事の経験は問わない" , "本工事では、配置予定技術者の工事経験は問わない")
                                 if found : 
                                    set("（該当無し）")
                                 if not found : 
                                    search in : taken
                                    search text : "平成21年度以降に元請として完成し、引渡しが完了した上記4.1.5 2)の要件を満たす工事"
                                    if found : 
                                       set(「同種工事（技術者）」temp)

「より同種性が高い工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "[[HEADING]] 5.1 技術評価項目"
      if found : 
         take right : 
            search in : taken
            search text : "5.1.1 企業の施工能力"
            if found : 
               take right : 
                  search in : taken
                  search text : "5.1.1.1 同種性の高い施工実績 |"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "･コリンズ又は"
                        if found : 
                           take left : 
                              search in : taken
                              search text : "【評価方法】"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "であれば4点"
                                    if found : 
                                       take left : 
                                          remove whitespaces
                                          replace("の施工実績" , "")
                                          store(temp04)
                                          set(temp04)
   if false : 
      search in : region_B
      search text : "5.1 技術評価項目"
      if found : 
         take right : 
            search in : taken
            search text : ("5.1.1 企業の施工能力" , "5.1.1 企業の 施工能力")
            if found : 
               take right : 
                  search in : taken
                  search text : "5.1.1.1 同種性の高い施工実績"
                  if found : 
                     take right :
                        search in : taken
                        search text : "【評価方法】"
                        if found : 
                           take right : 
                              search in : taken
                              search text : ("･様式2" , "･申請書及び資料")
                              if found : 
                                 take left:
                                    search in : taken
                                    search text : "であれば4点"
                                    if found : 
                                       take left :
                                          remove whitespaces
                                          store(yoridoushiseigatakaikouji_kigyo)
                                          set(yoridoushiseigatakaikouji_kigyo)
                  if not found : 
                     set("（該当無し）")

「高い同種性が認められる工事（企業）」:
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "[[HEADING]] 5.1 技術評価項目"
      if found : 
         take right : 
            search in : taken
            search text : "5.1.1 企業の施工能力"
            if found : 
               take right : 
                  search in : taken
                  search text : "5.1.1.1 同種性の高い施工実績 |"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "･コリンズ又は"
                        if found : 
                           take left : 
                              search in : taken
                              search text : "【評価方法】"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "であれば4点、"
                                    if found : 
                                       take right :
                                          search in : taken
                                          search text : "であれば2点"
                                          if found : 
                                             take left : 
                                                remove whitespaces
                                                add in left("同種工事の経験において")
                                                replace("の施工実績" , "")
                                                store(temp05)
                                                set(temp05)
   if false : 
      search in : region_B
      search text : "5.1 技術評価項目"
      if found : 
         take right : 
            search in : taken
            search text : ("5.1.1 企業の施工能力" , "5.1.1 企業の 施工能力")
            if found : 
               take right : 
                  search in : taken
                  search text : "5.1.1.1 同種性の高い施工実績"
                  if found : 
                     take right :
                        search in : taken
                        search text : "【評価方法】"
                        if found : 
                           take right : 
                              search in : taken
                              search text : ("･様式2" , "･申請書及び資料")
                              if found : 
                                 take left:
                                    search in : taken
                                    search text : "であれば4点"
                                    if found : 
                                       take right :
                                          remove whitespaces
                                          replace("であれば2点" , "")
                                          replace("、" , "")
                                          store(var2)
                                          set(var2)
                  if not found : 
                     set("（該当無し）")

「より同種性が高い工事（技術者）」: 
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "[[HEADING]] 5.1 技術評価項目"
      if found : 
         take right : 
            search in : taken
            search text : "5.1.2 配置予定技術者の能力"
            if found : 
               take right : 
                  search in : taken
                  search text : "5.1.2.2 同種性の高い施工経験"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "･特例監理技術者"
                        if found : 
                           take left : 
                              search in : taken
                              search text : "【評価方法】"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "であれば 3点"
                                    if found : 
                                       take left :
                                          remove whitespaces
                                          replace("の施工実績" , "")
                                          store(temp06)
                                          set(temp06)
   if false : 
      search in : region_B
      search text : "5.1 技術評価項目"
      if found : 
         take right : 
            search in : taken
            search text : "5.1.2 配置予定技術者の能力"
            if found : 
               take right : 
                  search in : taken
                  search text : "5.1.2.1 同種工事の経験における監理技術者等としての施工経験"
                  if found : 
                     take right :
                        search in : taken
                        search text : "【評価方法】"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "･特例監理技術者" 
                              if found : 
                                 take left:
                                    search in : taken
                                    search text : "3点"
                                    if found : 
                                       take left :
                                          remove whitespaces
                                          store(var2)
                                          set(var2)
            if not found : 
               set("（該当無し）")

「高い同種性が認められる工事（技術者）」: 
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "[[HEADING]] 5.1 技術評価項目"
      if found : 
         take right : 
            search in : taken
            search text : "5.1.2 配置予定技術者の能力"
            if found : 
               take right : 
                  search in : taken
                  search text : "5.1.2.2 同種性の高い施工経験"
                  if found : 
                     take right : 
                        search in : taken
                        search text : "･特例監理技術者"
                        if found : 
                           take left : 
                              search in : taken
                              search text : "【評価方法】"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "であれば 3点、"
                                    if found : 
                                       take right :
                                          search in : taken
                                          search text : "であれば 1.5点"
                                          if found : 
                                             take left : 
                                                remove whitespaces
                                                add in left("同種工事の経験において")
                                                replace("の施工実績" , "")
                                                store(temp07)
                                                set(temp07)
   if false : 
      search in : region_B
      search text : "5.1 技術評価項目"
      if found : 
         take right : 
            search in : taken
            search text : "5.1.2 配置予定技術者の能力"
            if found : 
               take right : 
                  search in : taken
                  search text : "5.1.2.1 同種工事の経験における監理技術者等としての施工経験"
                  if found : 
                     take right :
                        search in : taken
                        search text : "【評価方法】"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "･特例監理技術者" 
                              if found : 
                                 take left:
                                    search in : taken
                                    search text : "3点"
                                    if found : 
                                       take right :
                                          remove whitespaces
                                          replace("1.5点" , "")
                                          store(var2)
                                          set(var2)
            if not found : 
               set("（該当無し）")