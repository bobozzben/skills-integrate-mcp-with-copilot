from flask import Flask, render_template, redirect, url_for
from google.oauth2 import id_token
from google.auth.exceptions import InvalidTokenError, CredentialsEmptyError
import requests

class User:
    """用戶模型"""
    def __init__(self, user_id):
        self.id = str(user_id)
        
    def is_authenticated(self):
        return True
        
    def is_active(self):
        return True
        
    def is_anonymous(self):
        return False
    
def load_user(user_id):
    if not user_id:
        return None
    try:
        user_data = get_user_from_database(user_id)  # 假設有這個函數
        return User(user_data['id'])
    except Exception as e:
        app.logger.error(f"Error loading user {user_id}: {e}")
        return None

@app.route('/auth/google/callback')
def auth_callback():
    """Google 認證回調處理"""
    try:
        code = request.form.get('code', '')
        
        if not code:
            raise ValueError("Authorization code is missing")
            
        # 驗證令牌
        payload = id_token.verify_oauth2_token(
            code,
            'YOUR_CLIENT_ID'  # 替換為您的實際 Client ID
        )
        
        user_id = str(payload['sub'])
        
        if not user_id or 'email' not in payload:
            raise ValueError("Invalid Google ID token")
            
        return redirect(url_for('dashboard', user_id=user_id))
        
    except InvalidTokenError as e:
        return f"Authentication failed: {str(e)}", 401
        
    except Exception as e:
        app.logger.error(f"Auth callback error: {e}")
        return "Server error during authentication", 500

# 其他路由和功能保持不變...

if __name__ == "__main__":
    sys.path.append(os.path.dirname(__file__))
    os.environ['OAUTH_CLIENT_ID'] = 'your_client_id_here'
    
    # 啟動伺服器
    app.run(debug=True)