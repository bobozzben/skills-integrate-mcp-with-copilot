from flask import Flask, request, redirect, url_for
from google.oauth2 import id_token
from google.auth.exceptions import InvalidTokenError

app = Flask(__name__)

@app.route('/auth/google/callback')
def auth_callback():
    """Google 認證回調處理"""
    try:
        code = request.form.get('code', '')
        
        if not code:
            return "Authorization code is missing", 400
            
        payload = id_token.verify_oauth2_token(
            code,
            'YOUR_CLIENT_ID'  # 替換為您的實際 Client ID
        )
        
        user_id = str(payload['sub'])
        
        if not user_id or 'email' not in payload:
            return "Invalid Google ID token", 401
            
        from flask import session
        
        session['user'] = {
            'id': user_id,
            'email': payload.get('email'),
            'name': payload.get('name', '')
        }
        
        # 在這裡可以添加其他資訊或邏輯
        return redirect(url_for('dashboard'))
        
    except InvalidTokenError as e:
        return f"Invalid token: {str(e)}", 401
        
    except Exception as e:
        from flask import render_template, flash
        current_app.logger.error(f"Auth callback error: {e}")
        flash(str(e))
        return "Server error during authentication"

if __name__ == "__main__":
    app.run(debug=True)

# 請確保您的 redirect URI 與 Google OAuth2 實驗設定相符。