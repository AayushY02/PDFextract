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

reg_A : 
   search in : all
   search text : ("4.競争参加資格" , "4. 競争参加資格")
   if found : 
      take right : 
         search in : taken
         search text : ("5.総合評価に関する事項", "5. 総合評価に関する事項")
         if found : 
            take left : 
               store(region_A)
         
reg_B : 
   search in : all
   search text : ("5.総合評価に関する事項", "5.　総合評価に関する事項")
   if found : 
      take right : 
        store(region_B)

「同種工事(企業)」:
    check : name_of
    has value : 本官
    if true : 
        search in : region_A
        search text : "次に掲げる工事を元請として完成･引渡しが完了した次の要件を満たす同種工事の施工実績を有すること"
        if found : 
            take right : 
                search in : taken
                search text : "次に掲げる施工実績を有すること。"
                if found : 
                    take right : 
                        search in : taken
                        search text : "※コリンズで施工実績が確認できない場合"
                        if found : 
                            take left : 
                                remove whitespaces
                                store(temp01)
                                set(temp01)
    if false : 
        search in : region_A
        search text : "1社以上が次に掲げる施工実績を有すること。"
        if found :
            take right :  
                search in : taken
                search text : "次の要件を満たす施工実績を有すること。"
                if found : 
                    take right : 
                        search in : taken
                        search text : "同種工事:"
                        if found : 
                            take right : 
                                search in : taken
                                search text : ("※コリンズで施工実績が確認" , "･より同種工事:")
                                if found : 
                                    take left :
                                        remove whitespaces
                                        replace("の施工実績" , "")
                                        replace("であること。" , "")
                                        replace("を有すること。" , "")
                                        store(var1)
                                        set(var1)
                        if not found : 
                            search in : taken
                            search text : "※コリンズで施工実績が確認"
                            if found : 
                                take left : 
                                    remove whitespaces
                                    replace("の施工実績。" , "")
                                    replace("の施工実績" , "")
                                    replace("であること。" , "")
                                    replace("を有すること。" , "")
                                    store(var2)
                                    set(var2)
                if not found : 
                    search in : taken
                    search text : "次の(ア)、(イ)の要件を満たす施工実績を有すること。"
                    if found : 
                        search in : taken
                        search text : "※コリンズで施工実績が確認"
                        if found : 
                            take left : 
                                remove whitespaces
                                replace("であること。" , "")
                                replace("を有すること" , "")
                                store(var3)
                                set(var3)
                    if not found : 
                        search in : taken
                        search text : "※コリンズで施工実績が確認"
                        if found : 
                            take left : 
                                remove whitespaces
                                replace("を有すること" , "")
                                replace("であること。" , "")
                                store(var3)
                                set(var3)

「同種工事(技術者)」: 
    check : name_of
    has value : 本官
    if true : 
        search in : region_A
        search text : ("次に掲げる基準を満たす主任技術者又は監理技術者を当該工事に専任で配置", "次に掲げる基準を満たす主任技術者又は監理技術者を当該工事に配置")
        if found :
            take right : 
                search in : taken
                search text : "平成21年4月1日から技術資料等の提出期限日までに上記(4)に掲げる同種工事の要件を満たす工事現場に従事した経験を有する者であること"
                if found : 
                    set(「同種工事(企業)」)
    if false : 
        search in : region_A
        search text : ("次に掲げる基準を満たす主任技術者又は監理技術者を当該工事に専任で配置", "次に掲げる基準を満たす主任技術者又は監理技術者を当該工事に配置")
        if found :
            take right : 
                search in : taken
                search text : "専任補助者を配置する場合、主任技術者又は監理技術者"
                if found : 
                    take right : 
                        search in : taken
                        search text : "以下の"
                        if found : 
                            take right : 
                                search in : taken
                                search text : "があること"
                                if found : 
                                    take left : 
                                        remove whitespaces
                                        store(temp1)
                                search in : taken
                                search text : "65点未満のものは除く。"
                                if found : 
                                    take right : 
                                        search in : taken
                                        search text : "また、配置予定主任技術者又は監理技術者"
                                        if found : 
                                            take left : 
                                                remove whitespaces
                                                store(temp2)
                                                add in left(temp1)
                                                replace("を有すること。" , "")
                                                replace("であること。" , "")
                                                replace("があること" , "")
                                                store(temp3)
                                                set(temp3)
                if not found : 
                    search in : taken
                    search text : "技術資料等の提出期限日までに上記(4)に掲げる同種工事の要件を満たす工事現場に従事した経験を有する者であること(共同企業体"
                    if found : 
                        set(「同種工事(企業)」)

