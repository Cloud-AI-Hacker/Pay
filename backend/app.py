from flask import Flask, request, jsonify, send_from_directory
import uuid

app = Flask(__name__)

users = {}
tokens = {}

def auth_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401
        token = auth.split(' ')[1]
        username = tokens.get(token)
        if not username:
            return jsonify({'error': 'Invalid token'}), 401
        request.user = users[username]
        request.username = username
        return f(*args, **kwargs)
    return wrapper

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    if username in users:
        return jsonify({'error': 'user exists'}), 400
    users[username] = {
        'password': password,
        'balance': 0,
        'wallet_address': None,
        'deposits': [],
        'withdrawals': [],
        'payments': []
    }
    return jsonify({'message': 'registered'})

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    user = users.get(username)
    if not user or user['password'] != password:
        return jsonify({'error': 'invalid credentials'}), 401
    token = str(uuid.uuid4())
    tokens[token] = username
    return jsonify({'token': token})

@app.route('/api/v1/auth/logout', methods=['POST'])
@auth_required
def logout():
    token = request.headers.get('Authorization').split(' ')[1]
    tokens.pop(token, None)
    return jsonify({'message': 'logged out'})

@app.route('/api/v1/wallet', methods=['GET'])
@auth_required
def wallet():
    user = request.user
    return jsonify({
        'address': user['wallet_address'],
        'balance': user['balance']
    })

@app.route('/api/v1/wallet/generate-address', methods=['POST'])
@auth_required
def generate_address():
    user = request.user
    if not user['wallet_address']:
        user['wallet_address'] = 'T' + uuid.uuid4().hex[:33]
    return jsonify({'address': user['wallet_address']})

@app.route('/api/v1/deposits', methods=['GET'])
@auth_required
def deposits():
    return jsonify(request.user['deposits'])

@app.route('/api/v1/withdrawals', methods=['POST'])
@auth_required
def create_withdrawal():
    data = request.get_json() or {}
    amount = data.get('amount')
    address = data.get('address')
    if not amount or not address:
        return jsonify({'error': 'amount and address required'}), 400
    if request.user['balance'] < amount:
        return jsonify({'error': 'insufficient balance'}), 400
    withdrawal = {'id': str(uuid.uuid4()), 'amount': amount, 'address': address, 'status': 'pending'}
    request.user['withdrawals'].append(withdrawal)
    request.user['balance'] -= amount
    return jsonify(withdrawal)

@app.route('/api/v1/withdrawals', methods=['GET'])
@auth_required
def get_withdrawals():
    return jsonify(request.user['withdrawals'])

@app.route('/api/v1/payments', methods=['POST'])
@auth_required
def create_payment():
    data = request.get_json() or {}
    amount = data.get('amount')
    if not amount:
        return jsonify({'error': 'amount required'}), 400
    payment = {'id': str(uuid.uuid4()), 'amount': amount, 'address': 'T' + uuid.uuid4().hex[:33], 'status': 'pending'}
    request.user['payments'].append(payment)
    return jsonify(payment)

@app.route('/api/v1/payments', methods=['GET'])
@auth_required
def list_payments():
    return jsonify(request.user['payments'])

@app.route('/api/v1/admin/users', methods=['GET'])
@auth_required
def admin_users():
    # simple check: only user named 'admin' is admin
    if request.username != 'admin':
        return jsonify({'error': 'forbidden'}), 403
    return jsonify({u: {'balance': d['balance'], 'wallet_address': d['wallet_address']} for u, d in users.items()})

@app.route('/')
def index():
    return send_from_directory('../frontend/templates', 'user.html')

@app.route('/admin')
def admin_page():
    return send_from_directory('../frontend/templates', 'admin.html')

if __name__ == '__main__':
    app.run(debug=True)
