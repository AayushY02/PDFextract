# ============================================================
# 85_script_chubu_only_strong.dsl（中部地整PDF：取りこぼし最小化版）
# ============================================================
#
# ねらい：
# - Sがアップした「85（中部）」PDF群で、同種工事まわり（企業・技術者・同種性ランク）を
#   “取りこぼさない”方向に寄せる。
#
# 方針（取りこぼし対策）：
# 1) 入口（開始マーカー）を増やす
#    - "同種工事：" / "同種工事 :" / "同種工事として" / "同種工事（企業）" など
# 2) 出口（終了マーカー）を増やす（優先順）
#    - "また、同種工事のうち" がある時はそこで切る（最も安定）
#    - ない時は "同種工事のうち" / "なお、同種工事のうち" / "ただし" / "※" / "注" / "。" / 改行
# 3) ブロック分割で誤爆を減らす
#    - 企業ブロック：競争参加資格〜（配置予定技術者の直前）
#    - 技術者ブロック：配置予定技術者〜（総合評価 or 提出書類の直前）
#
# 抽出対象（9項目）
#  1) 同種工事（企業）
#  2) 同種工事（技術者）
#  3) より同種性が高い工事（企業）
#  4) 高い同種性が認められる工事（企業）
#  5) 同種性が認められる工事（企業）
#  6) より同種性が高い工事（技術者）
#  7) 高い同種性が認められる工事（技術者）
#  8) 同種性が認められる工事（技術者）
#  9) より同種性が高い工事（補足）
#
# ★編集ポイントの使い方：
# - 見つからない（該当なしが多い） → search text の候補語を増やす
# - 長すぎる（余計な文まで入る） → 終了マーカーを追加（より早く切る）
# - 短すぎる → 終了マーカーから早すぎるものを外す
# ============================================================

# ------------------------------------------------------------
# 0) 章・ブロック切り（取りこぼしより誤爆減を優先）
# ------------------------------------------------------------

# 0-1) 競争参加資格ブロック（見つかった位置から右へ → 次の大見出し手前で閉じる）
block_qual :
  search in : all
  search text : ["競争参加資格", "入札参加資格", "参加資格"]  # ★編集ポイント
  if found :
    take right :
      # 章終端候補（ここが見つかれば、その手前で閉じる）
      search in : taken
      search text : ["総合評価", "提出書類", "入札手続", "入札手続等", "手続等", "６．", "6．"]  # ★編集ポイント
      if found :
        take left :
          store(var_block_qual)
          set(var_block_qual)
  if not found :
    # 章切りに失敗しても動くよう、全文を保険にする
    set(all)

# 0-2) 企業ブロック：競争参加資格〜配置予定技術者の直前
block_company :
  check : var_block_qual
  has value : ""
  if false :
    search in : var_block_qual
    search text : ["配置予定技術者", "配置予定の技術者", "主任技術者", "監理技術者"]  # ★編集ポイント
    if found :
      take left :
        store(var_block_company)
        set(var_block_company)
  if not found :
    # 「配置予定技術者」が無い形式への保険：資格章全体を企業ブロックとして扱う
    store(var_block_company)
    set(var_block_company)

# 0-3) 技術者ブロック：配置予定技術者〜総合評価/提出書類の直前
block_engineer :
  check : var_block_qual
  has value : ""
  if false :
    search in : var_block_qual
    search text : ["配置予定技術者", "配置予定の技術者", "主任技術者", "監理技術者", "施工経験"]  # ★編集ポイント
    if found :
      take right :
        search in : taken
        search text : ["総合評価", "提出書類", "入札手続", "手続等", "６．", "6．"]  # ★編集ポイント
        if found :
          take left :
            store(var_block_engineer)
            set(var_block_engineer)
  if not found :
    # 見つからない場合は全文で探索（取りこぼし回避）
    set(all)

# ------------------------------------------------------------
# 1) “同種工事：〜（終端）” を抜く（企業・技術者）
# ------------------------------------------------------------

