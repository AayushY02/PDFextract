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
                    if not found : 
                        remove whitespaces
                        store(var_kouji)
                        set(var_kouji)

「同種工事(企業)」:
    search in : all
    search text : ["「同種工事」は、次の要件を満たす" , "同種工事とは4.(4)に明示"]
    if found : 
        search in : all
        search text : "次に掲げる施工実績を有すること。"
        if found : 
            take right : 
                store(text0)
                search in : text0
                search text : "※施工実績が確認できる資料(コリンズ"
                if found :
                    take left : 
                        remove whitespaces
                        store(text1)
                        set(text1)
    if not found : 
        search in : all
        search text : ["･同種工事", "･より同種工事"]
        if found :
            search in : all
            search text : "次の要件を満たす施工実績を有すること。"
            if found :  
                take right : 
                    store(text0)
                    search in : text0
                    search text : "･同種工事:"
                    if found : 
                        take right : 
                            search in : taken
                            search text : "･より同種工事:"
                            if found :
                                take left :
                                    remove whitespaces
                                    store(text1)
                                    set(text1)
        if not found : 
            search in : all
            search text : "同種工事:"
            if found : 
                search in : all
                search text : "次の要件を満たす施工実績を有すること。"
                if found :
                    take right : 
                        store(text0)
                        search in : text0
                        search text : "同種工事:"
                        if found : 
                            take right :
                                search in : taken
                                search text : ("※コリンズで" , "【注】 コリンズで")
                                if found : 
                                    take left : 
                                        remove whitespaces
                                        store(text1)
                                        set(text1)
            if not found : 
                search in : all
                search text : ["次の(ア)、(イ)の要件を満たす施工実績を有すること。", "同種工事とは4.(4)に明示"]
                if found : 
                    search in : all
                    search text : "次に掲げる施工実績を有すること。"
                    if found : 
                        take right : 
                            store(text0)
                            search in : text0
                            search text : "(イ)の要件を満たす施工実績を有すること。"
                            if found : 
                                take right : 
                                    search in : taken
                                    search text : ("※コリンズで" , "【注】 コリンズで")
                                    if found : 
                                        take left : 
                                            remove whitespaces
                                            store(text1)
                                            set(text1)
                if not found :
                    search in : all
                    search text : ["次の要件を満たす施工実績を有すること", "同種工事とは4.(4)に明示"]
                    if found : 
                        search in : all
                        search text : "次の要件を満たす施工実績を有すること"
                        if found : 
                            take right : 
                                store(text0)
                                search in : taken
                                search text : "同種工事:"
                                if found : 
                                    take right : 
                                        search in : taken
                                        search text : ("※コリンズで" , "【注】 コリンズで")
                                        if found : 
                                            take left : 
                                                remove whitespaces
                                                store(text1)
                                                set(text1)
                                if not found : 
                                    search in : taken
                                    search text : "･"
                                    if found : 
                                        take right : 
                                            search in : taken
                                            search text : ("※コリンズで" , "【注】 コリンズで")
                                            if found : 
                                                take left : 
                                                    remove whitespaces
                                                    store(text1)
                                                    set(text1)
                    if not found : 
                        set("記載なし")

「同種工事(技術者)」 :
    search in : all
    search text : ["工事に専任で配置できること", "に掲げる同種工事の要件を満たす工事現場に従事した経験を有する者"]
    if found :
        set(「同種工事(企業)」)
    if not found :
        search in : all
        search text : ["工事に専任で配置できること", "に掲げる要件の施工経験を有する者であること。"]
        if found :
            set(「同種工事(企業)」)
        if not found :
            set("記載なし")

