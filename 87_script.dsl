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
         take right:
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
               search text : "(電子入札対象案件)"
               if found : 
                  take left :
                     remove whitespaces
                     store(var_kouji)
                     set(var_kouji)


「同種工事(企業)」:
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

「同種工事(技術者)」:
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
               set(「同種工事(企業)」)


「より高い同種性(企業)doushusei_co_0」:  
   check : name_of
   has value : 本官
   if true : 
   if false : 
      search in : all
      search text : ("より高い同種性が認められる工事:" , "高い同種性が認められる工事:")
      if found : 
         search in : all
         search text : "企業の能力等(加算点)で提出した企業において"
         if found : 
            take right:
               search in : taken
               search text : "企業の能力等(加算点)"
               if found : 
                  take right : 
                     search in : taken
                     search text : "より高い同種性が認められる工事:"
                     if found : 
                        take right :
                           search in : taken
                           search text :  "より高い同種性が認められる工事の実績"
                           if found : 
                              take left : 
                                 remove whitespaces
                                 store(var10)
                                 set(var10)
      if not found : 
         search in : all
         search text : "企業の能力等("
         if found : 
            take right : 
               search in : taken
               search text : "同種工事の実績において、"
               if found : 
                  take right : 
                     search in : taken
                     search text : "で評価し、"
                     if found : 
                        take left : 
                           remove whitespaces
                           store(var20)
                           set(var20)

「同種性(企業)doushusei_co_2」:  
   check : name_of
   has value : 本官
   if true : 
   if false : 
      search in : all
      search text : ("より高い同種性が認められる工事:" , "高い同種性が認められる工事:")
      if found : 
         search in : all
         search text : "企業の能力等(加算点)で提出した企業において"
         if found : 
            take right:
               search in : taken
               search text : "企業の能力等(加算点)"
               if found : 
                  take right : 
                     search in : taken
                     search text : "より高い同種性が認められる工事:"
                     if found : 
                        take right :
                           search in : taken
                           search text : "同種性が認められる工事:"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "共同企業体の構成員"
                                 if found : 
                                    take left : 
                                       remove whitespaces
                                       store(var40)
                                       set(var40)
                     if not found :    
                        search in : taken
                        search text : "同種性が認められる工事:"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "共同企業体の構成員"
                              if found : 
                                 take left : 
                                    remove whitespaces
                                    store(var50)
                                    set(var50)



「より高い同種性(技術者) doushusei_en_0」:
   check : name_of
   has value : 本官
   if true : 
   if false : 
      search in : all
      search text : ("より高い同種性が認められる工事:" , "高い同種性が認められる工事:")
      if found : 
         search in : all
         search text : "企業の能力等(加算点)で提出した企業において"
         if found : 
            take right:
               search in : taken
               search text : "企業の能力等(加算点)"
               if found : 
                  take right : 
                     search in : taken
                     search text : "より高い同種性が認められる工事:"
                     if found : 
                        take right :
                           search in : taken
                           search text : "同種性が認められる工事:"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "技術者の能力等(加算点)"
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : "より高い同種性が認められる工事:"
                                       if found : 
                                          take right : 
                                             search in : taken
                                             search text : "より高い同種性が認められる工事の実績"
                                             if found : 
                                                take left : 
                                                   remove whitespaces
                                                   store(var60)
                                                   set(var60)
                           if not found : 
                              search in : taken
                              search text : "技術者の能力等(加算点)"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "より高い同種性が認められる工事:"
                                    if found : 
                                       take right : 
                                          search in : taken
                                          search text : "より高い同種性が認められる工事の実績"
                                          if found : 
                                             take left : 
                                                remove whitespaces
                                                store(var60)
                                                set(var60)
                     if not found :    
                        search in : taken
                        search text : "同種性が認められる工事:"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "技術者の能力等(加算点)"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "より高い同種性が認められる工事:"
                                    if found : 
                                       take right : 
                                          search in : taken
                                          search text : "より高い同種性が認められる工事の実績"
                                          if found : 
                                             take left : 
                                                remove whitespaces
                                                store(var60)
                                                set(var60)
                        if not found : 
                           search in : taken
                           search text : "技術者の能力等(加算点)"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "より高い同種性が認められる工事:"
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : "より高い同種性が認められる工事の実績"
                                       if found : 
                                          take left : 
                                             remove whitespaces
                                             store(var60)
                                             set(var60)
      if not found : 
         search in : all
         search text : "企業の能力等("
         if found : 
            take right : 
               search in : taken
               search text : "同種工事の実績において、"
               if found : 
                  take right : 
                     search in : taken
                     search text : 