# --- [抽出] 同種工事（企業）
「同種工事（企業）」 :
  search in : var_block_company
  search text : ["同種工事：", "同種工事:", "同種工事 :", "同種工事: ", "同種工事として、", "同種工事として", "同種工事（企業）"]  # ★編集ポイント
  if found :
    take right :
      # 終端①：最優先（典型）
      search in : taken
      search text : ["また、同種工事のうち", "また同種工事のうち", "また、同種工事における", "また、同種工事において", "また、同種工事に関する", "また、同種工事に係る", "また、同種工事は", "また、同種工事における", "また、同種工事における"]  # ★編集ポイント
      if found :
        take left :
          remove whitespaces
          store(var_same_co)
          set(var_same_co)

      # 終端②：次点（「また、」が無い）
      search in : taken
      search text : ["同種工事のうち", "なお、同種工事のうち", "なお同種工事のうち", "経常建設共同企業体", "共同企業体", "配置予定技術者", "配置予定の技術者", "主任技術者", "監理技術者", "\n"]  # ★編集ポイント
      if found :
        take left :
          remove whitespaces
          store(var_same_co)
          set(var_same_co)

      # 終端③：最後の保険（文末・注記）
      search in : taken
      search text : ["ただし", "※", "注", "。", "\n", "（", "【"]  # ★編集ポイント：早すぎるなら削る
      if found :
        take left :
          remove whitespaces
          store(var_same_co)
          set(var_same_co)
  if not found :
    set("該当なし")

# --- [抽出] 同種工事（技術者）
「同種工事（技術者）」 :
  search in : var_block_engineer
  search text : ["同種工事：", "同種工事:", "同種工事 :", "同種工事: ", "同種工事として、", "同種工事として", "同種工事（技術者）"]  # ★編集ポイント
  if found :
    take right :
      # 終端①：最優先
      search in : taken
      search text : ["また、同種工事のうち", "また同種工事のうち", "また、同種工事における", "また、同種工事において", "また、同種工事に関する", "また、同種工事に係る", "また、同種工事は", "また、同種工事における", "また、同種工事における"]  # ★編集ポイント
      if found :
        take left :
          remove whitespaces
          store(var_same_eng)
          set(var_same_eng)

      # 終端②：次点
      search in : taken
      search text : ["同種工事のうち", "なお、同種工事のうち", "なお同種工事のうち", "経常建設共同企業体", "共同企業体", "配置予定技術者", "配置予定の技術者", "主任技術者", "監理技術者", "\n"]  # ★編集ポイント
      if found :
        take left :
          remove whitespaces
          store(var_same_eng)
          set(var_same_eng)

      # 終端③：最後の保険
      search in : taken
      search text : ["ただし", "※", "注", "。", "\n", "（", "【"]  # ★編集ポイント
      if found :
        take left :
          remove whitespaces
          store(var_same_eng)
          set(var_same_eng)
  if not found :
    set("該当なし")

# ------------------------------------------------------------
# 2) 同種性ランク（企業・技術者）
# ------------------------------------------------------------

「より同種性が高い工事（企業）」 :
  search in : all
  search text : ["より同種性が高い工事：", "より同種性が高い工事 :", "を「より同種性が高い」と評価", "を『より同種性が高い』と評価"]  # ★編集ポイント
  if found :
    search in : all
    search text : ["より同種性が高い工事：", "より同種性が高い工事 :"]
    if found :
      take right :
        search in : taken
        search text : ["高い同種性", "同種性が認められる", "※", "注", "。", "\n"]
        if found :
          take left :
            remove whitespaces
            store(var_co_very_high)
            set(var_co_very_high)
    search in : all
    search text : ["を「より同種性が高い」と評価", "を『より同種性が高い』と評価"]
    if found :
      take left :
        search in : taken
        search text : ["また、同種工事のうち", "同種工事のうち", "なお、同種工事のうち", "\n"]
        if found :
          take right :
            search in : taken
            search text : ["を「より同種性が高い」と評価", "を『より同種性が高い』と評価"]
            if found :
              take left :
                remove whitespaces
                store(var_co_very_high)
                set(var_co_very_high)
  if not found :
    set("該当なし")