「同種工事(企業)」_doushu_co2:
    check : name_of
    has value : 本官
    if true : 
        search in : region_B
        search text : "2)評価基準及び得点配分"
        if found :
            take right : 
                search in : taken
                search text : "企業の能力等(加算点1)"
                if found : 
                    take right : 
                        search in : taken
                        search text : "◇同種工事とは4.(4)に明示しているとおりである。"
                        if found : 
                            take right : 
                                search in : taken
                                search text : "◇同種工事とは4.(4)に明示しているとおりである。"
                                if found : 
                                    take right : 
                                        search in : taken
                                        search text : "◇より同種工事とは"
                                        if found : 
                                            take left : 
                                                search in : taken
                                                search text : "同種工事:"
                                                if found : 
                                                    take right : 
                                                        remove whitespaces
                                                        replace("の施工実績。", "")
                                                        replace("の施工実績", "")
                                                        replace("を有すること。", "")
                                                        replace("を有すること", "")
                                                        replace("であること。", "")
                                                        replace("|", "")
                                                        store(varA)
                                                        set(varA)
                                                if not found : 
                                                    remove whitespaces
                                                    replace("の施工実績。", "")
                                                    replace("の施工実績", "")
                                                    replace("を有すること。", "")
                                                    replace("であること。", "")
                                                    replace("を有すること", "")
                                                    replace("|", "")
                                                    store(varB)
                                                    set(varB)
                                if not found : 
                                    search in : taken
                                    search text : "◇より同種工事とは"
                                    if found : 
                                        take left : 
                                            search in : taken
                                            search text : "同種工事:"
                                            if found : 
                                                take right : 
                                                    remove whitespaces
                                                    replace("の施工実績。", "")
                                                    replace("の施工実績", "")
                                                    replace("を有すること。", "")
                                                    replace("を有すること", "")
                                                    replace("であること。", "")
                                                    replace("|", "")
                                                    store(varC)
                                                    set(varC)
                                            if not found : 
                                                remove whitespaces
                                                replace("の施工実績。", "")
                                                replace("の施工実績", "")
                                                replace("を有すること。", "")
                                                replace("であること。", "")
                                                replace("|", "")
                                                store(varD)
                                                set(varD)
    if false : 
        search in : region_B
        search text : "2)評価基準及び得点配分"
        if found :
            take right : 
                search in : taken
                search text : "企業の能力等(加算点1)"
                if found : 
                    take right : 
                        search in : taken
                        search text : "◇同種工事とは4.(4)に明示しているとおりである。"
                        if found : 
                            take right : 
                                search in : taken
                                search text : "◇同種工事とは4.(4)に明示しているとおりである。"
                                if found : 
                                    take right : 
                                        search in : taken
                                        search text : "◇より同種工事とは"
                                        if found : 
                                            take left : 
                                                search in : taken
                                                search text : "同種工事:"
                                                if found : 
                                                    take right : 
                                                        remove whitespaces
                                                        replace("の施工実績。", "")
                                                        replace("の施工実績", "")
                                                        replace("を有すること。", "")
                                                        replace("を有すること", "")
                                                        replace("であること。", "")
                                                        replace("|", "")
                                                        store(varA)
                                                        set(varA)
                                                if not found : 
                                                    remove whitespaces
                                                    replace("の施工実績。", "")
                                                    replace("の施工実績", "")
                                                    replace("を有すること。", "")
                                                    replace("であること。", "")
                                                    replace("を有すること", "")
                                                    replace("|", "")
                                                    store(varB)
                                                    set(varB)
                                if not found : 
                                    search in : taken
                                    search text : "◇より同種工事とは"
                                    if found : 
                                        take left : 
                                            search in : taken
                                            search text : "同種工事:"
                                            if found : 
                                                take right : 
                                                    remove whitespaces
                                                    replace("の施工実績。", "")
                                                    replace("の施工実績", "")
                                                    replace("を有すること。", "")
                                                    replace("を有すること", "")
                                                    replace("であること。", "")
                                                    replace("|", "")
                                                    store(varC)
                                                    set(varC)
                                            if not found : 
                                                remove whitespaces
                                                replace("の施工実績。", "")
                                                replace("の施工実績", "")
                                                replace("を有すること。", "")
                                                replace("であること。", "")
                                                replace("|", "")
                                                store(varD)
                                                set(varD)



