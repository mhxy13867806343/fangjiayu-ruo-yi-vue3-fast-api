from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_password_hash(password):
    return pwd_context.hash(password)

# 生成加密密码
admin_password = get_password_hash('admin')
user_password = get_password_hash('123456')

print(f"Admin密码加密结果: {admin_password}")
print(f"用户密码加密结果: {user_password}")
