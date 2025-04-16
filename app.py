import streamlit as st
import requests
import json
import time

# 初始化帳號清單
if "user_ids" not in st.session_state:
    st.session_state.user_ids = [
        "同舟共雞", "火烤雞翅膀", "MuyanOuO",
        "法式馬丁尼", "如果爐是一種天賦", "Danphen",
        "超胖玨餅", "巴薩", "奧喵叫我來玩的", "靜小稀",
        "FeiFeiyaaa", "寸丹丹", "奧喵喵喵", "舟舟三世"
    ]

st.set_page_config(page_title="BrownDust2 優惠券兌換工具", page_icon="🎁")
st.title("🎁 BrownDust2 優惠券批次兌換工具")

# ---------------------------
# 顯示帳號清單（精簡模式）
# ---------------------------
st.subheader("📋 目前帳號清單")
st.markdown("、".join(st.session_state.user_ids))

# ---------------------------
# 帳號管理（展開編輯區）
# ---------------------------
with st.expander("🔧 管理帳號（點擊展開）"):
    st.markdown("每行一個帳號名稱，儲存後會自動更新")
    new_list = st.text_area("帳號清單", "\n".join(st.session_state.user_ids), height=200)
    if st.button("💾 儲存帳號清單"):
        updated = [line.strip() for line in new_list.splitlines() if line.strip()]
        st.session_state.user_ids = updated
        st.success("✅ 帳號清單已更新！")
        st.experimental_rerun()

# ---------------------------
# 兌換碼輸入與執行
# ---------------------------
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