「より同種性の高い(企業)」:
    check : name_of
    has value : 本官
    if true : 
        search in : region_B
        search text : "2)評価基準及び得点配分"
        if found :
            take right : 
                search in : taken
                search text : "企業の能力等(加算点1)"
                if found : 
                    take right : 
                        search in : taken
                        search text : "◇同種工事とは4.(4)に明示しているとおりである。"
                        if found : 
                            take right : 
                                search in : taken
                                search text : "「より同種性の高い工事」"
                                if found : 
                                    take right : 
                                        search in : taken
                                        search text : "次のとおりとする。"
                                        if found : 
                                            take right : 
                                                search in : taken
                                                search text : "◇施工実績"
                                                if found : 
                                                    take left : 
                                                        search in : taken
                                                        search text : "より同種工事:"
                                                        if found : 
                                                            take right : 
                                                                remove whitespaces
                                                                replace("の施工実績。", "")
                                                                replace("の施工実績", "")
                                                                replace("を有すること。", "")
                                                                replace("であること。", "")
                                                                replace("同種工事の要件に加え、", "")
                                                                replace("|", "")
                                                                store(varA1)
                                                                set(varA1)
                                                        if not found : 
                                                            remove whitespaces
                                                            replace("の施工実績。", "")
                                                            replace("の施工実績", "")
                                                            replace("を有すること。", "")
                                                            replace("であること。", "")
                                                            replace("同種工事の要件に加え、", "")
                                                            replace("|", "")
                                                            store(varA2)
                                                            set(varA2)
    if false : 
        search in : region_B
        search text : "2)評価基準及び得点配分"
        if found :
            take right : 
                search in : taken
                search text : "企業の能力等(加算点1)"
                if found : 
                    take right : 
                        search in : taken
                        search text : "◇同種工事とは4.(4)に明示しているとおりである。"
                        if found : 
                            take right : 
                                search in : taken
                                search text : "「より同種性の高い工事」"
                                if found : 
                                    take right : 
                                        search in : taken
                                        search text : "次のとおりとする。"
                                        if found : 
                                            take right : 
                                                search in : taken
                                                search text : "◇施工実績"
                                                if found : 
                                                    take left : 
                                                        search in : taken
                                                        search text : "より同種工事:"
                                                        if found : 
                                                            take right : 
                                                                remove whitespaces
                                                                replace("の施工実績。", "")
                                                                replace("の施工実績", "")
                                                                replace("を有すること。", "")
                                                                replace("であること。", "")
                                                                replace("同種工事の要件に加え、", "")
                                                                replace("|", "")
                                                                store(varA1)
                                                                set(varA1)
                                                        if not found : 
                                                            remove whitespaces
                                                            replace("の施工実績。", "")
                                                            replace("の施工実績", "")
                                                            replace("を有すること。", "")
                                                            replace("であること。", "")
                                                            replace("同種工事の要件に加え、", "")
                                                            replace("|", "")
                                                            store(varA2)
                                                            set(varA2)

「より同種性の高い(技術者) doushu_en01」:
    check : name_of
    has value : 本官
    if true : 
        search in : region_B
        search text : "2)評価基準及び得点配分"
        if found :
            take right : 
                search in : taken
                search text : "企業の能力等(加算点1)"
                if found : 
                    take right : 
                        search in : taken
                        search text : "②配置予定技術者の能力等(加算点2)"
                        if found : 
                            take right : 
                                search in : taken
                                search text : "◇同種及びより同種、配置予定技術者に関する発注機関別の考え方は、施工実績に準ずる。"
                                if found : 
                                    set(「より同種性の高い(企業)」)
                                if not found : 
                                    search in : taken
                                    search text : "上記4.(4)に掲げる同種工事の要件を満たす工事現場に従事"
                                    if found : 
                                        set(「より同種性の高い(企業)」)
    if false : 
        search in : region_B
        search text : "2)評価基準及び得点配分"
        if found :
            take right : 
                search in : taken
                search text : "企業の能力等(加算点1)"
                if found : 
                    take right : 
                        search in : taken
                        search text : "②配置予定技術者の能力等(加算点2)"
                        if found : 
                            take right : 
                                search in : taken
                                search text : "上記4.(4)に掲げる同種工事の要件を満たす工事現場に従事"
                                if found : 
                                    set(「より同種性の高い(企業)」)
                                if not found : 
                                    search in : taken
                                    search text : "◇同種及びより同種、配置予定技術者に関する発注機関別の考え方は、施工実績に準ずる。"
                                    if found : 
                                        set(「より同種性の高い(企業)」)


「同種工事（技術者） doushu_en02」: 
    check : name_of
    has value : 本官
    if true : 
        search in : region_B
        search text : "2)評価基準及び得点配分"
        if found :
            take right : 
                search in : taken
                search text : "企業の能力等(加算点1)"
                if found : 
                    take right : 
                        search in : taken
                        search text : "②配置予定技術者の能力等(加算点2)"
                        if found : 
                            take right : 
                                search in : taken
                                search text : "◇同種及びより同種、配置予定技術者に関する発注機関別の考え方は、施工実績に準ずる。"
                                if found : 
                                    set(「同種工事(企業)」_doushu_co2)
                                if not found : 
                                    search in : taken
                                    search text : "上記4.(4)に掲げる同種工事の要件を満たす工事現場に従事"
                                    if found : 
                                        set(「同種工事(企業)」_doushu_co2)
    if false : 
        search in : region_B
        search text : "2)評価基準及び得点配分"
        if found :
            take right : 
                search in : taken
                search text : "企業の能力等(加算点1)"
                if found : 
                    take right : 
                        search in : taken
                        search text : "②配置予定技術者の能力等(加算点2)"
                        if found : 
                            take right : 
                                search in : taken
                                search text : "上記4.(4)に掲げる同種工事の要件を満たす工事現場に従事"
                                if found : 
                                    set(「同種工事(企業)」_doushu_co2)
                                if not found : 
                                    search in : taken
                                    search text : "◇同種及びより同種、配置予定技術者に関する発注機関別の考え方は、施工実績に準ずる。"
                                    if found : 
                                        set(「同種工事(企業)」_doushu_co2)
                                        