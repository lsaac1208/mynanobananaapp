"""
认证系统测试
"""
import pytest
import json
from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        'email': 'test@example.com',
        'password': 'Test123456'
    }


@pytest.fixture
def registered_user(app, sample_user_data):
    """创建已注册用户"""
    with app.app_context():
        user = User(email=sample_user_data['email'], password=sample_user_data['password'])
        user.credits = 3
        db.session.add(user)
        db.session.commit()
        return user


class TestUserRegistration:
    """用户注册测试"""

    def test_successful_registration(self, client, sample_user_data):
        """测试成功注册"""
        response = client.post('/api/register',
                             data=json.dumps(sample_user_data),
                             content_type='application/json')

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['message'] == '注册成功'
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['email'] == sample_user_data['email']
        assert data['user']['credits'] == 3  # 注册赠送3次

    def test_invalid_email_format(self, client):
        """测试无效邮箱格式"""
        invalid_data = {
            'email': 'invalid-email',
            'password': 'Test123456'
        }

        response = client.post('/api/register',
                             data=json.dumps(invalid_data),
                             content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert '邮箱格式不正确' in data['error']

    def test_weak_password(self, client):
        """测试弱密码"""
        weak_passwords = [
            'short',      # 太短
            '12345678',   # 只有数字
            'abcdefgh',   # 只有字母
            'Test123'     # 少于8位
        ]

        for password in weak_passwords:
            user_data = {
                'email': 'test@example.com',
                'password': password
            }

            response = client.post('/api/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')

            assert response.status_code == 400

    def test_duplicate_email(self, client, registered_user, sample_user_data):
        """测试重复邮箱注册"""
        response = client.post('/api/register',
                             data=json.dumps(sample_user_data),
                             content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert '该邮箱已被注册' in data['error']

    def test_missing_fields(self, client):
        """测试缺少必要字段"""
        test_cases = [
            {},  # 空数据
            {'email': 'test@example.com'},  # 缺少密码
            {'password': 'Test123456'},  # 缺少邮箱
        ]

        for data in test_cases:
            response = client.post('/api/register',
                                 data=json.dumps(data),
                                 content_type='application/json')

            assert response.status_code == 400


class TestUserLogin:
    """用户登录测试"""

    def test_successful_login(self, client, registered_user, sample_user_data):
        """测试成功登录"""
        response = client.post('/api/login',
                             data=json.dumps(sample_user_data),
                             content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['message'] == '登录成功'
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data

    def test_invalid_credentials(self, client, registered_user):
        """测试无效登录凭据"""
        invalid_credentials = [
            {'email': 'wrong@example.com', 'password': 'Test123456'},  # 错误邮箱
            {'email': 'test@example.com', 'password': 'WrongPassword123'},  # 错误密码
            {'email': 'wrong@example.com', 'password': 'WrongPassword123'},  # 都错误
        ]

        for credentials in invalid_credentials:
            response = client.post('/api/login',
                                 data=json.dumps(credentials),
                                 content_type='application/json')

            assert response.status_code == 401
            data = json.loads(response.data)
            assert '邮箱或密码错误' in data['error']

    def test_rate_limiting(self, client, registered_user):
        """测试登录速率限制"""
        wrong_credentials = {
            'email': 'test@example.com',
            'password': 'WrongPassword123'
        }

        # 连续失败登录
        for i in range(6):  # 超过限制(5次)
            response = client.post('/api/login',
                                 data=json.dumps(wrong_credentials),
                                 content_type='application/json')

            if i < 5:
                assert response.status_code == 401
            else:
                assert response.status_code == 429  # 速率限制
                data = json.loads(response.data)
                assert '登录尝试过于频繁' in data['error']

    def test_inactive_user_login(self, client, app, sample_user_data):
        """测试停用用户登录"""
        with app.app_context():
            # 创建停用用户
            user = User(email=sample_user_data['email'], password=sample_user_data['password'])
            user.is_active = False
            db.session.add(user)
            db.session.commit()

        response = client.post('/api/login',
                             data=json.dumps(sample_user_data),
                             content_type='application/json')

        assert response.status_code == 403
        data = json.loads(response.data)
        assert '账号已被停用' in data['error']


class TestTokenOperations:
    """令牌操作测试"""

    def test_token_refresh(self, client, registered_user, sample_user_data):
        """测试令牌刷新"""
        # 先登录获取令牌
        login_response = client.post('/api/login',
                                   data=json.dumps(sample_user_data),
                                   content_type='application/json')

        login_data = json.loads(login_response.data)
        refresh_token = login_data['refresh_token']

        # 刷新令牌
        response = client.post('/api/refresh',
                             headers={'Authorization': f'Bearer {refresh_token}'})

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data

    def test_token_validation(self, client, registered_user, sample_user_data):
        """测试令牌验证"""
        # 先登录获取令牌
        login_response = client.post('/api/login',
                                   data=json.dumps(sample_user_data),
                                   content_type='application/json')

        login_data = json.loads(login_response.data)
        access_token = login_data['access_token']

        # 验证令牌
        response = client.get('/api/check-token',
                            headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == '令牌有效'
        assert 'user' in data

    def test_logout(self, client, registered_user, sample_user_data):
        """测试用户登出"""
        # 先登录
        login_response = client.post('/api/login',
                                   data=json.dumps(sample_user_data),
                                   content_type='application/json')

        login_data = json.loads(login_response.data)
        access_token = login_data['access_token']

        # 登出
        response = client.post('/api/logout',
                             headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == '登出成功'

        # 验证令牌已失效
        check_response = client.get('/api/check-token',
                                  headers={'Authorization': f'Bearer {access_token}'})

        assert check_response.status_code == 401

    def test_invalid_token(self, client):
        """测试无效令牌"""
        invalid_tokens = [
            'Bearer invalid_token',
            'Bearer ',
            'InvalidFormat',
            '',
        ]

        for token in invalid_tokens:
            response = client.get('/api/check-token',
                                headers={'Authorization': token})

            assert response.status_code == 401


class TestUserInfo:
    """用户信息测试"""

    def test_get_current_user(self, client, registered_user, sample_user_data):
        """测试获取当前用户信息"""
        # 先登录
        login_response = client.post('/api/login',
                                   data=json.dumps(sample_user_data),
                                   content_type='application/json')

        login_data = json.loads(login_response.data)
        access_token = login_data['access_token']

        # 获取用户信息
        response = client.get('/api/users/me',
                            headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['email'] == sample_user_data['email']

    def test_get_user_credits(self, client, registered_user, sample_user_data):
        """测试获取用户次数"""
        # 先登录
        login_response = client.post('/api/login',
                                   data=json.dumps(sample_user_data),
                                   content_type='application/json')

        login_data = json.loads(login_response.data)
        access_token = login_data['access_token']

        # 获取用户次数
        response = client.get('/api/users/me/credits',
                            headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'credits' in data
        assert data['credits'] == 3  # 注册时的初始次数


class TestSecurityFeatures:
    """安全特性测试"""

    def test_password_hashing(self, app, sample_user_data):
        """测试密码哈希"""
        with app.app_context():
            user = User(email=sample_user_data['email'], password=sample_user_data['password'])

            # 密码应该被哈希
            assert user.password_hash != sample_user_data['password']

            # 应该能正确验证密码
            assert user.check_password(sample_user_data['password']) is True
            assert user.check_password('wrong_password') is False

    def test_email_normalization(self, client):
        """测试邮箱标准化"""
        user_data = {
            'email': 'Test@EXAMPLE.COM',  # 大写邮箱
            'password': 'Test123456'
        }

        response = client.post('/api/register',
                             data=json.dumps(user_data),
                             content_type='application/json')

        assert response.status_code == 201
        data = json.loads(response.data)
        # 邮箱应该被转换为小写
        assert data['user']['email'] == 'test@example.com'

    def test_sensitive_data_exclusion(self, client, registered_user, sample_user_data):
        """测试敏感数据不会泄露"""
        # 登录获取用户信息
        login_response = client.post('/api/login',
                                   data=json.dumps(sample_user_data),
                                   content_type='application/json')

        login_data = json.loads(login_response.data)
        user_data = login_data['user']

        # 确保密码哈希没有在响应中
        assert 'password' not in user_data
        assert 'password_hash' not in user_data