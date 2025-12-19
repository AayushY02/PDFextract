block_qual :
    search in : all
    search text : ("競争参加資格", "入札参加資格", "参加資格")
    if found :
        take right :
            search in : taken
            search text : ("総合評価", "提出書類", "入札手続", "入札手続等", "手続等", "６．", "6．") 
            if found :
                take left :
                    store(var_block_qual)
                    set(var_block_qual)
    if not found :
        set(all)

block_company :
    check : var_block_qual
    has value : ""
    if false :
        search in : var_block_qual
        search text : ("配置予定技術者", "配置予定の技術者", "主任技術者", "監理技術者")
        if found :
            take left :
                store(var_block_company)
                set(var_block_company)
        if not found :
            store(var_block_company)
            set(var_block_company)

block_engineer :
    check : var_block_qual
    has value : ""
    if false :
        search in : var_block_qual
        search text : ("配置予定技術者", "配置予定の技術者", "主任技術者", "監理技術者", "施工経験") 
        if found :
            take right :
                search in : taken
                search text : ("総合評価", "提出書類", "入札手続", "手続等", "６．", "6．")
                if found :
                    take left :
                        store(var_block_engineer)
                        set(var_block_engineer)
        if not found :
            set(all)


「同種工事（企業）」:
    search in : var_block_company
    search text : ("同種工事：", "同種工事:", "同種工事 :", "同種工事: ", "同種工事として、", "同種工事として", "同種工事（企業）")
    if found :
        take right :
            search in : taken
            search text : ("また、同種工事のうち", "また同種工事のうち", "また、同種工事における", "また、同種工事において", "また、同種工事に関する", "また、同種工事に係る", "また、同種工事は", "また、同種工事における", "また、同種工事における")
            if found :
                take left :
                    remove whitespaces
                    store(var_same_co)
                    set(var_same_co)
        
            search in : taken
            search text : ("同種工事のうち", "なお、同種工事のうち", "なお同種工事のうち", "経常建設共同企業体", "共同企業体", "配置予定技術者", "配置予定の技術者", "主任技術者", "監理技術者", "\n")
            if found :
                take left :
                    remove whitespaces
                    store(var_same_co)
                    set(var_same_co)
 
            search in : taken
            search text : ("ただし", "※", "注", "。", "\n", "（", "【")
            if found :
                take left :
                    remove whitespaces
                    store(var_same_co)
                    set(var_same_co)
    if not found :
        set("該当なし")

「同種工事（技術者）」:
    search in : var_block_engineer
    search text : ("同種工事：", "同種工事:", "同種工事 :", "同種工事: ", "同種工事として、", "同種工事として", "同種工事（技術者）")
    if found :
        take right :
            search in : taken
            search text : ("また、同種工事のうち", "また同種工事のうち", "また、同種工事における", "また、同種工事において", "また、同種工事に関する", "また、同種工事に係る", "また、同種工事は", "また、同種工事における", "また、同種工事における")
            if found :
                take left :
                    remove whitespaces
                    store(var_same_eng)
                    set(var_same_eng)
            
                search in : taken
                search text : ("同種工事のうち", "なお、同種工事のうち", "なお同種工事のうち", "経常建設共同企業体", "共同企業体", "配置予定技術者", "配置予定の技術者", "主任技術者", "監理技術者", "\n")
                if found :
                    take left :
                        remove whitespaces
                        store(var_same_eng)
                        set(var_same_eng)

                search in : taken
                search text : ("ただし", "※", "注", "。", "\n", "（", "【")
                if found :
                    take left :
                        remove whitespaces
                        store(var_same_eng)
                        set(var_same_eng)
    if not found :
        set("該当なし")


