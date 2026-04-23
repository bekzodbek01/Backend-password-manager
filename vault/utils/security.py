from django.contrib.auth.hashers import check_password

def verify_master(user, master_password):
    print("USER:", user.username)
    print("HASH:", user.master_password)
    print("INPUT:", master_password)

    return check_password(master_password, user.master_password)