「高い同種性(技術者) doushusei_en_1」:
   check : name_of
   has value : 本官
   if true : 
   if false : 
      search in : all
      search text : ("より高い同種性が認められる工事:" , "高い同種性が認められる工事:")
      if found : 
         search in : all
         search text : "企業の能力等(加算点)で提出した企業において"
         if found : 
            take right:
               search in : taken
               search text : "企業の能力等(加算点)"
               if found : 
                  take right : 
                     search in : taken
                     search text : "より高い同種性が認められる工事:"
                     if found : 
                        take right :
                           search in : taken
                           search text : "同種性が認められる工事:"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "技術者の能力等(加算点)"
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : "より高い同種性が認められる工事:"
                                       if found : 
                                          take right : 
                                             search in : taken
                                             search text : "高い同種性が認められる工事:"
                                             if found : 
                                                search in : taken
                                                search text : "同種性が認められる工事:"
                                                if found : 
                                                   take right : 
                                                      search in : taken
                                                      search text : "高い同種性が認められる工事の実績"
                                                      if found : 
                                                         take left : 
                                                            remove whitespaces
                                                            store(var60)
                                                            set(var60)
                                       if not found : 
                                          search in : taken
                                          search text : "高い同種性が認められる工事:"
                                          if found : 
                                             search in : taken
                                             search text : "同種性が認められる工事:"
                                             if found : 
                                                take right : 
                                                   search in : taken
                                                   search text : "高い同種性が認められる工事の実績"
                                                   if found : 
                                                      take left : 
                                                         remove whitespaces
                                                         store(var60)
                                                         set(var60)
                           if not found : 
                              search in : taken
                              search text : "技術者の能力等(加算点)"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "より高い同種性が認められる工事:"
                                    if found : 
                                       take right : 
                                          search in : taken
                                          search text : "高い同種性が認められる工事:"
                                          if found : 
                                             search in : taken
                                             search text : "同種性が認められる工事:"
                                             if found : 
                                                take right : 
                                                   search in : taken
                                                   search text : "高い同種性が認められる工事の実績"
                                                   if found : 
                                                      take left : 
                                                         remove whitespaces
                                                         store(var60)
                                                         set(var60)
                                    if not found : 
                                       search in : taken
                                       search text : "高い同種性が認められる工事:"
                                       if found : 
                                          search in : taken
                                          search text : "同種性が認められる工事:"
                                          if found : 
                                             take right : 
                                                search in : taken
                                                search text : "高い同種性が認められる工事の実績"
                                                if found : 
                                                   take left : 
                                                      remove whitespaces
                                                      store(var60)
                                                      set(var60)
                     if not found :    
                        search in : taken
                        search text : "同種性が認められる工事:"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "技術者の能力等(加算点)"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "より高い同種性が認められる工事:"
                                    if found : 
                                       take right : 
                                          search in : taken
                                          search text : "高い同種性が認められる工事:"
                                          if found : 
                                             search in : taken
                                             search text : "同種性が認められる工事:"
                                             if found : 
                                                take right : 
                                                   search in : taken
                                                   search text : "高い同種性が認められる工事の実績"
                                                   if found : 
                                                      take left : 
                                                         remove whitespaces
                                                         store(var60)
                                                         set(var60)
                                    if not found : 
                                       search in : taken
                                       search text : "高い同種性が認められる工事:"
                                       if found : 
                                          search in : taken
                                          search text : "同種性が認められる工事:"
                                          if found : 
                                             take right : 
                                                search in : taken
                                                search text : "高い同種性が認められる工事の実績"
                                                if found : 
                                                   take left : 
                                                      remove whitespaces
                                                      store(var60)
                                                      set(var60)
                        if not found : 
                           search in : taken
                           search text : "技術者の能力等(加算点)"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "より高い同種性が認められる工事:"
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : "高い同種性が認められる工事:"
                                       if found : 
                                          search in : taken
                                          search text : "同種性が認められる工事:"
                                          if found : 
                                             take right : 
                                                search in : taken
                                                search text : "高い同種性が認められる工事の実績"
                                                if found : 
                                                   take left : 
                                                      remove whitespaces
                                                      store(var60)
                                                      set(var60)
                                 if not found : 
                                    search in : taken
                                    search text : "高い同種性が認められる工事:"
                                    if found : 
                                       search in : taken
                                       search text : "同種性が認められる工事:"
                                       if found : 
                                          take right : 
                                             search in : taken
                                             search text : "高い同種性が認められる工事の実績"
                                             if found : 
                                                take left : 
                                                   remove whitespaces
                                                   store(var60)
                                                   set(var60)


