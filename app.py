import streamlit as st
import requests
import json
import time

APP_ID = "bd2-live"
USER_IDS = ["同舟共雞", "ID玩家二", "ID玩家三"]
API_URL = "https://loj2urwaua.execute-api.ap-northeast-1.amazonaws.com/prod/coupon"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://redeem.bd2.pmang.cloud",
    "Referer": "https://redeem.bd2.pmang.cloud/",
    "User-Agent": "Mozilla/5.0"
}

st.set_page_config(page_title="BrownDust2 優惠券兌換工具", page_icon="🎁")

st.title("🎁 BrownDust2 優惠券批次兌換工具")

code = st.text_input("請輸入兌換碼")
if st.button("開始兌換") and code.strip():
    with st.spinner("兌換中，請稍候..."):
        for user_id in USER_IDS:
            payload = {
                "appId": APP_ID,
                "userId": user_id,
                "code": code.strip()
            }

            st.markdown(f"➡️ 正在處理 `{user_id}` ...")
            try:
                response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
                data = response.json()

                if response.status_code == 200:
                    st.success(f"✅ {user_id} 回應成功")
                    st.json(data)
                else:
                    st.warning(f"⚠️ {user_id} 失敗，狀態碼: {response.status_code}")
            except Exception as e:
                st.error(f"❌ {user_id} 發生錯誤: {e}")
            time.sleep(1)
else:
    st.info("請輸入兌換碼並點擊按鈕")