「高い同種性が認められる工事（企業）」 :
  search in : all
  search text : ["高い同種性が認められる工事：", "高い同種性が認められる工事 :", "を「高い同種性が認められる」と評価", "を『高い同種性が認められる』と評価"]  # ★編集ポイント
  if found :
    take right :
      search in : taken
      search text : ["同種性が認められる", "※", "注", "。", "\n"]
      if found :
        take left :
          remove whitespaces
          store(var_co_high)
          set(var_co_high)
  if not found :
    set("該当なし")

「同種性が認められる工事（企業）」 :
  search in : all
  search text : ["同種性が認められる工事：", "同種性が認められる工事 :", "を「同種性が認められる」と評価", "を『同種性が認められる』と評価"]  # ★編集ポイント
  if found :
    take right :
      search in : taken
      search text : ["※", "注", "。", "\n"]
      if found :
        take left :
          remove whitespaces
          store(var_co)
          set(var_co)
  if not found :
    set("該当なし")

「より同種性が高い工事（技術者）」 :
  search in : all
  search text : ["より同種性が高い工事（技術者）：", "より同種性が高い工事（技術者） :", "を「より同種性が高い」と評価", "を『より同種性が高い』と評価"]  # ★編集ポイント
  if found :
    take right :
      search in : taken
      search text : ["高い同種性", "同種性が認められる", "※", "注", "。", "\n"]
      if found :
        take left :
          remove whitespaces
          store(var_eng_very_high)
          set(var_eng_very_high)
  if not found :
    set("該当なし")

「高い同種性が認められる工事（技術者）」 :
  search in : all
  search text : ["高い同種性が認められる工事（技術者）：", "高い同種性が認められる工事（技術者） :", "高い同種性が認められる工事：", "高い同種性が認められる工事 :"]  # ★編集ポイント
  if found :
    take right :
      search in : taken
      search text : ["同種性が認められる", "※", "注", "。", "\n"]
      if found :
        take left :
          remove whitespaces
          store(var_eng_high)
          set(var_eng_high)
  if not found :
    set("該当なし")

「同種性が認められる工事（技術者）」 :
  search in : all
  search text : ["同種性が認められる工事（技術者）：", "同種性が認められる工事（技術者） :", "同種性が認められる工事：", "同種性が認められる工事 :"]  # ★編集ポイント
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

# ------------------------------------------------------------
# 3) 補足（注記・脚注）
# ------------------------------------------------------------

「より同種性が高い工事（補足）」 :
  # 典型：同種工事の直後に
  # 「また、同種工事における○○の施工実績を『より同種性が高い』と評価する。」
  # のように“評価対象(○○)”が続くケースを想定。
  search in : all
  search text : ["また、同種工事", "また同種工事"]  # ★編集ポイント（表記ゆれ保険）
  if found :
    take right :
      # 終端：評価フレーズの直前で止める
      search in : taken
      search text : ["を「より同種性が高い」と評価", "を『より同種性が高い』と評価", "を「高い同種性が認められる」と評価", "を『高い同種性が認められる』と評価", "を「同種性が認められる」と評価", "を『同種性が認められる』と評価"]  # ★編集ポイント
      if found :
        take left :
          remove whitespaces
          store(var_note)
          set(var_note)
  if not found :
    # 保険：文中の「より同種性が高い」以降の注記を拾う（精度は落ちるが取りこぼし回避）
    search in : all
    search text : ["より同種性が高い"]  # ★編集ポイント
    if found :
      take right :
        search in : taken
        search text : ["。", "\n"]
        if found :
          take left :
            remove whitespaces
            store(var_note)
            set(var_note)
  if not found :
    set("該当なし")