「同種性(技術者) doushusei_en_2」:
   check : name_of
   has value : 本官
   if true : 
   if false : 
      search in : all
      search text : ("より高い同種性が認められる工事:" , "高い同種性が認められる工事:")
      if found : 
         search in : all
         search text : "企業の能力等(加算点)で提出した企業において"
         if found : 
            take right:
               search in : taken
               search text : "企業の能力等(加算点)"
               if found : 
                  take right : 
                     search in : taken
                     search text : "より高い同種性が認められる工事:"
                     if found : 
                        take right :
                           search in : taken
                           search text : "同種性が認められる工事:"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "技術者の能力等(加算点)"
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : "より高い同種性が認められる工事:"
                                       if found : 
                                          take right : 
                                             search in : taken
                                             search text : "高い同種性が認められる工事:"
                                             if found : 
                                                search in : taken
                                                search text : "同種性が認められる工事:"
                                                if found : 
                                                   take right : 
                                                      search in : taken
                                                      search text : "同種性が認められる工事:"
                                                      if found : 
                                                         take right : 
                                                            search in : taken
                                                            search text : "共同企業体の構成員"
                                                            if found : 
                                                               take left : 
                                                                  remove whitespaces
                                                                  store(var60)
                                                                  set(var60)
                                             if not found : 
                                                search in : taken
                                                search text : "同種性が認められる工事:"
                                                if found : 
                                                   take right : 
                                                      search in : taken
                                                      search text : "共同企業体の構成員"
                                                      if found : 
                                                         take left : 
                                                            remove whitespaces
                                                            store(var60)
                                                            set(var60)
                                       if not found : 
                                          search in : taken
                                          search text : "同種性が認められる工事:"
                                          if found : 
                                             take right : 
                                                search in : taken
                                                search text : "高い同種性が認められる工事の実績"
                                                if found : 
                                                   take left : 
                                                      remove whitespaces
                                                      store(var60)
                                                      set(var60)
                           if not found : 
                              search in : taken
                              search text : "技術者の能力等(加算点)"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "より高い同種性が認められる工事:"
                                    if found : 
                                       take right : 
                                          search in : taken
                                          search text : "高い同種性が認められる工事:"
                                          if found : 
                                             search in : taken
                                             search text : "同種性が認められる工事:"
                                             if found : 
                                                take right : 
                                                   search in : taken
                                                   search text : "同種性が認められる工事:"
                                                   if found : 
                                                      take right : 
                                                         search in : taken
                                                         search text : "共同企業体の構成員"
                                                         if found : 
                                                            take left : 
                                                               remove whitespaces
                                                               store(var60)
                                                               set(var60)
                                    if not found : 
                                       search in : taken
                                       search text : "同種性が認められる工事:"
                                       if found : 
                                          take right : 
                                             search in : taken
                                             search text : "高い同種性が認められる工事の実績"
                                             if found : 
                                                take left : 
                                                   remove whitespaces
                                                   store(var60)
                                                   set(var60)
                     if not found :    
                        search in : taken
                        search text : "同種性が認められる工事:"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "技術者の能力等(加算点)"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "より高い同種性が認められる工事:"
                                    if found : 
                                       take right : 
                                          search in : taken
                                          search text : "高い同種性が認められる工事:"
                                          if found : 
                                             search in : taken
                                             search text : "同種性が認められる工事:"
                                             if found : 
                                                take right : 
                                                   search in : taken
                                                   search text : "同種性が認められる工事:"
                                                   if found : 
                                                      take right : 
                                                         search in : taken
                                                         search text : "共同企業体の構成員"
                                                         if found : 
                                                            take left : 
                                                               remove whitespaces
                                                               store(var60)
                                                               set(var60)
                                          if not found : 
                                             search in : taken
                                             search text : "同種性が認められる工事:"
                                             if found : 
                                                take right : 
                                                   search in : taken
                                                   search text : "共同企業体の構成員"
                                                   if found : 
                                                      take left : 
                                                         remove whitespaces
                                                         store(var60)
                                                         set(var60)
                                    if not found : 
                                       search in : taken
                                       search text : "同種性が認められる工事:"
                                       if found : 
                                          take right : 
                                             search in : taken
                                             search text : "高い同種性が認められる工事の実績"
                                             if found : 
                                                take left : 
                                                   remove whitespaces
                                                   store(var60)
                                                   set(var60)
                        if not found : 
                           search in : taken
                           search text : "技術者の能力等(加算点)"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "より高い同種性が認められる工事:"
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : "高い同種性が認められる工事:"
                                       if found : 
                                          search in : taken
                                          search text : "同種性が認められる工事:"
                                          if found : 
                                             take right : 
                                                search in : taken
                                                search text : "同種性が認められる工事:"
                                                if found : 
                                                   take right : 
                                                      search in : taken
                                                      search text : "共同企業体の構成員"
                                                      if found : 
                                                         take left : 
                                                            remove whitespaces
                                                            store(var60)
                                                            set(var60)
                                 if not found : 
                                    search in : taken
                                    search text : "同種性が認められる工事:"
                                    if found : 
                                       take right : 
                                          search in : taken
                                          search text : "高い同種性が認められる工事の実績"
                                          if found : 
                                             take left : 
                                                remove whitespaces
                                                store(var60)
                                                set(var60)


