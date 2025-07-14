import streamlit as st
import re
import dns.resolver
import smtplib
import socket

st.title("📧 メールアドレス有効性チェックアプリ")

email = st.text_input("メールアドレスを入力してください")

def is_valid_format(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def has_mx_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return True
    except:
        return False

def verify_smtp(email):
    try:
        domain = email.split('@')[1]
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(mx_records[0].exchange)

        server = smtplib.SMTP(timeout=10)
        server.set_debuglevel(0)
        server.connect(mx_record)
        server.helo()
        server.mail('test@example.com')  # 任意の差出人アドレス
        code, message = server.rcpt(email)
        server.quit()

        return code == 250
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, socket.timeout, smtplib.SMTPConnectError):
        return False

if st.button("チェック"):
    if not email:
        st.warning("メールアドレスを入力してください。")
    elif not is_valid_format(email):
        st.error("❌ メールアドレスの形式が正しくありません。")
    else:
        st.success("✅ 形式チェック：OK")
        domain = email.split('@')[1]
        if has_mx_record(domain):
            st.success(f"✅ ドメインチェック：'{domain}' にMXレコードがあります。")
            st.info("SMTPサーバーへの問い合わせ中...")
            result = verify_smtp(email)
            if result:
                st.success("✅ SMTPチェック：メールアドレスは有効の可能性があります。")
            else:
                st.warning("⚠️ SMTPチェック：正確な確認ができませんでした（無効 or ブロック）")
        else:
            st.error("❌ ドメインにMXレコードが見つかりません。メールを受信できません。")

