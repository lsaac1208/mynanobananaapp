"""
AI图片生成功能测试
"""
import pytest
import json
from unittest.mock import patch, AsyncMock
from app import create_app, db
from app.models.user import User
from app.models.creation import Creation


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
def auth_headers(client):
    """创建认证用户并返回认证头"""
    # 创建测试用户
    user_data = {
        'email': 'test@example.com',
        'password': 'Test123456'
    }

    # 注册用户
    response = client.post('/api/register',
                          data=json.dumps(user_data),
                          content_type='application/json')

    assert response.status_code == 201

    # 登录获取token
    response = client.post('/api/login',
                          data=json.dumps(user_data),
                          content_type='application/json')

    assert response.status_code == 200
    data = json.loads(response.data)
    token = data['access_token']

    # 为用户添加生成次数
    with client.application.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        user.credits = 5
        db.session.commit()

    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


class TestGenerateModels:
    """测试获取可用模型接口"""

    def test_get_available_models_success(self, client):
        """测试成功获取可用模型"""
        response = client.get('/api/generate/models')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['success'] is True
        assert 'models' in data
        assert 'sizes' in data
        assert 'nano-banana' in data['models']
        assert '1x1' in data['sizes']


class TestTextToImage:
    """测试文生图功能"""

    @patch('app.services.ai_generator.AIGeneratorService.generate_text_to_image')
    def test_text_to_image_success(self, mock_generate, client, auth_headers):
        """测试文生图成功"""
        # Mock AI服务返回
        mock_generate.return_value = {
            'success': True,
            'images': [
                {'url': 'https://example.com/image1.png'},
                {'url': 'https://example.com/image2.png'}
            ],
            'generation_time': 2.5,
            'model_used': 'nano-banana',
            'prompt': 'test prompt'
        }

        request_data = {
            'prompt': 'a beautiful landscape',
            'model': 'nano-banana',
            'size': '1x1',
            'n': 2
        }

        response = client.post('/api/generate/text-to-image',
                              data=json.dumps(request_data),
                              headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['success'] is True
        assert len(data['images']) == 2
        assert data['generation_time'] == 2.5
        assert data['model_used'] == 'nano-banana'
        assert 'remaining_credits' in data

        # 验证生成记录已保存
        with client.application.app_context():
            creations = Creation.query.all()
            assert len(creations) == 2
            assert creations[0].prompt == 'a beautiful landscape'

    def test_text_to_image_no_auth(self, client):
        """测试未认证用户访问"""
        request_data = {
            'prompt': 'a beautiful landscape'
        }

        response = client.post('/api/generate/text-to-image',
                              data=json.dumps(request_data),
                              content_type='application/json')

        assert response.status_code == 401

    def test_text_to_image_no_credits(self, client, auth_headers):
        """测试用户次数不足"""
        # 清空用户次数
        with client.application.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            user.credits = 0
            db.session.commit()

        request_data = {
            'prompt': 'a beautiful landscape'
        }

        response = client.post('/api/generate/text-to-image',
                              data=json.dumps(request_data),
                              headers=auth_headers)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Insufficient credits' in data['error']

    def test_text_to_image_invalid_prompt(self, client, auth_headers):
        """测试无效提示词"""
        request_data = {
            'prompt': ''  # 空提示词
        }

        response = client.post('/api/generate/text-to-image',
                              data=json.dumps(request_data),
                              headers=auth_headers)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Prompt is required' in data['error']

    @patch('app.services.ai_generator.AIGeneratorService.generate_text_to_image')
    def test_text_to_image_api_failure(self, mock_generate, client, auth_headers):
        """测试AI API调用失败"""
        # Mock AI服务返回失败
        mock_generate.return_value = {
            'success': False,
            'error': 'API key invalid',
            'generation_time': 0.1
        }

        request_data = {
            'prompt': 'a beautiful landscape'
        }

        response = client.post('/api/generate/text-to-image',
                              data=json.dumps(request_data),
                              headers=auth_headers)

        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'API key invalid' in data['error']

        # 验证次数已退还
        with client.application.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            assert user.credits == 5  # 次数应该被退还


class TestImageToImage:
    """测试图生图功能"""

    @patch('app.services.ai_generator.AIGeneratorService.generate_image_to_image')
    def test_image_to_image_success(self, mock_generate, client, auth_headers):
        """测试图生图成功"""
        # Mock AI服务返回
        mock_generate.return_value = {
            'success': True,
            'images': [
                {'url': 'https://example.com/image1.png'}
            ],
            'generation_time': 3.2,
            'model_used': 'nano-banana',
            'prompt': 'edit this image'
        }

        # 创建测试图片数据
        test_image_data = b'fake image data'

        request_data = {
            'prompt': 'make it more colorful',
            'model': 'nano-banana',
            'size': '1x1'
        }

        # 构建multipart请求
        data = {
            'image': (test_image_data, 'test.png', 'image/png'),
            **request_data
        }

        response = client.post('/api/generate/image-to-image',
                              data=data,
                              headers={'Authorization': auth_headers['Authorization']})

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['success'] is True
        assert len(data['images']) == 1
        assert data['generation_time'] == 3.2
        assert 'remaining_credits' in data

    def test_image_to_image_no_image(self, client, auth_headers):
        """测试没有上传图片"""
        request_data = {
            'prompt': 'make it more colorful'
        }

        response = client.post('/api/generate/image-to-image',
                              data=request_data,
                              headers={'Authorization': auth_headers['Authorization']})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Image file is required' in data['error']

    def test_image_to_image_invalid_file_type(self, client, auth_headers):
        """测试上传无效文件类型"""
        test_file_data = b'fake text data'

        data = {
            'image': (test_file_data, 'test.txt', 'text/plain'),
            'prompt': 'make it colorful'
        }

        response = client.post('/api/generate/image-to-image',
                              data=data,
                              headers={'Authorization': auth_headers['Authorization']})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid image format' in data['error']


class TestCreditManagement:
    """测试次数管理"""

    def test_credit_consumption(self, client, auth_headers):
        """测试次数消费"""
        # 获取初始次数
        with client.application.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            initial_credits = user.credits

        with patch('app.services.ai_generator.AIGeneratorService.generate_text_to_image') as mock_generate:
            mock_generate.return_value = {
                'success': True,
                'images': [{'url': 'https://example.com/image1.png'}],
                'generation_time': 2.0,
                'model_used': 'nano-banana',
                'prompt': 'test'
            }

            request_data = {'prompt': 'test prompt'}

            response = client.post('/api/generate/text-to-image',
                                  data=json.dumps(request_data),
                                  headers=auth_headers)

            assert response.status_code == 200
            data = json.loads(response.data)

            # 验证次数减少
            assert data['remaining_credits'] == initial_credits - 1

            # 验证数据库中的次数
            with client.application.app_context():
                user = User.query.filter_by(email='test@example.com').first()
                assert user.credits == initial_credits - 1

    def test_credit_refund_on_failure(self, client, auth_headers):
        """测试生成失败时次数退还"""
        # 获取初始次数
        with client.application.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            initial_credits = user.credits

        with patch('app.services.ai_generator.AIGeneratorService.generate_text_to_image') as mock_generate:
            mock_generate.return_value = {
                'success': False,
                'error': 'Generation failed',
                'generation_time': 0.5
            }

            request_data = {'prompt': 'test prompt'}

            response = client.post('/api/generate/text-to-image',
                                  data=json.dumps(request_data),
                                  headers=auth_headers)

            assert response.status_code == 500

            # 验证次数被退还
            with client.application.app_context():
                user = User.query.filter_by(email='test@example.com').first()
                assert user.credits == initial_credits  # 次数应该不变