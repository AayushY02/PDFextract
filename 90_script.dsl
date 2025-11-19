has_eval_phrase :
    search in : all
    search text : "総合評価に関する事項"
    if found :
        set(true)
    if not found :
        set(false)

name_bu : 
    search in : all
    search text : "沖縄総合事務局"
    if found : 
        set("沖縄総合事務局")

name_of :
    search in : all
    search text : "支出負担行為担当官沖縄総合事務局開発建設部長"
    if found :
        set("本官")
    if not found : 
        search in : all
        search text : "分任支出負担行為担当官"
        if found :
            take right :
                search in : taken
                search text : "沖縄総合事務局"
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

「同種工事（企業）」:
    search in : all
    search text : ["「同種工事」は、次の要件を満たす" , "同種工事とは４．（４）に明示"]
    if found : 
        search in : all
        search text : "次に掲げる施工実績を有すること。"
        if found :  
            take right : 
                search in : taken
                search text : "「同種工事」は"
                if found : 
                    search in : taken
                    search text : "「同種工事」は、次の要件を満たす施工実績を有すること。・"
                    if found :
                        take left : 
                            remove whitespaces
                            store(v1)
                            set(v1)
                if not found : 
                    search in : taken
                    search text : "※施工実績が確認できる資料(コリンズ"
                    if found : 
                        take left : 
                            remove whitespaces
                            store(v2)
                            set(v2)
    if not found : 
        search in : all
        search text : ["・同種工事" , "・より同種工事"]
        if found :
            search in : all
            seach text : "次の要件を満たす施工実績を有すること。"
            if found : 
                take right : 
                    search in : taken
                    search text : "・同種工事："
                    if found : 
                        take right : 
                            search in : taken
                            search text : "・より同種工事："
                            if found :
                                take left :
                                    remove whitespaces
                                    store(v2)
                                    set(v2)
        if not found : 
            search in : all
            search text : "同種工事："
            if found : 
                search in : all
                search text : "次の要件を満たす施工実績を有すること。"
                if found :
                    take right : 
                        search in : taken
                        search text : "同種工事："
                        if found : 
                            take right :
                                search in : taken
                                search text : "※コリンズで"
                                if found : 
                                    take left : 
                                        remove whitespaces
                                        store(v3)
                                        set(v3)
            if not found : 
                search in : all
                search text : ["次の(ｱ)、(ｲ)の要件を満たす施工実績を有すること。", "同種工事とは４．（４）に明示"]
                if found : 
                    search in : all
                    search text : "次に掲げる施工実績を有すること。"
                    if found : 
                        take right : 
                            search in : taken
                            search text : "(ｲ)の要件を満たす施工実績を有すること。"
                            if found : 
                                take right : 
                                    search in : taken
                                    search text : "※コリンズで"
                                    if found :  
                                        take left : 
                                            remove whitespaces
                                            store(v4)
                                            set(v4)
                if not found :
                    search in : all
                    search text : ["次の要件を満たす施工実績を有すること", "同種工事とは４．（４）に明示"]
                    if found : 
                        search in : all
                        search text : "次の要件を満たす施工実績を有すること"
                        if found : 
                            take right : 
                                search in : taken
                                search text : "同種工事："
                                if found : 
                                    take right : 
                                        search in : taken
                                        search text : "※コリンズで"
                                        if found : 
                                            take left : 
                                                remove whitespaces
                                                store(v5)
                                                set(v5)
                                if not found : 
                                    search in : taken
                                    search text : "・"
                                    if found : 
                                        take right : 
                                            search in : taken
                                            search text : "※コリンズで"
                                            if found : 
                                                take left : 
                                                    remove whitespaces
                                                    store(v6)
                                                    set(v6)
                    if not found : 
                        set("記載なし")








    

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
        search text: "次に掲げる基準を満たす配置予定技術者"
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
                            store(var_ts_kigyo_false)
                            set(var_ts_kigyo_false)

「より同種性の高い」:
    search in : all
    search text : ["また、" , "を「より同種性が高い」と評価"]
    if found : 
        search in : all 
        search text : "また、"
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
