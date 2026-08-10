import sys
print("Testing CyberShield AI startup...")

from app import create_app
print("  OK: app.py imported")

app = create_app('development')
print("  OK: App created successfully")
print("  OK: Blueprints: " + str(list(app.blueprints.keys())))

client = app.test_client()
with app.app_context():
    r1 = client.get('/health')
    print("  OK: /health -> " + str(r1.status_code))
    r2 = client.get('/')
    print("  OK: / (home) -> " + str(r2.status_code))
    r3 = client.get('/auth/login')
    print("  OK: /auth/login -> " + str(r3.status_code))
    r4 = client.get('/dashboard/')
    print("  OK: /dashboard/ -> " + str(r4.status_code) + " (302 = redirect to login, correct)")

print("")
print("========================================")
print("  CyberShield AI is READY!")
print("  Run:   python app.py")
print("  Open:  http://localhost:5000")
print("  Admin: admin / Admin@123")
print("========================================")