「配点(企業)」: 
   check : name_of
   has value : 本官
   if true : 
   if false : 
      search in : all
      search text : ("より高い同種性が認められる工事:" , "高い同種性が認められる工事:")
      if found : 
         search in : all
         search text : "企業の能力等(加算点)で提出した企業において"
         if found : 
            take right:
               search in : taken
               search text : "企業の能力等(加算点)"
               if found : 
                  take right : 
                     search in : taken
                     search text : "で評価し、それぞれ"
                     if found : 
                        take right :  
                           search in : taken
                           search text : "の加算点を"
                           if found : 
                              take left : 
                                 remove whitespaces 
                                 store(score_co)
                                 set(score_co)
      if not found : 
         search in : all
         search text : "企業の能力等("
         if found : 
            take right : 
               search in : taken
               search text : "、それぞれ"
               if found : 
                  take right : 
                     search in : taken
                     search text : "の加算点を与える。"
                     if found : 
                        take left : 
                           remove whitespaces
                           store(score_co)
                           set(score_co)


「配点(技術者)」: 
   check : name_of
   has value : 本官
   if true : 
      search in : all
      search text : "技術者の能力等("
      if found :  
         take right : 
            search in : taken
            search text : "で評価し、"
            if found :  
               take right : 
                  search in : taken
                  search text : "の加算点を与える。"
                  if found : 
                     take left : 
                        replace("それぞれ","")
                        remove whitespaces
                        store(score_en)
                        set(score_en)

   if false : 
      search in : all
      search text : ("より高い同種性が認められる工事:" , "高い同種性が認められる工事:")
      if found : 
         search in : all
         search text : "企業の能力等(加算点)で提出した企業において"
         if found : 
            take right:
               search in : taken
               search text : "企業の能力等(加算点)"
               if found : 
                  take right : 
                     search in : taken
                     search text : "より高い同種性が認められる工事:"
                     if found : 
                        take right :
                           search in : taken
                           search text : "同種性が認められる工事:"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "技術者の能力等(加算点)"
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : "で評価し、それぞれ"
                                       if found : 
                                          take right : 
                                             search in : taken
                                             search text : "の加算点を"
                                             if found : 
                                                take left : 
                                                   remove whitespaces
                                                   store(score_en)
                                                   set(score_en)
                           if not found : 
                              search in : taken
                              search text : "技術者の能力等(加算点)"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "で評価し、それぞれ"
                                    if found : 
                                       take right : 
                                          search in : taken
                                          search text : "の加算点を"
                                          if found : 
                                             take left : 
                                                remove whitespaces
                                                store(score_en)
                                                set(score_en)
                     if not found :    
                        search in : taken
                        search text : "同種性が認められる工事:"
                        if found : 
                           take right : 
                              search in : taken
                              search text : "技術者の能力等(加算点)"
                              if found : 
                                 take right : 
                                    search in : taken
                                    search text : "で評価し、それぞれ"
                                    if found : 
                                       take right : 
                                          search in : taken
                                          search text : "の加算点を"
                                          if found : 
                                             take left : 
                                                remove whitespaces
                                                store(score_en)
                                                set(score_en)
                        if not found : 
                           search in : taken
                           search text : "技術者の能力等(加算点)"
                           if found : 
                              take right : 
                                 search in : taken
                                 search text : "で評価し、それぞれ"
                                 if found : 
                                    take right : 
                                       search in : taken
                                       search text : "の加算点を"
                                       if found : 
                                          take left : 
                                             remove whitespaces
                                             store(score_en)
                                             set(score_en)
      if not found : 
         search in : all
         search text : "企業の能力等("
         if found : 
            take right : 
               search in : taken
               search text : "技術者の能力等("
               if found : 
                  take right : 
                     search in : taken
                     search text : "で評価し、"
                     if found : 
                        take right :  
                           search in : taken
                           search taken : "の加算点を与える。"
                           if found : 
                              take left : 
                                 replace("それぞれ","")
                                 remove whitespaces
                                 store(score_en)
                                 set(score_en)
                        