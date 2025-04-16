import streamlit as st
import requests
import json
import time

# 初始化使用者清單（session_state 中）
if "user_ids" not in st.session_state:
    st.session_state.user_ids = \
        [
            "同舟共雞", "火烤雞翅膀", "MuyanOuO",
            "法式馬丁尼", "如果爐是一種天賦", "Danphen",
            "超胖玨餅", "巴薩", "奧喵叫我來玩的", "靜小稀",
            "FeiFeiyaaa", "寸丹丹", "奧喵喵喵", "舟舟三世"
        ]

st.set_page_config(page_title="BrownDust2 優惠券兌換工具", page_icon="🎁")
st.title("🎁 BrownDust2 優惠券批次兌換工具")

# ----------------------
# 使用者帳號列表區塊
# ----------------------
st.subheader("目前帳號清單")
edited_users = []

# 顯示清單，並允許編輯或刪除
for idx, user in enumerate(st.session_state.user_ids):
    col1, col2, col3 = st.columns([5, 1, 1])

    with col1:
        new_value = st.text_input(f"帳號 {idx + 1}", user, key=f"user_{idx}")
        edited_users.append(new_value)

    with col2:
        if st.button("🗑️", key=f"delete_{idx}"):
            confirm = st.checkbox(f"確認刪除帳號「{user}」", key=f"confirm_{idx}")
            if confirm:
                st.session_state.user_ids.pop(idx)
                st.experimental_rerun()

# 更新使用者清單（僅更新文字）
st.session_state.user_ids = edited_users

# ----------------------
# 新增帳號功能
# ----------------------
with st.form("add_user_form"):
    new_user = st.text_input("新增帳號名稱", "")
    submitted = st.form_submit_button("➕ 加入帳號")
    if submitted and new_user.strip():
        st.session_state.user_ids.append(new_user.strip())
        st.experimental_rerun()

# ----------------------
# 輸入兌換碼並執行批次兌換
# ----------------------
st.subheader("輸入優惠券代碼")
code = st.text_input("請輸入兌換碼")

if st.button("🚀 開始兌換") and code.strip():
    with st.spinner("執行中..."):
        for user_id in st.session_state.user_ids:
            payload = {
                "appId": "bd2-live",
                "userId": user_id,
                "code": code.strip()
            }

            st.markdown(f"➡️ 正在處理 `{user_id}` ...")
            try:
                response = requests.post(
                    "https://loj2urwaua.execute-api.ap-northeast-1.amazonaws.com/prod/coupon",
                    headers={
                        "Content-Type": "application/json",
                        "Origin": "https://redeem.bd2.pmang.cloud",
                        "Referer": "https://redeem.bd2.pmang.cloud/",
                        "User-Agent": "Mozilla/5.0"
                    },
                    data=json.dumps(payload)
                )
                data = response.json()
                if response.status_code == 200:
                    st.success(f"✅ {user_id} 回應成功")
                    st.json(data)
                else:
                    st.warning(f"⚠️ {user_id} 失敗，狀態碼: {response.status_code}")
            except Exception as e:
                st.error(f"❌ {user_id} 發生錯誤: {e}")
            time.sleep(1)
