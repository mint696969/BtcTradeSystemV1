# path: ./tmp/clipboard_probe.py
# desc: Streamlit上でClipboard APIが動作するか最小確認（環境切り分け用）

import streamlit as st
import streamlit.components.v1 as components

st.title("Clipboard probe")
snap = st.text_area("copy対象", value="hello from probe", height=80)

# iframe 内のボタンで clipboard.writeText() を試す
components.html(f"""
<!DOCTYPE html>
<html><body>
  <textarea id="t" style="width:100%;height:60px;">{snap}</textarea>
  <button id="btn">Copy (JS)</button>
  <div id="r" style="margin-top:6px;color:#888;">waiting...</div>
  <script>
    const btn = document.getElementById('btn');
    btn.addEventListener('click', async () => {{
      try {{
        const v = document.getElementById('t').value;
        await navigator.clipboard.writeText(v);
        document.getElementById('r').innerText = 'OK: copied ' + v.length + ' chars';
      }} catch (e) {{
        document.getElementById('r').innerText = 'NG: ' + e;
      }}
    }});
  </script>
</body></html>
""", height=180)
st.info("結果が OK ならブラウザ権限は問題なし。NGなら UI 実装ではなく環境/権限起因の可能性。")
