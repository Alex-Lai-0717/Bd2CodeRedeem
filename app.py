import streamlit as st
import requests
import json
import time
import base64

REMOTE_USER_LIST_URL = "https://raw.githubusercontent.com/Alex-Lai-0717/Bd2CodeRedeem/main/user_ids.json"

# 初始化狀態
if "last_result" not in st.session_state:
    st.session_state.last_result = {
        "success": [],
        "used": [],
        "error": [],
        "log": []
    }

if "user_ids" not in st.session_state:
    try:
        res = requests.get(REMOTE_USER_LIST_URL)
        st.session_state.user_ids = res.json()
    except Exception:
        st.session_state.user_ids = ["帳號載入失敗"]

if "running" not in st.session_state:
    st.session_state.running = False

st.set_page_config(page_title="BrownDust2 優惠券兌換工具", page_icon="🎁")
st.title("🎁 BrownDust2 優惠券兌換工具")

# 顯示帳號清單
st.subheader("📋 目前帳號清單")
cols = st.columns(5)
for i, user in enumerate(st.session_state.user_ids):
    col = cols[i % 5]
    with col:
        col.markdown(
            f"""
            <div style='
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                margin: 6px 0;
                background-color: #f8f9fa;
                color: #333;
                text-align: center;
                min-width: 120px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                font-size: 15px;
                font-weight: 500;
            ' title="{user}">
                {user}
            </div>
            """,
            unsafe_allow_html=True
        )

# 編輯帳號清單功能
def update_user_ids_to_github(user_ids):
    token = st.secrets["github_token"]
    repo = st.secrets["github_repo"]
    file_path = st.secrets["github_file_path"]
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    get_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    res = requests.get(get_url, headers=headers)
    if res.status_code != 200:
        st.error("❌ 無法取得 GitHub 檔案內容，請確認檔案已存在 repo 中")
        return

    sha = res.json().get("sha")
    content = json.dumps(user_ids, ensure_ascii=False, indent=2)
    b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    put_payload = {
        "message": "更新使用者帳號清單",
        "content": b64_content,
        "sha": sha
    }

    put_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    put_res = requests.put(put_url, headers=headers, json=put_payload)

    if put_res.status_code in [200, 201]:
        st.success("✅ 已成功儲存並同步至 GitHub 🎉")
        st.rerun()
    else:
        st.error("❌ 同步 GitHub 失敗")
        st.json(put_res.json())

# 編輯帳號 UI 區塊
with st.expander("🔧 管理帳號（點擊展開）"):
    st.markdown("每行一個帳號名稱，儲存後會自動更新。")
    updated_text = st.text_area("帳號清單", "\n".join(st.session_state.user_ids), height=200)
    if st.button("💾 儲存帳號清單"):
        updated_users = [line.strip() for line in updated_text.splitlines() if line.strip()]
        st.session_state.user_ids = updated_users
        update_user_ids_to_github(updated_users)

# 輸入兌換碼
st.subheader("輸入優惠券代碼")
code = st.text_input("請輸入兌換碼")

# 開始兌換按鈕
if st.button("🚀 開始兌換") and code.strip():
    st.session_state.running = True

# 如果正在執行
if st.session_state.running:
    if st.button("🔴 停止執行"):
        st.session_state.running = False

    st.info("執行中...")

    # 暫存本次執行結果
    success_users = []
    used_users = []
    error_users = []
    execution_log = []

    with st.spinner("正在批次處理帳號..."):
        for user_id in st.session_state.user_ids:
            if not st.session_state.running:
                st.warning("⛔️ 使用者已手動中止執行")
                break

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
                message = data.get("message", "")

                if "이미 사용한 쿠폰입니다" in message:
                    st.warning(f"⚠️ {user_id}：該帳號已使用過此兌換碼")
                    used_users.append(user_id)
                    execution_log.append({"user": user_id, "status": "used", "response": data})

                elif response.status_code == 200:
                    st.success(f"✅ {user_id}：兌換成功")
                    success_users.append(user_id)
                    execution_log.append({"user": user_id, "status": "success", "response": data})

                else:
                    st.error(f"❌ {user_id}：未知錯誤（HTTP {response.status_code}）")
                    error_users.append(user_id)
                    execution_log.append({"user": user_id, "status": "error", "response": data})

            except Exception as e:
                st.error(f"❌ {user_id} 發生錯誤: {e}")
                error_users.append(user_id)
                execution_log.append({"user": user_id, "status": "exception", "response": {"error": str(e)}})

            time.sleep(1)

    st.session_state.running = False
    st.session_state.last_result = {
        "success": success_users,
        "used": used_users,
        "error": error_users,
        "log": execution_log
    }

# 結果摘要
if st.session_state.last_result["log"]:
    st.subheader("📊 執行結果摘要")
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ 成功兌換", len(st.session_state.last_result["success"]))
    col2.metric("⚠️ 已兌換過", len(st.session_state.last_result["used"]))
    col3.metric("❌ 發生錯誤", len(st.session_state.last_result["error"]))

    with st.expander("🔍 詳細處理紀錄"):
        for log in st.session_state.last_result["log"]:
            st.markdown(f"**{log['user']}** - {log['status']}")
            with st.expander("查看 API 回應"):
                st.json(log["response"])