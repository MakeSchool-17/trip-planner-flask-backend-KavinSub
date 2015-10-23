import bcrypt as bc

def encrypt(password):
    hashed = bc.hashpw(password.encode("utf-8"), bc.gensalt(12))
    return hashed

def check(password, hashed):
    return bc.hashpw(password.encode("utf-8"), hashed) == hashed

if __name__ == '__main__':
    password = '1!23asdDNA'
    hashed = encrypt(password)
    print("{} -> {} which is type {}".format(password, hashed, type(hashed)))
    print("{}".format(check(password, hashed)))