「より同種性が高い工事（企業）」 :
    search in : all
    search text : ("より同種性が高い工事：", "より同種性が高い工事 :", "を「より同種性が高い」と評価", "を『より同種性が高い』と評価")
    if found :
        search in : all
        search text : ("より同種性が高い工事：", "より同種性が高い工事 :")
        if found :
            take right :
                search in : taken
                search text : ("高い同種性", "同種性が認められる", "※", "注", "。", "\n")
                if found :
                take left :
                    remove whitespaces
                    store(var_co_very_high)
                    set(var_co_very_high)
                    
        search in : all
        search text : ("を「より同種性が高い」と評価", "を『より同種性が高い』と評価")
        if found :
            take left :
                search in : taken
                search text : ("また、同種工事のうち", "同種工事のうち", "なお、同種工事のうち", "\n")
                if found :
                    take right :
                        search in : taken
                        search text : ("を「より同種性が高い」と評価", "を『より同種性が高い』と評価")
                        if found :
                            take left :
                                remove whitespaces
                                store(var_co_very_high)
                                set(var_co_very_high)
    if not found :
        set("該当なし")

「高い同種性が認められる工事（企業）」 :
    search in : all
    search text : ("高い同種性が認められる工事：", "高い同種性が認められる工事 :", "を「高い同種性が認められる」と評価", "を『高い同種性が認められる』と評価")
    if found :
        take right :
            search in : taken
            search text : ("同種性が認められる", "※", "注", "。", "\n")
            if found :
                take left :
                    remove whitespaces
                    store(var_co_high)
                    set(var_co_high)
    if not found :
        set("該当なし")

「同種性が認められる工事（企業）」 :
    search in : all
    search text : ("同種性が認められる工事：", "同種性が認められる工事 :", "を「同種性が認められる」と評価", "を『同種性が認められる』と評価")
    if found :
        take right :
            search in : taken
            search text : ("※", "注", "。", "\n")
            if found :
                take left :
                    remove whitespaces
                    store(var_co)
                    set(var_co)
    if not found :
        set("該当なし")

「より同種性が高い工事（技術者）」 :
    search in : all
    search text : ("より同種性が高い工事（技術者）：", "より同種性が高い工事（技術者） :", "を「より同種性が高い」と評価", "を『より同種性が高い』と評価")
    if found :
        take right :
            search in : taken
            search text : ("高い同種性", "同種性が認められる", "※", "注", "。", "\n")
            if found :
                take left :
                    remove whitespaces
                    store(var_eng_very_high)
                    set(var_eng_very_high)
    if not found :
        set("該当なし")

「高い同種性が認められる工事（技術者）」 :
    search in : all
    search text : ("高い同種性が認められる工事（技術者）：", "高い同種性が認められる工事（技術者） :", "高い同種性が認められる工事：", "高い同種性が認められる工事 :")
    if found :
        take right :
            search in : taken
            search text : ("同種性が認められる", "※", "注", "。", "\n")
            if found :
                take left :
                    remove whitespaces
                    store(var_eng_high)
                    set(var_eng_high)
    if not found :
        set("該当なし")

「同種性が認められる工事（技術者）」 :
    search in : all
    search text : ("同種性が認められる工事（技術者）：", "同種性が認められる工事（技術者） :", "同種性が認められる工事：", "同種性が認められる工事 :")
    if found :
        take right :
            search in : taken
            search text : ["※", "注", "。", "\n"]
            if found :
                take left :
                    remove whitespaces
                    store(var_eng)
                    set(var_eng)
    if not found :
        set("該当なし")

「より同種性が高い工事（補足）」 :
    search in : all
    search text : ("また、同種工事", "また同種工事")
    if found :
        take right :
            search in : taken
            search text : ("を「より同種性が高い」と評価", "を『より同種性が高い』と評価", "を「高い同種性が認められる」と評価", "を『高い同種性が認められる』と評価", "を「同種性が認められる」と評価", "を『同種性が認められる』と評価")
            if found :
                take left :
                    remove whitespaces
                    store(var_note)
                    set(var_note)
            if not found :
                search in : all
                search text : ("より同種性が高い")
                if found :
                    take right :
                        search in : taken
                        search text : ("。", "\n")
                        if found :
                            take left :
                                remove whitespaces
                                store(var_note)
                                set(var_note)
    if not found :
        set("該当なし")