「より同種性の高い(企業)」:
    check : name_of
    has value : 本官
    if true : 
        search in : all
        search text : ["同種工事:", "より同種工事:"]
        if found : 
            search in : text0
            search text : "同種工事とは4"
            if found : 
                take right : 
                    search in : taken
                    search text : "より同種工事とは、"
                    if found : 
                        take right : 
                            search in : taken
                            search text : "より同種工事:"
                            if found : 
                                take right : 
                                    search in : taken
                                    search text : "◇施工実績"
                                    if found : 
                                        take left : 
                                            remove whitespaces
                                            store(var30)
                                            set(var30)
    if false :     
        search in : all
        search text : ["同種工事とは", "より同種工事とは"]
        if found :
            search in : all
            search text : ["同種工事:", "より同種工事:"]
            if found : 
                search in : all
                search text : "同種工事とは4"
                if found : 
                    take right :
                        search in : taken
                        search text : "より同種工事とは、"
                        if found : 
                            take right : 
                                search in : taken
                                search text : "より同種工事:"
                                if found : 
                                    take right : 
                                        search in : taken
                                        search text : "◇施工実績"
                                        if found : 
                                            take left : 
                                                remove whitespaces
                                                store(var10)
                                                set(var10) 
                                if not found : 
                                    search in : taken
                                    search text : "次のとおりとする。\n･" 
                                    if found : 
                                        take right : 
                                            search in : taken
                                            search text : "◇施工実績"
                                            if found : 
                                                take left : 
                                                    remove whitespaces
                                                    store(exception1)
                                                    set(exception1)
            if not found : 
                search in : all
                search text : "同種工事とは4"
                if found : 
                    take right : 
                        search in : taken
                        search text : "より同種工事とは、"
                        if found : 
                            take right : 
                                search in : taken
                                search text :  "次のとおりとする。･"
                                if found : 
                                    take right : 
                                        search in : taken
                                        search text : "◇施工実績"
                                        if found : 
                                            take left : 
                                                remove whitespaces
                                                store(var20)
                                                set(var20)
                                if not found : 
                                    search in : taken
                                    search text : "次のとおりとする。\n･"
                                    if found : 
                                        take right : 
                                            search in : taken
                                            search text : "◇施工実績"
                                            if found : 
                                                take left : 
                                                    remove whitespaces
                                                    store(var20)
                                                    set(var20)


「同種工事(企業)」_doushu_co2 :
    check : name_of
    has value : 本官
    if true : 
        search in : all
        search text : ["同種工事:", "より同種工事:"]
        if found : 
            search in : all
            search text : "同種工事とは4"
            if found : 
                take right : 
                    search in : taken
                    search text : "より同種工事とは、"
                    if found : 
                        take right : 
                            search in : taken
                            search text : "より同種工事:"
                            if found : 
                                take right : 
                                    search in : taken
                                    search text : "◇施工実績"
                                    if found : 
                                        take left : 
                                            remove whitespaces
                                            store(var30)
                                            set(var30)
    if false :     
        search in : all
        search text : ["同種工事とは", "より同種工事とは"]
        if found :
            search in : all
            search text : ["同種工事:", "より同種工事:"]
            if found : 
                search in : all
                search text : "同種工事とは4"
                if found : 
                    take right :
                        search in : taken
                        search text : "同種工事:"
                        if found : 
                            take right : 
                                search in : taken
                                search text : "◇より同種工事とは"
                                if found : 
                                    take left : 
                                        remove whitespaces
                                        store(var50)
                                        set(var50) 
                        if not found : 
                            search in : taken 
                            search text : "おりである。"
                            if found : 
                                take right : 
                                    search in : taken
                                    search text : "･"
                                    if found : 
                                        take right : 
                                            search in : taken
                                            search text : "◇より同種工事とは"
                                            if found : 
                                                take left : 
                                                    remove whitespaces
                                                    store(exception2)
                                                    set(exception2) 
            if not found : 
                search in : all
                search text : "同種工事とは4"
                if found : 
                    take right : 
                        search in : taken
                        search text : ")に明示しているとおりである。\n･"
                        if found : 
                            take right : 
                                search in : taken
                                search text :  "◇より同種工事とは"
                                if found : 
                                    take left : 
                                        remove whitespaces
                                        store(var40)
                                        set(var40)

「より同種性の高い(技術者) doushu_en01」 :
    search in : all
    search text : "配置予定技術者の能力等(加算点2)"
    if found :
        search in : all
        search text : ("配置予定技術者に関する発注機関別の評価方法は、施工実績に準ずる" , "配置予定技術者に関する発注機関別の考え方は、施工実績に準ずる。")
        if found :
            set(「より同種性の高い(企業)」)
        if not found :
            set("")

「同種工事（技術者） doushu_en02」 :
    search in : text0
    search text : "配置予定技術者の能力等(加算点2)"
    if found :
        search in : all
        search text : ("配置予定技術者に関する発注機関別の評価方法は、施工実績に準ずる" , "配置予定技術者に関する発注機関別の考え方は、施工実績に準ずる。")
        if found :
            set(「同種工事(企業)」_doushu_co2)
        if not found :
            set("")